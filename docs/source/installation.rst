.. _install:

************
Installation
************

Promus depends on other software. First we will go through some of
the requirements.


Requirements
============

- Python: Promus is a python package, thus if you wish to use promus
  you will need a copy of Python installed on your system.
- Git: You may obtain a copy of ``git`` at
  `http://git-scm.com/downloads <http://git-scm.com/downloads>`_.
- Pip: To make the installation of promus slightly easier you can use
  `pip <http://pip.readthedocs.org/en/latest/installing.html#install-pip>`_.
  Having this package installed will make the installation of
  promus and future packages a breeze.


Installing promus
=================

The easiest way to install promus is to use ``pip``. If you wish to
perform a global installation and you have admin rights then do::

    sudo pip install promus

or to install in some directory under your user account::

    pip install --user promus

If you prefer to do the installation manually then from the command
line you may do the following (where x.y is the version number): ::

    wget https://pypi.python.org/packages/source/p/promus/promus-x.y.tar.gz
    tar xvzf promus-x.y.tar.gz
    cd promus-x.y/
    sudo python setup.py install

The last command can be replaced by ``python setup.py install
--user``. See `PyPI <https://pypi.python.org/pypi/promus/>`_ for all
available versions.

Once you have finished do the installation you need to set up your
``$PATH`` so that your shell may look for it. If you are using ``bash``
you can call the ``install`` command from promus::

    python -m promus install

After performing this command you will be able to use promus from the
command line::

    promus -h


Setting up promus
=================

Once you complete the installation we need to first setup promus.
This is done by giving some information about yourself::

    $ promus setup
    Full name: 
    E-mail address: 
    Hostname alias: 
    Host e-mail: 
    Password:

Your "Full name" and "E-mail address" are the two pieces of
information that identify you. Please use the email address that you
would want collaborators to use when they request that you join one
of their projects. All authentication is done by comparing an email
address.

.. note:: 

    Make sure to use only one e-mail address in all the machines you
    are using. This will help with the identification of users even
    if you have different usernames in different machines.

The "Hostname alias" should be a word that helps you identify the
host that you are using. For instance, when using a macbook pro you
could give the machine a name and thus you could use that as the
Hostname alias. This will not only help you but also your
collaborators know where you are submitting information from.

The "Host e-mail" and "Password" are two entries which you may skip
if you are not planning on Hosting any repositories. If you do decide
to Host repositories then you can use any email address setup with
smtp (gmail, yahoo, etc) and its password. This email address will be
used to send emails on your behalf to the users of the repository.

To make sure that the email you provided for the host is working you
can use the ``verify`` command to make promus send you an email. ::

    $ promus verify
    sending email ... done

At this point you should be ready to start using promus.
