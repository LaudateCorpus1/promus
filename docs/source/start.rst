.. _getting-started:

***************
Getting Started
***************

In this section we will explain how to create your first repository
in a remote machine to which you have access via ``ssh``. We will 
assume that you already followed the installation instructions in
your local machine. To start first we need to set up the remote
server.

Password-less Connection To Server
==================================

To set up a repository in a remote server we need access to a remote
server. This will be done many times and for that we will want to avoid
typing in your password.

To create a passwordless access to a remote server we use the
``connect`` command ::

    promus connect username@server-name server-alias

Here "server-alias" is the name you want to assign to the remote
server. This is helpful since it can help you avoid typing the
complete server name in the future.

You will be prompted for your password if the remote machine has not
been set up with passwordless access. Once this is done you will be
able to ``ssh`` as you always do minus the password, or you can use
the ``server-alias`` you provided to promus by using::

    ssh server-alias

Once you connect to the server you need to install and setup promus
there so that you may start creating your first repositories. Please
remember to use the same e-mail address you used in your local
machine during the promus setup. You want to make sure that you are
able to identity yourself to the server and others with your email
address.

Send a Collaboration Request
============================

The promus setup helps promus identify you as its master. Once you
create repositories promus will allow you to modify them without
questioning you about your permissions to the repository. To do this
however, you need to act as a git user. In order to do that you need
to send a collaboration request to yourself.::

    promus send request <your_email> 'your name'

This will send an email with an attachment which will be used to
connect to the server as a git user.

Accepting a Collaboration Request
=================================

To accept a collaboration request simply follow the instructions
on the email sent by promus. The typical command to execute is::

    promus add host username@hostname

This has to be done from a working directory which contains the file
``username@hostname``. This file contains a temporary private key
which was set up so that you can send your public key. After this,
you will be able to connect to the server as a git user.

Initializing Your First Repository
==================================

To create your first repository in a remote server you have to first
access the server and execute the following command::

    promus init <name_of_repository>

Where ``<name_of_repository>`` should be replaced by any name you
desire.

.. note::

    This will create the repository in ``~/git``. You may specify the
    directory in which you want the repository to be created by
    specifying the option ``--dir``.


Cloning a Repository
====================

In your local machine now you will want to "clone" or make a copy of
the repository. This can be done by::

    promus clone <host>:/path/to/repository.git

Here ``<host>`` should be replaced by the host you are trying to
obtain the repository from. The path to the repository is usually
``~/git/<repository_name>.git``.

.. note::

    The email sent to you by promus verifying the connection mentions
    the host name and a user name. These two pieces of information
    need to be concatenated with a dash in order to create the server
    name. If you are still not sure which repository and how to clone
    it you may use the command ``promus search``. This will search
    all possible connections to outside repositories and tell you
    how to make a clone.
