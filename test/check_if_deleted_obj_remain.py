import os
import subprocess
import zipfile
import shutil
import sys
from collections import Counter
from datetime import datetime
import base64
import xml.etree.ElementTree as ET

def get_file_name(file_path):
    basename = os.path.basename(file_path)
    name, ext = os.path.splitext(basename)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    bkp_name = f"{name}_backup_{timestamp}{ext}"
    return bkp_name

def remove_deleted_objects(keepass, path):
    print(f"Checking for deleted objects in: {path}")
    deleted_objects = keepass.xpath("//DeletedObjects/DeletedObject")

    print(f"Deleted objects found: {len(deleted_objects)}")

    if len(deleted_objects) > 0:
        deletion_count = 0
        for element in deleted_objects:
            element.getparent().remove(element)
            deletion_count += 1
        keepass.save()
        print(f"{deletion_count} deleted objects were removed from the KeePass database.")
    else:
        print("No deleted objects found in the KeePass database.")

def process_kdbx_share_file(path, password):
    folder_name = os.path.splitext(path)[0]
    os.makedirs(folder_name, exist_ok=True)

    with zipfile.ZipFile(path, 'r') as zip_ref:
        zip_ref.extractall(folder_name)

    container_path = os.path.join(folder_name, "container.share.kdbx")
    print(f"Using container.share.kdbx at: {container_path}")

    from pykeepass import PyKeePass
    kee_share_kp = PyKeePass(container_path, password=password)
    remove_deleted_objects(kee_share_kp, container_path)

    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
        for root, _, files in os.walk(folder_name):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_name)
                zip_ref.write(file_path, arcname)

    print(f"Updated .kdbx.share file: {path}")
    shutil.rmtree(folder_name)

def verify_deleted_objects_removal(keepass, file_path):
    deleted_objects = keepass.xpath("//DeletedObjects/DeletedObject")
    if len(deleted_objects) == 0:
        print("Verification successful: No deleted objects remain in the database.")
    else:
        print(f"Verification failed: {len(deleted_objects)} deleted objects still exist.")
        sys.exit(1)

def read_passwords(file_path):
    """Read filenames and passwords from a text file where they are separated by spaces."""
    passwords = {}
    try:
        with open(file_path, 'r') as f:
            for line in f:
                parts = line.strip().split(maxsplit=1)
                if len(parts) == 2:
                    filename, password = parts
                    passwords[filename.strip()] = password.strip()
    except FileNotFoundError:
        print(f"Error: Password file {file_path} not found.")
        sys.exit(1)
    return passwords

def export_kdbx_to_xml(file_path, password):
    file_name = os.path.basename(file_path)

    if file_name.endswith(".kdbx"):
        try:
            from pykeepass import PyKeePass
            kp = PyKeePass(file_path, password=password)
            verify_deleted_objects_removal(kp, file_path)
        except Exception as e:
            print(f"Failed to verify {file_name}: {e}")
            sys.exit(1)

    elif file_name.endswith(".kdbx.share"):
        try:
            if not password:
                print(f"Password not provided for {file_name}, skipping.")
                return

            process_kdbx_share_file(file_path, password)
            print(f"Processed {file_name} successfully.")
        except Exception as e:
            print(f"Failed to process {file_name}: {e}")

    try:
        from pykeepass import PyKeePass
        if not password:
            print(f"Password not provided for verification of {file_name}, skipping.")
            return

        kp = PyKeePass(file_path, password=password)
        verify_deleted_objects_removal(kp, file_path)
    except Exception as e:
        print(f"Failed to verify {file_name}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python export_kdbx_to_xml.py <file_path> <password>")
        sys.exit(1)

    file_path = sys.argv[1]
    password = sys.argv[2]

    if not os.path.isfile(file_path):
        print(f"Error: {file_path} is not a valid file.")
        sys.exit(1)

    export_kdbx_to_xml(file_path, password)