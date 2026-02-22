# Test Scenario

I managed to recreate the scenario I faced for some example files if someone wants/needs to see it:

- copy <https://github.com/fn1701/RemoveKeePass2DeletedObjects/tree/master/test/TestFiles> to /tmp/TestFiles
- disable `Settings > KeeShare > Allow import` and `Settings > KeeShare > Allow export` in KeePassXC Settings
- check if all Groups contain entries
- enable `Settings > KeeShare > Allow import` and `Settings > KeeShare > Allow export` in KeePassXC Settings
- Groups 1-3 should be empty now

I managed to do this by sharing 4 Groups (with each Group having a .kdbx or kdbx.share file) between 2 Databases. Then I deleted all Groups from TestFile0.kdbx and merged it with a previous version of TestFile0.kdbx. This propagated the deleted entries to the .kdbx or kdbx.share files except for some reason for the 4th/last Group.
If you know open TestFile1.kdbx with import/export enabled these deletedObjects will sync to that file as well and delete the corresponding entries from it.
