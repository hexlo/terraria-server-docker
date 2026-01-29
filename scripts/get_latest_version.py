#!/usr/bin/env python3
"""
Find the latest available Terraria dedicated server version.

Scrapes the Terraria Fandom wiki to get a base version, then increments
to find the actual latest version available for download.

Assumes that version numbers always start with 1, have 4 numbers, each number is between 0-9 (no 2-digit minor version for example)
and is in the format: 1.M.m.h where { M: major, m: minor, h: hotfix }
"""

import sys
import urllib.request
import urllib.error
import re

DEFAULT_VERSION = '1450'
MAX_CONSECUTIVE_FAILURES = 1


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


def find_highest_version():
    """Find the highest available Terraria version.

    Systematically searches for the highest version by:
    1. Finding the highest major version
    2. Finding the highest minor version within that major
    3. Finding the highest hotfix version within that minor

    Returns:
        String of highest available version found
    """

    base_version = get_base_version()
    if base_version is None:
        # If scraping failed, use the default version
        print(f"Base version from web scraper: could not find anything, using default version {DEFAULT_VERSION}")
        base_version = DEFAULT_VERSION
    else:
        print(f"Base version from web scraper: {base_version}")

    base_int = version_to_int(base_version)
    base_str = str(base_int).zfill(4)  # Ensure 4 digits

    # Parse base version components (assume format: 1Mmh where M=major, m=minor, h=hotfix)
    if len(base_str) < 4:
        print(f"Error: Invalid version format '{base_version}'", file=sys.stderr)
        return base_version

    major = int(base_str[1])
    minor = int(base_str[2])
    hotfix = int(base_str[3])

    print(f"Starting search from base version {base_version} (1.{major}.{minor}.{hotfix})")

    # Step 1: Find highest major version
    print("\n=== Finding highest major version ===")
    highest_major = major
    test_major = major + 1

    while test_major <= 9:  # Major version can only be 0-9
        # Test version with next major, minor=0, hotfix=0
        test_version = int(f"1{test_major}00")
        print(f"Testing major version 1.{test_major}.0.0 ({test_version})...", end=" ", flush=True)

        if is_version_available(str(test_version)):
            print("✓ Available")
            highest_major = test_major
            test_major += 1
        else:
            print("✗ Not available")
            break

    print(f"Highest major version: 1.{highest_major}.x.x")

    # Step 2: Find highest minor version within the highest major
    print("\n=== Finding highest minor version ===")

    # major version hasnt changed. We start at the minor version already found + 1
    if highest_major == major:
        highest_minor = minor
        test_minor = minor + 1

    # major version is higher than the version found. We start the minor at 0 and iterate
    else:
        highest_minor = 0
        test_minor = 0

    while test_minor <= 9:  # Minor version can only be 0-9
        # Test version with highest major, test minor, hotfix=0
        test_version = int(f"1{highest_major}{test_minor}0")
        print(f"Testing minor version 1.{highest_major}.{test_minor}.0 ({test_version})...", end=" ", flush=True)

        if is_version_available(str(test_version)):
            print("✓ Available")
            highest_minor = test_minor
            test_minor += 1
        else:
            print("✗ Not available")
            break

    print(f"Highest minor version: 1.{highest_major}.{highest_minor}.x")

    # Step 3: Find highest hotfix version within the highest major.minor
    print("\n=== Finding highest hotfix version ===")

    # minor version did not change. We start at the minor version already found + 1
    if highest_minor == minor:
        highest_hotfix = hotfix
        test_hotfix = hotfix + 1

    # major version is higher than the version found. We start the minor at 0 and iterate
    else:
        highest_hotfix = 0
        test_hotfix = 0

    while test_hotfix <= 9:  # Hotfix version can only be 0-9
        # Test version with highest major, highest minor, test hotfix
        test_version = int(f"1{highest_major}{highest_minor}{test_hotfix}")
        print(f"Testing hotfix version 1.{highest_major}.{highest_minor}.{test_hotfix} ({test_version})...", end=" ", flush=True)

        if is_version_available(str(test_version)):
            print("✓ Available")
            highest_hotfix = test_hotfix
            test_hotfix += 1
        else:
            print("✗ Not available")
            break

    highest_version = str(int(f"1{highest_major}{highest_minor}{highest_hotfix}"))
    print(f"\nHighest available version found: {highest_version} (1.{highest_major}.{highest_minor}.{highest_hotfix})")

    return highest_version


if __name__ == "__main__":
    latest = find_highest_version()
    print(latest)
