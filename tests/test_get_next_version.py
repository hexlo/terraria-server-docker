#!/usr/bin/env python3
"""
Unit tests for get-next-version.py using Python Standard Library only.
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import io
import urllib.error
from urllib.error import HTTPError, URLError
import os

# Add scripts directory to path to import the script
script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts')
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Use importlib to load the module
import importlib.util
module_path = os.path.join(script_dir, "get_latest_version.py")
spec = importlib.util.spec_from_file_location("get_latest_version", module_path)
get_latest_version = importlib.util.module_from_spec(spec)
spec.loader.exec_module(get_latest_version)

# Alias for backward compatibility with test code
get_next_version = get_latest_version


class TestVersionConversion(unittest.TestCase):
    """Test version string to integer conversions."""

    def test_version_to_int_valid(self):
        """Test valid version string to integer conversion."""
        self.assertEqual(get_next_version.version_to_int('1450'), 1450)
        self.assertEqual(get_next_version.version_to_int('1452'), 1452)
        self.assertEqual(get_next_version.version_to_int('1500'), 1500)

    def test_version_to_int_zero(self):
        """Test zero version."""
        self.assertEqual(get_next_version.version_to_int('0'), 0)

    def test_version_to_int_large_number(self):
        """Test large version number."""
        self.assertEqual(get_next_version.version_to_int('9999'), 9999)

    def test_version_to_int_invalid_format(self):
        """Test invalid version format should exit."""
        with self.assertRaises(SystemExit):
            get_next_version.version_to_int('abc')

    def test_version_to_int_empty_string(self):
        """Test empty string version."""
        with self.assertRaises(SystemExit):
            get_next_version.version_to_int('')

    def test_int_to_version_valid(self):
        """Test valid integer to version string conversion."""
        self.assertEqual(get_next_version.int_to_version(1450), '1450')
        self.assertEqual(get_next_version.int_to_version(1452), '1452')
        self.assertEqual(get_next_version.int_to_version(1500), '1500')

    def test_int_to_version_zero(self):
        """Test zero integer to version."""
        self.assertEqual(get_next_version.int_to_version(0), '0')

    def test_int_to_version_large_number(self):
        """Test large integer to version."""
        self.assertEqual(get_next_version.int_to_version(9999), '9999')

    def test_round_trip_conversion(self):
        """Test converting back and forth preserves value."""
        original = '1450'
        as_int = get_next_version.version_to_int(original)
        back_to_string = get_next_version.int_to_version(as_int)
        self.assertEqual(original, back_to_string)


class TestVersionAvailability(unittest.TestCase):
    """Test is_version_available function with mocked HTTP requests."""

    @patch('urllib.request.urlopen')
    def test_head_request_success(self, mock_urlopen):
        """Test successful HEAD request."""
        mock_urlopen.return_value = MagicMock()
        result = get_next_version.is_version_available('1450')
        self.assertTrue(result)
        mock_urlopen.assert_called_once()

    @patch('urllib.request.urlopen')
    def test_head_request_404_not_found(self, mock_urlopen):
        """Test HEAD request returns 404 (version not available)."""
        mock_urlopen.side_effect = HTTPError(
            url='http://example.com', code=404, msg='Not Found',
            hdrs={}, fp=None
        )
        result = get_next_version.is_version_available('9999')
        self.assertFalse(result)

    @patch('urllib.request.urlopen')
    def test_head_request_405_fallback_to_get_success(self, mock_urlopen):
        """Test HEAD returns 405, fallback to GET succeeds."""
        # First call (HEAD) raises 405, second call (GET) succeeds
        mock_urlopen.side_effect = [
            HTTPError(url='http://example.com', code=405, msg='Method Not Allowed',
                     hdrs={}, fp=None),
            MagicMock()  # GET succeeds
        ]
        result = get_next_version.is_version_available('1450')
        self.assertTrue(result)
        self.assertEqual(mock_urlopen.call_count, 2)

    @patch('urllib.request.urlopen')
    def test_head_request_405_fallback_to_get_fails(self, mock_urlopen):
        """Test HEAD returns 405, fallback to GET fails."""
        mock_urlopen.side_effect = [
            HTTPError(url='http://example.com', code=405, msg='Method Not Allowed',
                     hdrs={}, fp=None),
            HTTPError(url='http://example.com', code=404, msg='Not Found',
                     hdrs={}, fp=None)
        ]
        result = get_next_version.is_version_available('9999')
        self.assertFalse(result)

    @patch('urllib.request.urlopen')
    def test_head_request_500_server_error(self, mock_urlopen):
        """Test HEAD request returns 500 error."""
        mock_urlopen.side_effect = HTTPError(
            url='http://example.com', code=500, msg='Server Error',
            hdrs={}, fp=None
        )
        result = get_next_version.is_version_available('1450')
        self.assertFalse(result)

    @patch('urllib.request.urlopen')
    def test_network_error(self, mock_urlopen):
        """Test network error (URLError)."""
        mock_urlopen.side_effect = URLError('Connection refused')
        result = get_next_version.is_version_available('1450')
        self.assertFalse(result)

    @patch('urllib.request.urlopen')
    def test_timeout_error(self, mock_urlopen):
        """Test timeout error."""
        mock_urlopen.side_effect = TimeoutError('Request timeout')
        result = get_next_version.is_version_available('1450')
        self.assertFalse(result)

    @patch('urllib.request.urlopen')
    def test_generic_exception(self, mock_urlopen):
        """Test generic exception handling."""
        mock_urlopen.side_effect = Exception('Unexpected error')
        result = get_next_version.is_version_available('1450')
        self.assertFalse(result)


class TestGetBaseVersion(unittest.TestCase):
    """Test get_base_version function with mocked HTTP requests."""

    @patch('urllib.request.urlopen')
    def test_successful_scrape(self, mock_urlopen):
        """Test successfully scraping base version from wiki."""
        html_content = '''
        <html>
            <a href="https://terraria.org/api/download/pc-dedicated-server/terraria-server-1450.zip">Download</a>
        </html>
        '''
        mock_response = MagicMock()
        mock_response.read.return_value = html_content.encode('utf-8')
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        mock_urlopen.return_value = mock_response

        result = get_next_version.get_base_version()
        self.assertEqual(result, '1450')

    @patch('urllib.request.urlopen')
    def test_multiple_urls_gets_last(self, mock_urlopen):
        """Test that when multiple URLs exist, we get the last one."""
        html_content = '''
        <html>
            <a href="https://terraria.org/api/download/pc-dedicated-server/terraria-server-1450.zip">Old</a>
            <a href="https://terraria.org/api/download/pc-dedicated-server/terraria-server-1451.zip">Newer</a>
            <a href="https://terraria.org/api/download/pc-dedicated-server/terraria-server-1452.zip">Latest</a>
        </html>
        '''
        mock_response = MagicMock()
        mock_response.read.return_value = html_content.encode('utf-8')
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        mock_urlopen.return_value = mock_response

        result = get_next_version.get_base_version()
        self.assertEqual(result, '1452')

    @patch('urllib.request.urlopen')
    def test_no_matching_urls(self, mock_urlopen):
        """Test when HTML has no matching download URLs."""
        html_content = '<html><body>No downloads here</body></html>'
        mock_response = MagicMock()
        mock_response.read.return_value = html_content.encode('utf-8')
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        mock_urlopen.return_value = mock_response

        result = get_next_version.get_base_version()
        self.assertIsNone(result)

    @patch('urllib.request.urlopen')
    def test_network_error_returns_none(self, mock_urlopen):
        """Test that network error returns None."""
        mock_urlopen.side_effect = URLError('Connection failed')

        result = get_next_version.get_base_version()
        self.assertIsNone(result)

    @patch('urllib.request.urlopen')
    def test_http_error_returns_none(self, mock_urlopen):
        """Test that HTTP error returns None."""
        mock_urlopen.side_effect = HTTPError(
            url='http://example.com', code=404, msg='Not Found',
            hdrs={}, fp=None
        )

        result = get_next_version.get_base_version()
        self.assertIsNone(result)

    @patch('urllib.request.urlopen')
    def test_empty_html(self, mock_urlopen):
        """Test with empty HTML response."""
        mock_response = MagicMock()
        mock_response.read.return_value = b''
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        mock_urlopen.return_value = mock_response

        result = get_next_version.get_base_version()
        self.assertIsNone(result)


class TestFindLatestVersion(unittest.TestCase):
    """Test find_latest_version function (main logic)."""

    def setUp(self):
        """Set up patches for this test class."""
        pass

    @patch.object(get_next_version, 'get_base_version')
    @patch.object(get_next_version, 'is_version_available')
    def test_normal_case_finds_latest(self, mock_available, mock_base):
        """Test normal case: finds latest version by incrementing."""
        mock_base.return_value = '1450'
        # Simulate: 1451 available, 1452 available, 1453+ not available
        # Also need to provide values for the larger jumps (1460, 1470, 1500)
        mock_available.side_effect = [True, True, False, False, False, False, False, False]

        # Capture stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output

        result = get_next_version.find_latest_version()

        sys.stdout = sys.__stdout__
        self.assertEqual(result, '1452')

    @patch.object(get_next_version, 'get_base_version')
    @patch.object(get_next_version, 'is_version_available')
    def test_base_version_unavailable(self, mock_available, mock_base):
        """Test when base version itself is not available."""
        mock_base.return_value = '1450'
        # Simulate: base version not available, so search from there
        mock_available.side_effect = [False, False, False, False, False, False]

        captured_output = io.StringIO()
        sys.stdout = captured_output

        result = get_next_version.find_latest_version()

        sys.stdout = sys.__stdout__
        self.assertEqual(result, '1450')

    @patch.object(get_next_version, 'get_base_version')
    @patch.object(get_next_version, 'is_version_available')
    def test_fallback_to_default_version(self, mock_available, mock_base):
        """Test fallback to DEFAULT_VERSION when scraper fails."""
        mock_base.return_value = None
        # When base version is None, should use DEFAULT_VERSION ('1450')
        # Then find next available versions
        mock_available.side_effect = [True, True, False, False, False, False, False, False]

        captured_output = io.StringIO()
        sys.stdout = captured_output

        result = get_next_version.find_latest_version()

        sys.stdout = sys.__stdout__
        self.assertEqual(result, '1452')

    @patch.object(get_next_version, 'get_base_version')
    @patch.object(get_next_version, 'is_version_available')
    def test_gap_detection_at_1460(self, mock_available, mock_base):
        """Test gap detection: finds unavailable, then 1460 is available."""
        mock_base.return_value = '1450'
        # 1451, 1452 available, then 1453-1455 not available
        # Then jump to 1460, which IS available, continues searching
        # Then 1470, 1500 jumps (not available since we already found newer versions)
        mock_available.side_effect = [
            True, True,           # 1451, 1452 available
            False, False, False,  # 1453-1455 not available
            True,                 # 1460 available (gap detected, restart search)
            True, True,           # 1461, 1462 available
            False, False, False,  # 1463-1465 not available
            False, False          # 1470, 1500 not available (or skipped)
        ]

        captured_output = io.StringIO()
        sys.stdout = captured_output

        result = get_next_version.find_latest_version()

        sys.stdout = sys.__stdout__
        self.assertEqual(result, '1462')

    @patch.object(get_next_version, 'get_base_version')
    @patch.object(get_next_version, 'is_version_available')
    def test_stops_after_3_consecutive_failures(self, mock_available, mock_base):
        """Test that search stops after 3 consecutive version failures."""
        mock_base.return_value = '1450'
        # 1451 available, then 3+ failures should stop
        # Also need to provide values for the larger jumps (1460, 1470, 1500)
        mock_available.side_effect = [True, False, False, False, False, False, False]

        captured_output = io.StringIO()
        sys.stdout = captured_output

        result = get_next_version.find_latest_version()

        sys.stdout = sys.__stdout__
        # Should stop after 3 failures, so last_available stays at 1451
        self.assertEqual(result, '1451')
        # is_version_available is called:
        # - 1 for 1451 (available)
        # - 3 for 1452-1454 (failures to stop loop)
        # - 3 for larger jumps 1460, 1470, 1500
        # = 7 total calls
        self.assertEqual(mock_available.call_count, 7)

    @patch.object(get_next_version, 'get_base_version')
    @patch.object(get_next_version, 'is_version_available')
    def test_output_shows_base_version_source(self, mock_available, mock_base):
        """Test that output indicates whether version came from scraper or default."""
        mock_base.return_value = '1450'
        mock_available.side_effect = [False, False, False, False, False, False]

        captured_output = io.StringIO()
        sys.stdout = captured_output

        get_next_version.find_latest_version()

        output = captured_output.getvalue()
        sys.stdout = sys.__stdout__
        self.assertIn('Base version from web scraper: 1450', output)

    @patch.object(get_next_version, 'get_base_version')
    @patch.object(get_next_version, 'is_version_available')
    def test_output_shows_default_version_used(self, mock_available, mock_base):
        """Test that output shows when default version is used."""
        mock_base.return_value = None
        mock_available.side_effect = [False, False, False, False, False, False]

        captured_output = io.StringIO()
        sys.stdout = captured_output

        get_next_version.find_latest_version()

        output = captured_output.getvalue()
        sys.stdout = sys.__stdout__
        self.assertIn('could not find anything', output)
        self.assertIn(get_next_version.DEFAULT_VERSION, output)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    @patch.object(get_next_version, 'get_base_version')
    @patch.object(get_next_version, 'is_version_available')
    def test_all_versions_available(self, mock_available, mock_base):
        """Test when many versions are available (should stop after max consecutive failures = 0)."""
        mock_base.return_value = '1450'
        # All versions available, but we stop when we find 3 consecutive failures
        # Also need to provide values for the larger jumps (1460, 1470, 1500)
        mock_available.side_effect = [True, True, True, True, True, False, False, False, False, False, False]

        captured_output = io.StringIO()
        sys.stdout = captured_output

        result = get_next_version.find_latest_version()

        sys.stdout = sys.__stdout__
        self.assertEqual(result, '1455')

    @patch.object(get_next_version, 'get_base_version')
    @patch.object(get_next_version, 'is_version_available')
    def test_version_string_in_output(self, mock_available, mock_base):
        """Test that version numbers are printed during search."""
        mock_base.return_value = '1450'
        mock_available.side_effect = [True, False, False, False, False, False, False]

        captured_output = io.StringIO()
        sys.stdout = captured_output

        get_next_version.find_latest_version()

        output = captured_output.getvalue()
        sys.stdout = sys.__stdout__
        self.assertIn('1451', output)
        self.assertIn('Available', output)


if __name__ == '__main__':
    unittest.main()
