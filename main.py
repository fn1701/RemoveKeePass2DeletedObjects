import gc
import pykeepass

import sys
import tkinter as tk
from tkinter import filedialog, simpledialog
from datetime import datetime
import os
import shutil

import base64
import xml.etree.ElementTree as ET
import zipfile

import getpass

from collections import Counter

root = tk.Tk()
root.withdraw()

home_dir = os.path.expanduser("~")

def get_file_name(file_path):
    basename = os.path.basename(file_path)
    name, ext = os.path.splitext(basename)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    bkp_name = f"{name}_backup_{timestamp}{ext}"
    return bkp_name

def remove_deleted_objects(keepass, path):
    print(f"Checking for deleted objects in: {path}")  # Debugging statement
    deleted_objects = keepass.xpath("//DeletedObjects/DeletedObject")

    print(f"Deleted objects found: {len(deleted_objects)}")  # Debugging statement

    if len(deleted_objects) > 0:
        deleted_objects_count = 0
        deletion_times = Counter()

        for element in deleted_objects:
            del_time = keepass.xpath("DeletionTime", tree=element)
            if del_time:
                decoded_time = keepass._decode_time(del_time[0].text)
                deletion_times[decoded_time] += 1
                deleted_objects_count += 1

        print("Deleted objects found:") # Debugging statement
        for time, count in sorted(deletion_times.items()):
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S')}: {count}")

        ok_remove = tk.messagebox.askokcancel(
            "Remove deleted objects?",
            f"Found {deleted_objects_count} deleted objects in {path}. Shall we remove them from the database?",
            parent=root,
        )
        if ok_remove:
            deletion_count = 0
            for element in deleted_objects:
                element.getparent().remove(element)
                deletion_count += 1
            keepass.save()
            print(f"{deletion_count} deleted objects were removed from the KeePass database.")
        else:
            print("Deleted objects were not removed from the KeePass database.")
            return
    else:
        print("No deleted objects found in the KeePass database.")
        return

def run():
    global root
    global home_dir

    # Check for headless mode
    headless = len(sys.argv) > 1
    db_path = sys.argv[1] if headless else None

    if headless:
        print("Running in headless mode...")
        if not os.path.isfile(db_path):
            print(f"Error: Database file '{db_path}' does not exist.")
            return
    else:
        print("Starting KeePass database cleanup...")  # Debugging statement
        db_path = filedialog.askopenfilename(
            title="Select your KeePass Database",
            initialdir=home_dir,
            filetypes=(("KeePass DB Files", "*.kdbx"),),
            parent=root
        )

    if not db_path:
        print("No database selected, exiting.")
        return

    kp = None

    try:
        password = None
        if headless:
            if len(sys.argv) > 2:
                password = sys.argv[2]  # Use the provided password
            else:
                password = getpass.getpass(prompt="Enter KeePass password: ")  # Prompt for password securely
        else:
            password = simpledialog.askstring(
                "Password",
                prompt="Enter your KeePass password:",
                show="*",
                parent=root
            )

        kp = pykeepass.PyKeePass(db_path, password=password)
        gc.collect()
        print("KeePass database loaded.")

    except Exception as e:
        print(f"Error loading KeePass database: {e}")
        return

    finally:
        gc.collect()

    if not kp:
        print("KeePass database not loaded, exiting.")
        return

    try:
        print("Searching for KeeShare Groups...")
        kee_share_groups = kp.xpath("//Group/CustomData/Item[Key='KeeShare/Reference']")

        kee_share_credentials = {}
        db_dir = os.path.dirname(db_path)
        for element in kee_share_groups:
            ks_xml = ET.fromstring(base64.b64decode(kp.xpath("Value", tree=element)[0].text).decode("utf-8"))
            if ks_xml is not None:
                ks_path = os.path.abspath(os.path.join(db_dir, base64.b64decode(ks_xml.find("Path").text).decode("utf-8")))
                ks_pw = base64.b64decode(ks_xml.find("Password").text).decode("utf-8")
                kee_share_credentials[ks_path] = ks_pw
                print(f"Found KeeShare group: {ks_path}")
            try:
               del ks_xml
            except NameError:
                pass

        print("Creating backup of this database and all databases connected via KeeShare.")
        backup_target = os.path.join(os.path.dirname(db_path), "KeePass2DeletedObjects_backup")
        os.makedirs(backup_target, exist_ok=True)
        backup_filepath = os.path.join(backup_target, get_file_name(db_path))
        shutil.copy(db_path, backup_filepath)
        print(f"Backup of {db_path} created at {backup_target}")
        for key, _ in kee_share_credentials.items():
            backup_filepath = os.path.join(backup_target, get_file_name(key))
            shutil.copy(key, backup_filepath)
            print(f"Backup of {key} created at {backup_filepath}")

        print("Searching for deleted objects...")
        remove_deleted_objects(kp, db_path)
        for path, password in kee_share_credentials.items():
            print(f"Opening KeeShare database: {path}")

            if path.endswith(".kdbx.share"):
                process_kdbx_share_file(path, password)
            else:
                # Process regular KeeShare database
                kee_share_kp = pykeepass.PyKeePass(path, password=password)
                remove_deleted_objects(kee_share_kp, path)

    finally:
        try:
            del kp
        except NameError:
            pass
        gc.collect()
        print("Cleanup process completed.")  # Debugging statement

run()
gc.collect()
for var in list(locals().keys()):
    if var not in ("__builtins__", "__file__", "__name__", "__package__", "__doc__"):
        del locals()[var]

def process_kdbx_share_file(path, password):
    # Unzip the .kdbx.share file
    folder_name = os.path.splitext(path)[0]  # Remove .kdbx.share extension
    os.makedirs(folder_name, exist_ok=True)

    with zipfile.ZipFile(path, 'r') as zip_ref:
        zip_ref.extractall(folder_name)

    # Point to container.share.kdbx inside the extracted folder
    container_path = os.path.join(folder_name, "container.share.kdbx")
    print(f"Using container.share.kdbx at: {container_path}")

    # Process the container.share.kdbx file
    kee_share_kp = pykeepass.PyKeePass(container_path, password=password)
    remove_deleted_objects(kee_share_kp, container_path)

    # Re-zip the folder and replace the original .kdbx.share file
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
        for root, _, files in os.walk(folder_name):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_name)
                zip_ref.write(file_path, arcname)

    print(f"Updated .kdbx.share file: {path}")

    # Clean up the extracted folder
    shutil.rmtree(folder_name)