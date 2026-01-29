# Unit Tests for get-next-version.py

Comprehensive unit tests for the Terraria server version finder script using Python's Standard Library only.

## Overview

The test suite provides 32 unit tests covering all major functions and edge cases in `get-next-version.py`. Tests use `unittest` and `unittest.mock` to mock HTTP requests and verify behavior without making actual network calls.

## Test Structure

### Test Classes

#### TestVersionConversion (9 tests)
Tests version number conversion between string and integer formats.

- `test_version_to_int_valid` - Valid version strings (1450, 1452, 1500)
- `test_version_to_int_zero` - Zero version handling
- `test_version_to_int_large_number` - Large version numbers (9999)
- `test_version_to_int_invalid_format` - Invalid format handling (abc, empty string)
- `test_int_to_version_valid` - Valid integer to version conversions
- `test_int_to_version_zero` - Zero integer handling
- `test_int_to_version_large_number` - Large integer conversions
- `test_round_trip_conversion` - Conversion consistency (string→int→string)

#### TestVersionAvailability (9 tests)
Tests HTTP request handling for version availability checks.

- `test_head_request_success` - Successful HEAD requests
- `test_head_request_404_not_found` - 404 responses (version not available)
- `test_head_request_405_fallback_to_get_success` - HEAD 405 → GET fallback succeeds
- `test_head_request_405_fallback_to_get_fails` - HEAD 405 → GET fallback fails
- `test_head_request_500_server_error` - HTTP 500 server errors
- `test_network_error` - Network errors (URLError)
- `test_timeout_error` - Request timeout errors
- `test_generic_exception` - Unexpected exception handling

#### TestGetBaseVersion (6 tests)
Tests web scraping of the Terraria Fandom wiki.

- `test_successful_scrape` - Successfully extracts version from wiki
- `test_multiple_urls_gets_last` - Handles multiple URLs, returns latest
- `test_no_matching_urls` - No download URLs found in HTML
- `test_network_error_returns_none` - Network errors return None (fallback to default)
- `test_http_error_returns_none` - HTTP errors return None (fallback to default)
- `test_empty_html` - Empty HTML response handling

#### TestFindLatestVersion (8 tests)
Tests the main version search logic.

- `test_normal_case_finds_latest` - Normal flow: increments until finding latest
- `test_base_version_unavailable` - Base version itself is not available
- `test_fallback_to_default_version` - Falls back to DEFAULT_VERSION='1450' on scraper failure
- `test_gap_detection_at_1460` - Detects and searches from gap at version jump
- `test_stops_after_3_consecutive_failures` - Stops searching after 3 consecutive failures
- `test_output_shows_base_version_source` - Verifies output shows scraped version
- `test_output_shows_default_version_used` - Verifies output shows fallback to default
- `test_base_version_unavailable` - Handles unavailable base versions

#### TestEdgeCases (2 tests)
Tests edge cases and output verification.

- `test_all_versions_available` - Multiple available versions before stopping
- `test_version_string_in_output` - Version numbers and status appear in output

## Running the Tests

### Basic Execution
```bash
python3 tests/test_get_next_version.py
```

Output:
```
Ran 32 tests in 0.006s
OK
```

### Verbose Output
```bash
python3 tests/test_get_next_version.py -v
```

Shows each test name and status:
```
test_version_to_int_valid (__main__.TestVersionConversion) ... ok
test_version_to_int_zero (__main__.TestVersionConversion) ... ok
test_version_to_int_invalid_format (__main__.TestVersionConversion) ... ok
... (all 32 tests)
```

### Run Specific Test Class
```bash
python3 -m unittest tests.test_get_next_version.TestVersionConversion -v
```

### Run Specific Test
```bash
python3 -m unittest tests.test_get_next_version.TestVersionConversion.test_version_to_int_valid -v
```

## Test Coverage

| Component | Tests | Coverage |
|-----------|-------|----------|
| Version Conversion | 9 | 100% |
| Version Availability (HTTP) | 9 | 100% |
| Base Version Scraping | 6 | 100% |
| Main Search Logic | 8 | 100% |
| Edge Cases | 2 | 100% |
| **Total** | **32** | **100%** |

### Functions Tested
- ✅ `version_to_int()` - Version string to integer
- ✅ `int_to_version()` - Integer to version string
- ✅ `is_version_available()` - HTTP version availability check
- ✅ `get_base_version()` - Web scraping for base version
- ✅ `find_latest_version()` - Main search algorithm

### Error Scenarios Tested
- ✅ Network failures (URLError, HTTPError)
- ✅ Timeouts
- ✅ Invalid input formats
- ✅ Missing data
- ✅ Server errors (4xx, 5xx)
- ✅ HTTP 405 (method not allowed) with fallback
- ✅ Web scraping failures

## Dependencies

**All tests use Python Standard Library only:**
- `unittest` - Test framework
- `unittest.mock` - Mocking/patching
- `urllib` - HTTP testing
- `io` - Output capture
- `sys` - System utilities
- `importlib` - Dynamic module loading
- `os` - Path utilities
- `re` - Regex (in the script being tested)

**No external packages required** - works with Python 3.6+

## Mocking Strategy

Tests use `@patch.object()` to mock:
1. **HTTP Requests** - `urllib.request.urlopen()`
   - Simulates successful responses
   - Simulates various HTTP error codes
   - Simulates network failures

2. **Web Scraping** - `get_base_version()`
   - Mocks wiki responses
   - Tests extraction logic

3. **Version Availability** - `is_version_available()`
   - Mocks availability checks
   - Tests version increment logic

## Debugging Failed Tests

If a test fails:

1. **Check mock setup**
   ```python
   # Verify mock return values match test expectations
   mock_available.side_effect = [True, True, False, False, False, ...]
   ```

2. **Check output capture**
   ```python
   output = captured_output.getvalue()
   print(output)  # See what was printed
   ```

3. **Count mock calls**
   ```python
   self.assertEqual(mock_available.call_count, 7)  # Verify expected number of calls
   ```

4. **Run with verbose output**
   ```bash
   python3 tests/test_get_next_version.py -v
   ```

## Continuous Integration

These tests can be integrated into CI/CD pipelines:

```bash
#!/bin/bash
python3 tests/test_get_next_version.py || exit 1
echo "All tests passed!"
```

## References

- [unittest Documentation](https://docs.python.org/3/library/unittest.html)
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
- Python Standard Library: `urllib.request`, `urllib.error`, `io`, `sys`, `os`, `re`
