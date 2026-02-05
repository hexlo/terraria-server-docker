#!/usr/bin/env python3
import os
import sys
import shutil
import zipfile

def prune(working_dir="."):
    zip_filename = os.path.join(working_dir, "terraria-server.zip")
    extracted_folder_path = None
    should_remove_zip = False
    
    if os.path.exists(zip_filename):
        print(f"Unzipping {zip_filename}...")
        try:
            with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
                if not zip_ref.namelist():
                    print("Error: Zip file is empty.")
                    sys.exit(1)
                extracted_folder_name = zip_ref.namelist()[0].split('/')[0]
                zip_ref.extractall(working_dir)
                extracted_folder_path = os.path.join(working_dir, extracted_folder_name)
                should_remove_zip = True
        except zipfile.BadZipFile:
            print("Error: Bad zip file.")
            sys.exit(1)
    else:
        print(f"{zip_filename} not found. Checking for extracted folder...")
        if os.path.exists(working_dir):
            for item in os.listdir(working_dir):
                item_path = os.path.join(working_dir, item)
                if os.path.isdir(item_path) and os.path.isdir(os.path.join(item_path, "Linux")):
                    extracted_folder_path = item_path
                    break

    if not extracted_folder_path or not os.path.isdir(extracted_folder_path):
        print(f"Error: Zip file not found and extracted folder not detected.")
        sys.exit(1)

    linux_folder = os.path.join(extracted_folder_path, "Linux")
    if not os.path.isdir(linux_folder):
        print(f"Error: Linux folder not found at '{linux_folder}'.")
        sys.exit(1)

    print(f"Moving files from {linux_folder} to {working_dir}...")
    for item in os.listdir(linux_folder):
        src = os.path.join(linux_folder, item)
        dst = os.path.join(working_dir, item)
        
        # Remove destination if it exists to ensure overwrite
        if os.path.exists(dst):
            if os.path.isdir(dst):
                shutil.rmtree(dst)
            else:
                os.remove(dst)
        
        shutil.move(src, dst)

    print("Cleaning up...")
    # Remove the version folder (which now contains Mac, Windows, and empty Linux)
    shutil.rmtree(extracted_folder_path)
    
    # Remove the zip file
    if should_remove_zip:
        os.remove(zip_filename)
    print("Pruning complete.")

if __name__ == "__main__":
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    prune(target_dir)