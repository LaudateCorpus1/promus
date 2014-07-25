.. _install:

*****************
Installing Promus
*****************

There is more than one way to install promus, here we present two
options, the easy way and the not so easy way. Choose one and
continue reading.

The Easy Way
============

The easiest way to install promus is to use ``pip``. If you wish to
perform a global installation and you have admin rights then do

.. code-block:: sh

    sudo pip install promus

or to install in some directory under your user account

.. code-block:: sh

    pip install --user promus


Installing on \*nix Systems
===========================

From the command line do the following (where x.y is the version
number):

.. code-block:: sh

    wget https://pypi.python.org/packages/source/p/promus/promus-x.y.tar.gz
    tar xvzf promus-x.y.tar.gz
    cd promus-x.y/
    sudo python setup.py install

The last command can be replaced by ``python setup.py install
--user``. See `PyPI <https://pypi.python.org/pypi/promus/>`_ for all
available versions.

You may install promus at any time but be aware that the script will
not work unless you have ``git`` installed.

.. _git:

Git
===

Promus was designed with one goal in mind: to make ``git`` available
in your own server without administrator rights. For this reason,
before you even think about using promus you must obtain a copy of
``git`` which you can obtain at `http://git-scm.com/downloads
<http://git-scm.com/downloads>`_.

Make sure that ``git`` is installed in your system before proceding
with the next section.

.. _setup:

Promus Script
=============

Before you can use promus you must make sure that you can access
the ``promus`` command from your shell. For that you need to make
sure that your ``PATH`` includes the path where your ``promus`` script
is installed.

To locate the paths python stores its packages simply fire up ``python``
and enter the following

.. code-block:: python

    import sys, site
    path = '%s/bin:%s/bin' % (site.getuserbase(), sys.prefix)
    print "export PATH=%s:$PATH\n" % path

Now copy the output given the commands and append it to the file
``~/.bash_profile`` or ``.bashrc`` depending on the system and shell
you are using. In this case we assume you are using ``bash``.

Setting up promus
=================

If you completed the previous sections then you are well on your way
to creating your first private repositories or to connect to one.
First you need to let promus and git some information about yourself.
::

    $ promus setup
    Full name: 
    E-mail address: 
    Hostname alias: 
    Host e-mail: 
    Password:

Keep in mind that if you are not going to use your personal computer
to create repositories then there is no need to provide a ``Host
e-mail`` nor a ``Password``. What is important however, is that you
provide a ``Hostname alias``. The alias will be helpful to identify
the machine from where you provided commands.

If you are setting up promus to create repositories and your server
provides you with an e-mail address then you are allowed to ommit
entering your password since the system can authenticate you when you
``ssh`` to the server.

To make sure that the email you provided for the host is working you
can use the ``verify`` command to make promus send you an email. ::

    $ promus verify
    sending email ... done

At this point you should be ready to start using promus.
