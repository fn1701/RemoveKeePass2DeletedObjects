# Motivation
In [KeePassXC](https://github.com/keepassxreboot/keepassxc) there are several bug reports about password entries dissapearing, when the password database is connected to another database using KeeShare (among others, see [1], [2], [3], [4], [5], [6]).

## Cause of the problem
Instead of just removing an entry from the database, KeePass keeps a record of deletions inside the `<DeletedObjects>` section. This allows other instances of the database (e.g., on different devices) to recognize that an object was deleted and not mistakenly restore it.

Normally, this is a good thing. However, when the database is connected to another database using KeeShare, this can cause a serious problem leading to the loss of password entries. KeePassXC seems to populate the information about deleted entries not only to the main database, but also to (all?) connected databases.

This can lead to situations where it becomes impossible to restore a deleted entry, even if you have a backup of the database: as soon as you open the backup, the list of deleted entries from a connected database will tell KeePassXC to delete the entry again.

## A possible solution
The KeePassXC team is aware of this problem. Given the design of the KeePass2 format, the best bet is to manage the list of `<DeletedObjects>` in the database.

[KeePass2](https://keepass.info/) (the Windows program) has [dialogs for database maintenance](https://github.com/keepassxreboot/keepassxc/issues/7550) and also includes an option to delete information on deleted objects.
KeePassXC does not have this feature yet.
At the time of writing, the implementation of such a feature is "to be triaged" (see [here](https://github.com/orgs/keepassxreboot/projects/4/views/1?filterQuery=6477)).

This program is aims to do just the same: it will clear the `<DeletedObjects>` section of a KeePassXC database and all connected databases. This should allow you to restore deleted entries from a backup of the database.

# When will it help?
If you have reasons to believe that the entries you are missing are physically still there but shadowed by one or multiple connected databases, this program can possibly help you to make things right again. This is especially true if you have a backup of the database that contains the entries you are missing.

Otherwise, if you don't have a backup, chances are that KeePassXC has already removed the entries from the database, and they are lost.

To test if your database (or database backup) still contains the entries in question, you can open it in an environment, where files connected via KeeShare are not accessible. This can be done by renaming the connected database files or moving them to a different location. Otherwise, you can also move the affected database to a location where KeePassXC cannot access the connected databases. Another way would be to use a different KeePass client that does not support KeeShare.

# What does it do?
This program will do the following:

1. Open the main KeePass database file (the program will ask for the file path and the password in a tk dialog).
2. Crawl the database and find the credentials (file path and password) for all connected databases.
3. Create a backup of all the database files (main database and connected databases).
4. Remove all entries from the `<DeletedObjects>` section of the main database and all connected databases (a dialog will request confirmation for each database).
5. Save all databases.

# How to use it?
To use this program, you need to do the following:

1. (Optional but recommended) Create a manual backup of your main KeePass database and all databases connected via KeeShare. In principle, thiis program will also create automatic backups, but why trust a program that you don't know?
2. Clone this project with git (or just download `main.py` and `requirements.txt`.
3. Make sure you have a recent version of Python 3 installed (this program was tested with Python 3.13).
4. (Optional but recommended) Create a virtual environment for this project. Please refer to the [Python documentation](https://docs.python.org/3/tutorial/venv.html) for instructions on how to do this. If you are using a virtual environment, make sure to activate it before running the program.
5. Install the required dependencies. You can do this by running `pip install -r requirements.txt`.
6. Make sure that the KeePassXC database files are not open in KeePassXC or any other program.
7. Run the program with `python main.py`. Watch the shell output as well as the tk dialogs that pop up. The program will ask for the file path and password of the main database. It will then lead you through the process of removing the deleted objects from the database and all connected databases.
8. After the program has finished, you can open the main database just like you would normally do. If everything went well, you should be able to see the entries that were previously missing.

# Disclaimer
This should go without saying but this program is provided "as is" without any warranty of any kind. Use it at your own risk. The author is not responsible for any damage or loss of data that may occur as a result of using this program.

[1]: https://github.com/keepassxreboot/keepassxc/issues/6477  
[2]: https://github.com/keepassxreboot/keepassxc/issues/10229  
[3]: https://github.com/keepassxreboot/keepassxc/issues/6013  
[4]: https://github.com/keepassxreboot/keepassxc/issues/7721  
[5]: https://github.com/keepassxreboot/keepassxc/issues/4199
[6]: https://github.com/keepassxreboot/keepassxc/issues/7300