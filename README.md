# Motivation

In [KeePassXC](https://github.com/keepassxreboot/keepassxc) multiple bug reports have been filed about password entries
disappearing when the password database is connected to another database via KeeShare (among others,
see [1], [2], [3], [4], [5], [6]).

## Cause of the Problem

Instead of just removing an entry from the database, **the KeePass database format maintains a record of deletions**
inside the `<DeletedObjects>` section. This mechanism allows other synchronized instances of the database (e.g., on
different devices) to recognize that an object was deleted and avoid mistakenly restoring it.

Under normal circumstance, this is beneficial. However, when **KeeShare** is used to connect multiple databases, this
behavior can lead to **serious issues, potentially resulting in lost password entries**. KeePassXC appears to propagate
deletion records **not only to the main database, but also to other (all?) connected databases**.

As a result, even if you have a backup of your database, it may become impossible to restore a deleted entry. As soon as
you open the backup, the list of deleted entries from a connected database may instruct KeePassXC to delete the entry
again.

## A Possible Solution

The KeePassXC team is aware of this problem. Given the design of the **KeePass2 format**, the best approach is to
**manage the list of `<DeletedObject>` entries** in the database.

[KeePass2](https://keepass.info/) (the Windows program) provides
[database maintenance dialogs](https://github.com/keepassxreboot/keepassxc/issues/7550) including an option to **delete
information about deleted objects**. However, **KeePassXC currently lacks this feature**.

At the time of writing, the implementation of such a feature
is "[to be triaged](https://github.com/orgs/keepassxreboot/projects/4/views/1?filterQuery=6477)".

**This program is aims to fill this gap.** it **clears the `<DeletedObjects>` section** of a KeePass database and all
connected databases, enabling the restoration of deleted entries from a backup.

# When Will it Help?

This program may help **if you suspect that missing entries still physically exist** but are being "shadowed" or hidden
due to **deletion records propagated by connected databases**. It is therefore especially useful **if you have a backup
of the database containing the missing entries**.

However, if **no backup is available**, KeePassXC may have already **permanently removed the entries**, making recovery
impossible. In this case, the program will not be able to restore the entries.

## How to Tes if Your Entries are Still There

To check whether the missing entries are still present in your database (or its backup), open the database in an
environment where **KeeShare-connected files are inaccessible**. You can do this by:

- **Renaming or moving the connected database files** to another location.

- **Running KeePassXC in a different location (file system)** where it cannot access the connected databases.

- **Using a different KeePass client that does not support KeeShare**.

Once you open the database in such an environment, you can explicitly check whether the missing entries are still there.

# What Does This Program Do?

This program will perform the following steps:

1. **Open the main KeePass database file** (the program will ask for the file path and the password in a tk dialog).
2. **Scan the database** for credentials (location path and password) of **connected databases**.
3. **Create backups** of the main database and all connected databases.
4. **Remove all entries from the `<DeletedObjects>` section** of the main database and all connected databases (a dialog
   will request confirmation for each database).
5. **Save all modified databases**.

# How to use it?

Follow these steps to use the program:

1. (**Optional but recommended**) **Manually back up** of your main KeePass database and all databases connected via
   KeeShare. This program will also create automatic backups, but why trust a program that you don't know?
2. **Clone this project** with git or download `main.py` and `requirements.txt`.
3. **Ensure Python 3** is installed (this program was tested with **Python 3.13**).
4. (**Optional but recommended**) **Create a virtual environment** for this project. Refer to
   the [Python documentation](https://docs.python.org/3/tutorial/venv.html) for instructions. If
   you are using a virtual environment, activate it before proceeding.
5. Install the required dependencies by running:

       pip install -r "requirements.txt".

6. **Ensure that the KeePass database files are closed** (not open in KeePassXC or any other program).
7. Run the program using:

       python main.py

8. Follow both the **shell output** and **prompts in the tk dialogs that pop up**. The program
   will ask for the file path and password of the **main database**. It will then guide you through the process of
   removing deleted objects from the main database and all connected databases.
9. After completion, open the main database as usual. If successful, the previously missing entries should now be
   present again.

# Disclaimer

This should go without saying but **this program is provided "as is" without any warranty**. Use it at **own
risk**. The author is **not responsible** for any damage or loss of data that may occur as a result of using this
program.

[1]: https://github.com/keepassxreboot/keepassxc/issues/6477

[2]: https://github.com/keepassxreboot/keepassxc/issues/10229

[3]: https://github.com/keepassxreboot/keepassxc/issues/6013

[4]: https://github.com/keepassxreboot/keepassxc/issues/7721

[5]: https://github.com/keepassxreboot/keepassxc/issues/4199

[6]: https://github.com/keepassxreboot/keepassxc/issues/7300
