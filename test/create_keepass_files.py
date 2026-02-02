import pykeepass
import os
from random import randint, choice
import string
import xml.etree.ElementTree as ET

def create_random_entry(kp, group, num_entries):
    for _ in range(num_entries):
        title = ''.join(choice(string.ascii_letters) for _ in range(10))
        username = ''.join(choice(string.ascii_letters) for _ in range(8))
        password = ''.join(choice(string.ascii_letters + string.digits) for _ in range(12))
        url = f"https://example{randint(1, 100)}.com"
        notes = ''.join(choice(string.ascii_letters + string.digits) for _ in range(50))
        kp.add_entry(group, title=title, username=username, password=password, url=url, notes=notes)

def add_custom_data_to_group(kp, group, key, value):
    # Locate the group in the XML tree
    group_element = kp._find_group(group.uuid)
    custom_data = group_element.find("CustomData")

    # Create CustomData section if it doesn't exist
    if custom_data is None:
        custom_data = ET.SubElement(group_element, "CustomData")

    # Add the custom data item
    item = ET.SubElement(custom_data, "Item")
    key_element = ET.SubElement(item, "Key")
    key_element.text = key
    value_element = ET.SubElement(item, "Value")
    value_element.text = value

def create_keepass_files():
    base_dir = "/tmp/TestFiles"
    os.makedirs(base_dir, exist_ok=True)

    files = [
        ("TestFile0.kdbx", "verySecurePassword0"),
        ("TestFile1.kdbx", "verySecurePassword1")
    ]

    for file_name, password in files:
        file_path = os.path.join(base_dir, file_name)
        kp = pykeepass.create_database(file_path, password=password)

        # Add groups and entries to TestFile0
        if file_name == "TestFile0.kdbx":
            group0 = kp.add_group(kp.root_group, "TestRelativeKdbx")
            group1 = kp.add_group(kp.root_group, "TestAbsoluteKdbx")
            group2 = kp.add_group(kp.root_group, "TestRelativeKdbxShare")
            group3 = kp.add_group(kp.root_group, "TestAbsoluteKdbxShare")

            create_random_entry(kp, group0, 100)
            create_random_entry(kp, group1, 100)
            create_random_entry(kp, group2, 100)
            create_random_entry(kp, group3, 100)

            # Add KeeShare reference to TestRelativeKdbxShare
            add_custom_data_to_group(kp, group2, "KeeShare/Reference", "PD94bWwgdmVyc2lvbj0iMS4wIj8+PEtlZVNoYXJlPjxUeXBlPjxJbXBvcnQvPjxFeHBvcnQvPjwvVHlwZT48R3JvdXA+M1JSQVdmeFhUdFNtMUc0a1E1TDY2dz09PC9Hcm91cD48UGF0aD5MaTlVWlhOMFVtVnNZWFJwZG1WTFpHSjRVMmhoY21VdWEyUmllQzV6YUdGeVpRPT08L1BhdGg+PFBhc3N3b3JkPk9VZGNkVDBxUGs0dFZGaE9jbVpjYUNzMllrMHpSajg0SXlNaVIzWW1kanhNWjFCY0sxNWhPeWxBZEdCeEpUSlJjWG82UFZoNllqSmpkQzVsT0dGc1ZBPT08L1Bhc3N3b3JkPjxLZWVwR3JvdXBzPlRydWU8L0tlZXBHcm91cHM+PC9LZWVTaGFyZT4K")
            add_custom_data_to_group(kp, group2, "_LAST_MODIFIED", "Mo. Feb. 2 22:49:41 2026 GMT")

        # Add empty groups to TestFile1
        elif file_name == "TestFile1.kdbx":
            kp.add_group(kp.root_group, "TestRelativeKdbx")
            kp.add_group(kp.root_group, "TestAbsoluteKdbx")
            kp.add_group(kp.root_group, "TestRelativeKdbxShare")
            kp.add_group(kp.root_group, "TestAbsoluteKdbxShare")

        kp.save()
        print(f"Created KeePass file: {file_path}")

if __name__ == "__main__":
    create_keepass_files()