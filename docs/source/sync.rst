.. _sync:

*************************
Synchronizing Directories
*************************

Promus provides a command to perform a two way synchronization of
directories. This comes in handy when we want to create a copy of the
contents of one of our repositories into another machine. In this way
we can continue working on the other machine without first having to
push the changes and then pulling them into the other machine.

Directories Setup
=================

We can sync any two directories as long as they both exist. To
register them to promus we need to first provide the local directory
followed by the remote directory::

    promus sync path/to/local/directory path/to/remote/directory

You may provide a third argument to declare an alias. If at a later
time you wish to sync by referring to an alias you can use the option
``--set-alias``.

Syncing
=======

To sync you may first want to see the entries that promus is keeping
track of::

    promus sync

This will display all the directory pairs that it syncs. To be able
to perform the synchronization you must either enter the entry
integer or the alias for the entry::

    promus sync index/alias

Entry Management
================

There will come a time when some entries are of no use to us. To
remove them we can use the ``--remove`` option. Notice however, that
to remove an entry you must specify the index you wish to remove. The
same goes to the option ``--reset`` which resets the last
synchronization date.

Alias
=====

To be able to refer to a set of directories by an alias you can
always either use three arguments when registering the directories or
use the option ``--set-alias``. This is particular useful because if
you wish to work in three different machines you can give the same
alias to all three parings. Then when syncing under the alias all the
directories will be synced.

Example
=======

To synchronize two local directories::

    $ promus sync ~/Desktop/work ~/Desktop/work-copy
    Registration successful. 
    $ promus sync
    [ 0 ][      Never Synced      ]: /Users/jmlopez/Desktop/work/ <==> /Users/jmlopez/Desktop/work-copy/

There is only one file in the work directory.::

    $ promus sync 0
    [ 0 ][      Never Synced      ]: /Users/jmlopez/Desktop/work/ <==> /Users/jmlopez/Desktop/work-copy/
    * receiving list of incoming files ... done
      - analysing 1 incoming files
        [1/1]: ./ is an existing directory.
      - analysing 1 missing files in remote
        [1/1]: file.txt has been modified - will not be deleted.
    * remote --> local (update: no deletion) ... done
    * local --> remote (delete) ... done
    * saving sync date: Aug/28/2014 - 16:27:54 ... done

To set an alias::

    $ promus sync 0 --set-alias work
    0 <==> work

After doing some work in the directory::

    $ promus sync work
    [ 0 ][ Aug/28/2014 - 16:27:54 ][ work ]: /Users/jmlopez/Desktop/work/ <==> /Users/jmlopez/Desktop/work-copy/
    * receiving list of incoming files ... done
      - analysing 1 incoming files
        [1/1]: ./ is an existing directory.
      - analysing 10 missing files in remote
        [1/10]: file copy.txt may require deletion.
        [2/10]: file copy 9.txt may require deletion.
        [3/10]: file copy 8.txt may require deletion.
        [4/10]: file copy 7.txt may require deletion.
        [5/10]: file copy 6.txt may require deletion.
        [6/10]: file copy 5.txt may require deletion.
        [7/10]: file copy 4.txt may require deletion.
        [8/10]: file copy 3.txt may require deletion.
        [9/10]: file copy 2.txt may require deletion.
        [10/10]: file copy 10.txt may require deletion.
    * remote --> local (update: no deletion) ... done
    * local --> remote (delete) ... done
    * saving sync date: Aug/28/2014 - 16:29:33 ... done

In this case the file was copied multiple times. Since these files
did not exit in the remote location it could have meant that the file
required deletion. It is only after performing the update when we
realize that these files are new and that they must be uploaded to
the remote location.

.. note::

    The sync command is more useful if you are using it with
    repositories. This will allow you to see if you obtained all the
    correct changes to the directories and will prevent you from
    losing or overwriting any desirable data.
