import urllib.request
import urllib.error
import json
import os
import sys
import shutil

import get_latest_filename


def download_server(version, dir_path=""):
    if not isinstance(version, str):
        raise TypeError("Version must be a string")
    
    match version:
        case "latest":
            print("Getting latest filename...")
            filename = get_latest_filename.get_latest_filename()
        
        case _:
            print("Using Custom Version")
            print("Formatting version...")
            formated_version = version.replace(".", "")
            assert formated_version.isdigit(), "Version must be a number"
            formated_version = formated_version.zfill(4)
            assert len(formated_version) == 4, "Version must be 4 digits"
            print("Formated version:", formated_version)
            filename = f"terraria-server-{formated_version}.zip"
    
    url = f"https://terraria.org/api/download/pc-dedicated-server/{filename}"

    if not dir_path:
        dir_path = os.getcwd()

    output_path = os.path.join(dir_path, "terraria-server.zip")
    print(f"Downloading {url} to {output_path}...")

    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    with urllib.request.urlopen(req) as response, open(output_path, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download_server.py <version> [output directory]")
        sys.exit(1)
    
    output_dir = sys.argv[2] if len(sys.argv) > 2 else ""
    download_server(sys.argv[1], output_dir)
