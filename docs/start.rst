.. _getting-started:

***************
Getting Started
***************

Promus allows you to create repositories in a remote server to which
you and your collaborators may have access to. There are several
scenarios in which you can use promus.


Password-less Connection To Server
==================================

We assume that you wish to create a repository in some server to
which you have access via ``ssh`` from your personal computer. We
also assume that the alias given to your personal computer is ``mac``
and shall henceforth refer to the personal computer by the alias.

To create a passwordless access to a remote machine we need to let
the remote machine get a hold of a public key that may have been
created by promus or may have already existed in the ``mac`` machine.

To do this use the promus ``connect`` command:

.. code-block:: sh

    promus connect username@server-name server-alias

You will be prompted for your password the remote machine has not
been set up with passwordless access. Once this is done you will
be able to ``ssh`` as you always do minus the password, or you can
use the ``server-alias`` you provided to promus:

.. code-block:: sh

    ssh server-alias

Once you connect to the server you can install promus there so that
you may start creating your first repositories.


Send a Collaboration Request
============================

If you wish for collaborators to be able to access your repositories
you need to let promous know what their public keys are so that they
may access your account with a limited amount of privilages. These
privilages are minimum and they only include ``git`` commands.

To let promus send an email in your behalf you can execute the
following command:

.. code-block:: sh

    promus send request email@hostname 'First Last'

The last argument, namely ``'First Last'`` is not required but if you
provide it, then promus will address your collaborator by that name.
The email sent will contain contain a link to this documentation and
the command that needs to be executed to accept the request.

Accepting a Collaboration Request
=================================

By accepting a collaboration request you will simply send your public
key so that your host can recognize you. The instructions on how to do
this are stated on the email sent by your host. The typical command
to execute is

.. code-block:: sh

    promus add host username@hostname

This has to be done from a working directory which contains the file
``username@hostname``. This file contains a temporary private key
which was set up just so that you can send your public key. After
this, you will be able to connect to a repository to which your
collaborator has given you permission to access.


