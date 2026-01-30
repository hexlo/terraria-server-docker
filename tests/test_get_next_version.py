#!/usr/bin/env python3
"""
Unit tests for get_highest_version.py.
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


class TestFindHighestVersion(unittest.TestCase):
    """Test find_highest_version function (main logic)."""

    @patch.object(get_next_version, 'get_base_version')
    @patch.object(get_next_version, 'is_version_available')
    def test_finds_higher_major_version(self, mock_available, mock_base):
        """Test finding a higher major version (e.g., 1.4.x.x -> 1.5.x.x)."""
        mock_base.return_value = '1452'  # 1.4.5.2
        # Test major versions: 1.5.0.0 (1500) available, 1.6.0.0 (1600) not available
        # Then test minor versions within 1.5.x.x: stops on first unavailable
        # Then test hotfix versions within highest minor: stops on first unavailable
        mock_available.side_effect = [
            True, False,  # Major: 1500 available, 1600 not (breaks)
            True, True, True, False,  # Minor: 1500, 1510, 1520 available, 1530 not (breaks)
            True, True, True, False   # Hotfix: 1520, 1521, 1522 available, 1523 not (breaks)
        ]

        captured_output = io.StringIO()
        sys.stdout = captured_output

        result = get_next_version.find_highest_version()

        sys.stdout = sys.__stdout__
        self.assertEqual(result, '1522')  # 1.5.2.2

    @patch.object(get_next_version, 'get_base_version')
    @patch.object(get_next_version, 'is_version_available')
    def test_stays_in_same_major_version(self, mock_available, mock_base):
        """Test when major version hasn't changed, searches minor versions."""
        mock_base.return_value = '1452'  # 1.4.5.2
        # Test major versions: 1.5.0.0 (1500) not available
        # Since major didn't change, start testing minor from 1.4.6.0
        # Then test hotfix within highest minor found
        mock_available.side_effect = [
            False,  # Major: 1500 not available
            True, False,  # Minor: 1.4.6.0 available, 1.4.7.0 not
            True, True, False, False, False, False, False, False, False, False  # Hotfix: 1.4.6.0-9 (0,1 available)
        ]

        captured_output = io.StringIO()
        sys.stdout = captured_output

        result = get_next_version.find_highest_version()

        sys.stdout = sys.__stdout__
        self.assertEqual(result, '1461')  # 1.4.6.1

    @patch.object(get_next_version, 'get_base_version')
    @patch.object(get_next_version, 'is_version_available')
    def test_only_hotfix_increments(self, mock_available, mock_base):
        """Test when only hotfix version increments."""
        mock_base.return_value = '1452'  # 1.4.5.2
        # Major 1.5.0.0 not available
        # Minor 1.4.6.0 not available
        # Only hotfix increments: 1.4.5.3, 1.4.5.4 available
        mock_available.side_effect = [
            False,  # Major: 1500 not available
            False,  # Minor: 1460 not available
            True, True, True, False, False, False, False, False, False, False  # Hotfix: start from 1453 (3,4,5 available)
        ]

        captured_output = io.StringIO()
        sys.stdout = captured_output

        result = get_next_version.find_highest_version()

        sys.stdout = sys.__stdout__
        self.assertEqual(result, '1455')  # 1.4.5.5

    @patch.object(get_next_version, 'get_base_version')
    @patch.object(get_next_version, 'is_version_available')
    def test_no_higher_version_available(self, mock_available, mock_base):
        """Test when no higher version is available."""
        mock_base.return_value = '1452'  # 1.4.5.2
        # All higher versions are not available
        mock_available.side_effect = [
            False,  # Major: 1500 not available
            False,  # Minor: 1460 not available
            False, False, False, False, False, False, False  # Hotfix: all not available
        ]

        captured_output = io.StringIO()
        sys.stdout = captured_output

        result = get_next_version.find_highest_version()

        sys.stdout = sys.__stdout__
        self.assertEqual(result, '1452')  # Stays at base version

    @patch.object(get_next_version, 'get_base_version')
    @patch.object(get_next_version, 'is_version_available')
    def test_fallback_to_default_version(self, mock_available, mock_base):
        """Test fallback to DEFAULT_VERSION when scraper fails."""
        mock_base.return_value = None
        # When base version is None, should use DEFAULT_VERSION ('1450')
        # Then search for higher versions
        mock_available.side_effect = [
            True, False,  # Major: 1500 available, 1600 not
            True, False, False, False, False, False, False, False, False, False,  # Minor: 1500 available, rest not
            True, False, False, False, False, False, False, False, False, False   # Hotfix: 1500 available, rest not
        ]

        captured_output = io.StringIO()
        sys.stdout = captured_output

        result = get_next_version.find_highest_version()

        sys.stdout = sys.__stdout__
        self.assertEqual(result, '1500')  # 1.5.0.0

    @patch.object(get_next_version, 'get_base_version')
    @patch.object(get_next_version, 'is_version_available')
    def test_output_shows_base_version_source(self, mock_available, mock_base):
        """Test that output indicates version came from scraper."""
        mock_base.return_value = '1452'
        mock_available.side_effect = [False] * 20  # All not available

        captured_output = io.StringIO()
        sys.stdout = captured_output

        get_next_version.find_highest_version()

        output = captured_output.getvalue()
        sys.stdout = sys.__stdout__
        self.assertIn('Base version from web scraper: 1452', output)

    @patch.object(get_next_version, 'get_base_version')
    @patch.object(get_next_version, 'is_version_available')
    def test_output_shows_default_version_used(self, mock_available, mock_base):
        """Test that output shows when default version is used."""
        mock_base.return_value = None
        mock_available.side_effect = [False] * 20

        captured_output = io.StringIO()
        sys.stdout = captured_output

        get_next_version.find_highest_version()

        output = captured_output.getvalue()
        sys.stdout = sys.__stdout__
        self.assertIn('could not find anything', output)
        self.assertIn(get_next_version.DEFAULT_VERSION, output)

    @patch.object(get_next_version, 'get_base_version')
    @patch.object(get_next_version, 'is_version_available')
    def test_searches_all_major_versions(self, mock_available, mock_base):
        """Test that it searches through multiple major versions."""
        mock_base.return_value = '1452'  # 1.4.5.2
        # Major: 1.5, 1.6, 1.7 all available, 1.8 not (breaks)
        # Minor: within 1.7, 0-3 available, 4 not (breaks)
        # Hotfix: within 1.7.3, 0-5 available, 6 not (breaks)
        mock_available.side_effect = [
            True, True, True, False,  # Major: 1500, 1600, 1700 available, 1800 not (breaks)
            True, True, True, True, False,  # Minor: 1700, 1710, 1720, 1730 available, 1740 not (breaks)
            True, True, True, True, True, True, False  # Hotfix: 1730-1735 available, 1736 not (breaks)
        ]

        captured_output = io.StringIO()
        sys.stdout = captured_output

        result = get_next_version.find_highest_version()

        sys.stdout = sys.__stdout__
        self.assertEqual(result, '1735')  # 1.7.3.5


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    @patch.object(get_next_version, 'get_base_version')
    @patch.object(get_next_version, 'is_version_available')
    def test_max_major_version_1998(self, mock_available, mock_base):
        """Test behavior at maximum major version 1.9.9.8."""
        mock_base.return_value = '1998'  # 1.9.9.8
        # Major search: test_major would be 10, but loop condition is <= 9, so doesn't execute
        # Minor search: test_minor would be 10, but loop condition is <= 9, so doesn't execute
        # Hotfix search: test_hotfix starts at 9
        mock_available.side_effect = [
            # No calls for major or minor (loops don't execute)
            True, False  # Hotfix: 1999 available, then break on next check
        ]

        captured_output = io.StringIO()
        sys.stdout = captured_output

        result = get_next_version.find_highest_version()

        sys.stdout = sys.__stdout__
        self.assertEqual(result, '1999')  # 1.9.9.9

    @patch.object(get_next_version, 'get_base_version')
    @patch.object(get_next_version, 'is_version_available')
    def test_version_string_in_output(self, mock_available, mock_base):
        """Test that version numbers are printed during search."""
        mock_base.return_value = '1452'
        mock_available.side_effect = [False] * 20

        captured_output = io.StringIO()
        sys.stdout = captured_output

        get_next_version.find_highest_version()

        output = captured_output.getvalue()
        sys.stdout = sys.__stdout__
        self.assertIn('Finding highest major version', output)
        self.assertIn('Finding highest minor version', output)
        self.assertIn('Finding highest hotfix version', output)


if __name__ == '__main__':
    unittest.main()
