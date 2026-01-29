#!/usr/bin/env python3
"""
Find the latest available Terraria dedicated server version.

Scrapes the Terraria Fandom wiki to get a base version, then increments
to find the actual latest version available for download.
"""

import sys
import urllib.request
import urllib.error
import re

DEFAULT_VERSION = '1450'


def get_base_version():
    """Get the base Terraria version by scraping the Terraria Fandom wiki.

    Returns the version string on success, or None on failure.
    """
    try:
        url = "https://terraria.fandom.com/wiki/Server"
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')

        # Extract download URLs
        pattern = r'https://terraria\.org/api/download/pc-dedicated-server/[^"]*'
        matches = re.findall(pattern, html)

        if not matches:
            print("Error: Could not find Terraria download URL on Fandom wiki", file=sys.stderr)
            return None

        # Get the last (most recent) URL and extract version
        latest_url = matches[-1]
        version = latest_url.split('/terraria-server-')[1].split('.zip')[0]

        if not version:
            print("Error: Could not extract version from URL", file=sys.stderr)
            return None

        return version
    except (urllib.error.URLError, urllib.error.HTTPError, Exception) as e:
        print(f"Error fetching Terraria version: {e}", file=sys.stderr)
        return None


def version_to_int(version_str):
    """Convert version string like '1450' to integer."""
    try:
        return int(version_str)
    except ValueError:
        print(f"Error: Invalid version format '{version_str}'", file=sys.stderr)
        sys.exit(1)


def int_to_version(version_int):
    """Convert integer back to version string."""
    return str(version_int)


def is_version_available(version):
    """Check if a version is available for download."""
    url = f"https://terraria.org/api/download/pc-dedicated-server/terraria-server-{version}.zip"

    try:
        # Try HEAD request first (more efficient)
        req = urllib.request.Request(url, method='HEAD')
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        try:
            urllib.request.urlopen(req, timeout=10)
            return True
        except urllib.error.HTTPError as e:
            # If HEAD is not supported, try GET
            if e.code == 405:
                req = urllib.request.Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
                urllib.request.urlopen(req, timeout=10)
                return True
            return False
    except (urllib.error.URLError, urllib.error.HTTPError, Exception):
        return False


def find_latest_version():
    """Find the latest available Terraria version."""
    # get_base_version() returns either a version string or None
    base_version = get_base_version()
    if base_version is None:
        # If scraping failed, use the default version
        print(f"Base version from web scraper: could not find anything, using default version {DEFAULT_VERSION}")
        base_version = DEFAULT_VERSION
    else:
        print(f"Base version from web scraper: {base_version}")

    # At this point, base_version is guaranteed to be a valid string
    current_version_int = version_to_int(base_version)

    last_available = base_version
    current_version_int += 1

    # Increment and test versions
    max_consecutive_failures = 3  # Stop after 3 consecutive failures
    consecutive_failures = 0

    while consecutive_failures < max_consecutive_failures:
        current_version = int_to_version(current_version_int)

        print(f"Testing version {current_version}...", end=" ", flush=True)

        if is_version_available(current_version):
            print("✓ Available")
            last_available = current_version
            consecutive_failures = 0
        else:
            print("✗ Not available")
            consecutive_failures += 1

        current_version_int += 1

    # Test some larger jumps to ensure no gaps
    print("\nTesting larger version jumps to ensure no gaps...")
    test_jumps = [1460, 1470, 1500]
    for jump_version in test_jumps:
        if jump_version > version_to_int(last_available):
            print(f"Testing version {jump_version}...", end=" ", flush=True)
            if is_version_available(int_to_version(jump_version)):
                print("✓ Available (gap detected, incrementing from here)")
                # If we find a newer version, restart the search from here
                current_version_int = jump_version + 1
                last_available = int_to_version(jump_version)
                consecutive_failures = 0

                while consecutive_failures < max_consecutive_failures:
                    current_version = int_to_version(current_version_int)
                    print(f"Testing version {current_version}...", end=" ", flush=True)

                    if is_version_available(current_version):
                        print("✓ Available")
                        last_available = current_version
                        consecutive_failures = 0
                    else:
                        print("✗ Not available")
                        consecutive_failures += 1

                    current_version_int += 1
            else:
                print("✗ Not available")

    print(f"\nLatest available version: {last_available}")
    return last_available


if __name__ == "__main__":
    latest = find_latest_version()
    print(latest)
