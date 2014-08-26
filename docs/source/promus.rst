***************
What is Promus?
***************

Promus is a manager designed to allow the synchronization of digital
information. It can be used to create your personal data backups or
to collaborate with others. Promus is a sandbox where ``ssh`` and
``git`` commands are executed in order to manage your data.

Why Promus?
+++++++++++

Several free services already exist which allow you to easily backup
and synchronize your data. These are great tools but they have
limitations. Here we will explore two services in particular, Dropbox
and Github.

Dropbox
+++++++

This is a service which seamlessly synchronizes data among distinct
machines. The idea is simple, we have several machines in which we
would like to have access to some data. Suppose we have machine A, B
and C. With Dropbox we can create a directory in machine A, place
some data in it and later on access this same data through machine B
and C. This is possible due to the Dropbox server to which data is
uploaded and downloaded in order to perform a synchronization.

Dropbox can serve as a backup source and it can also be used to share
with family, friends or even collaborators. The main advantage of
this software is that the end user does not have to worry about
synchronization, everything just happens. This is great when only a
single user has access to his data but complications can arise once
we start sharing our files with others.

The main disadvantage of Dropbox is collaboration. When we allow a
directory to be shared with others we can run into conflicting copies
of our files. This happens when user A modifies a file when the
Dropbox service is not on (perhaps the user turned it off or
there was no network access). Meanwhile user B modifies that same
copy at a later time. When user A finally obtains network access
Dropbox will have two copies of this file which now has different
content. That is, the changes of user B will most likely be
overwritten. Dropbox does create a backup file when conflicts happen,
but this can be a headache to collaborators when they are trying to
find out how to fix these changes since there is no clear way of
finding out what changes to keep.

Another disadvantage is the amount of data that Dropbox allows you to
synchronize for free. If more space is needed then it must be
purchased.

Github
++++++

Github focuses in collaboration. It does so by using the `git
<http://git-scm.com/>`_ software to create repositories which help
you can keep track of all the changes done to your files. Their
website has been designed to display all the information about the
repositories in an intuitive and useful manner.

Conflicting files will always arise regardless of what service you
use, but with git we can see exactly what the conflicts are so that
you may fix them and move on.

However, unlike Dropbox, here you have to explicitly state when you
want synchronize, this is done by first creating a "commit". When
creating a commit you write a description of the changes made to the
files, hopefully something meaningful which will help you and other
collaborators whenever we look back at the history of the files.

The main Drawback with Github is financially. This time is not a
matter of space, but about privacy. Github provides free repositories
as long as they are public. That is, everyone with an internet
connection can have access to your files. If you would like a project
of yours to be private then you have pay a fee.

Git
+++

Github uses the git software in order to make the synchronization
possible. There are several other software which uses git to achieve
the same but this time in our own servers: Gitosis and Gitolite.
These softwares however make one undisclosed assumption: you must be
the administrator of the server. The way the communication between
the server and our personal machines is possible is through the git
user which must be created in the server. Once we manage to create
the repository in the server then we have to give access to other
users by modifying files which only an administrator has access to.

SSH and Promus
++++++++++++++

To answer the previous questions, promus is a python script which
user ``ssh`` and ``git`` commands to create your own personal
repositories under your user account. As to why you would like to use
promus, simply consider that, as opposed to gitosis and gitolite,
there is no need to ever contact your administrator for anything
related to the git or ssh software or to ask to allow someone else to
access your repositories. Is promus secure? As with any software,
promus will only be as secure as you make it to be. Promus uses
``ssh`` to allow other people to connect to your repositories, it is
up to you to only allow trusted collaborators access to them. If you
have access to a trusted server, say a server at your department at
an institution then give promus a try and see how simple it is to
keep track of your work and collaborate with others.
