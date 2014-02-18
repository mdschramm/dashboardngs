======================================
How to Set Up the Multiscale Dashboard
======================================

Guide written by `Mark Micchelli`_

.. _`Mark Micchelli`: mailto:mark.micchelli@mssm.edu

The production version of the Multiscale Dashboard currently lives
in Mark Micchelli's Minerva account: ``/hpc/users/micchm01``.

There are two places you can set up a custom development version
of the Multiscale Dashboard--on Minerva, or on your local machine.
In both cases, it is highly recommended you use pip_,
virtualenv_, and optionally, virtualenvwrapper_.

.. _pip: http://pypi.python.org/pypi/pip
.. _virtualenv: http://www.virtualenv.org
.. _virtualenvwrapper: http://virtualenvwrapper.readthedocs.org


Setting Up the Multiscale Dashboard on Minerva
==============================================

Instructions
------------

Chances are, you just want to get up and running as fast as possible,
and this is a loooong document. I encourage you to at least skim
through the explanation section, but if you just stick close to
these instructions you should be be okay.


Part 1: Installing Pip, Virtualenv, and Virtualenvwrapper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Install pip to your local site-packages directory (instructions
   modified slightly from
   http://www.pip-installer.org/en/latest/installing.html#installing-from-source)::

	$ curl -O https://pypi.python.org/packages/source/p/pip/pip-X.X.tar.gz
	$ tar xvfz pip-X.X.tar.gz
	$ cd pip-X.X
	$ python setup.py install --user


2. Add your local site-packages directory to your path::

	# add the following lines to your bash_profile
	PATH=$PATH:$HOME/.local/bin
	export PATH

	# then, in the shell, run the following
	$ source ~/.bash_profile


3. Install virtualenv and virtualenvwrapper to your local site
   packages directory::

	$ pip install --user virtualenv
	$ pip install --user virtualenvwrapper


4. Set up a virtualenv called "dashboardngs" (instructions
   slightly modified from
   http://virtualenvwrapper.readthedocs.org/en/latest/#introduction)::

	# run the following in the shell
	$ export WORKON_HOME=~/.virtualenvs
	$ mkdir -p WORKON_HOME
	$ source $HOME/.local/bin/virtualenvwrapper.sh
	$ mkvirtualenv dashboardngs

	# then, add the following line to your bash_profile
	source $HOME/.local/bin/virtualenvwrapper.sh


Part 2: Getting the Dashboardngs Repo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

5. Create the following directory structure underneath your home directory::

		$HOME
		|- www
		   |- staging
		   |- static
		      |- dashboardngs_staging
		   |- media
		      |- dashboardngs_staging

   **PLEASE NOTE:** If you already have a folder called ``staging``
   in your ``www`` directory, all is not lost. Just continue with
   these instructions while using a different name, and once you're
   all done, replace all instances of ``staging`` in the
   ``pbg/settings/staging.py`` file with whatever you chose.


6. In the ``www/staging`` directory, execute the following command::

	$ git clone https://<username>@bitbucket.org/hardikshah/dashboardngs.git


Part 3: Installing Django and Other Python Package Requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

7. Add the global MySQL-python package to your Python path::

	# add the following lines to your bash_profile
	PYTHONPATH=$PYTHONPATH:/usr/lib64/python2.6/site-packages
	export PYTHONPATH

	# then, in the shell, run the following
	$ source ~/.bash_profile


8. Make sure you are in your virtualenv (virtualenvwrapper syntax shown)::

	$ workon dashboardngs


9. Install all packages in the ``requirements.txt`` file::

	$ pip install -r $HOME/www/staging/dashboardngs/requirements.txt


Part 4: Setting Up Your Environment Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

10. Create the a script called ``virtualdjango.py`` in
    ``$HOME/.virtualenvs/dashboardngs/bin``::

	# contents of virtualdjango.py

	activate_this = "/path/to/virtualenvs/dashboardngs/bin/activate_this.py"
	execfile(activate_this, dict(__file__=activate_this))
	from django.core.handlers.modpython import handler


11. Add the following lines to your ``bash_profile``::

	export DASHBOARD_NGS_GMAIL_PASSWORD=""
	export DASHBOARD_NGS_DEV_DATABASE_PASSWORD=""
	export DASHBOARD_NGS_SECRET_KEY=""

    **PLEASE NOTE:** we are deliberately keeping the database password
    and secret key out of version control. You will need to ask a current
    Multiscale Dashboard dev for this information.


12. Create a file called ``.htaccess`` in your ``$HOME/www/staging``
    directory::

	# Contents of .htaccess

	SetHandler python-program
	PythonHandler virtualdjango
	PythonPath "['/hpc/users/USERNAME/.virtualenvs/dashboardngs/bin', '/hpc/users/USERNAME/www/staging/dashboardngs/pbg'] + sys.path"
	SetEnv HOME "/hpc/users/USERNAME/"
	SetEnv DJANGO_SETTINGS_MODULE pbg.settings.staging
	SetEnv DASHBOARD_NGS_GMAIL_PASSWORD ""
	SetEnv DASHBOARD_NGS_DEV_DATABASE_PASSWORD ""
	SetEnv DASHBOARD_NGS_SECRET_KEY ""
	PythonDebug On


Explanations
------------

This is a long, complicated process, and I'm working to try to
simplify it. However, many of these steps are not specific to the
Multiscale Dashboard; if you ever want to start another serious
Python or Django project, the infrastructure provided here will
make that setup much easier. Furthermore, after all these steps are
completed, working with your development environment will be as
painless as can be. With this setup, you can confidently push your
work to the production environment, and you should be able to deftly
handle trickier matters like database schema changes and data
migrations.


Part 1: Installing Pip, Virtualenv, and Virtualenvwrapper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before setting up anything on Minerva, you should make sure you have
installed pip, virtualenv, and virtualenvwrapper. These
tools isolate your development environment as much as possible from
Minerva, meaning you can install your own version upgrades and helper
packages without needing to contact the HPC team.

Python packages usually live in a global directory called
``site-packages`` underneath the main Python installation. Minerva
being what it is, there are about a dozen different ``site-packages``
directories in all sorts of different places, each corresponding
to a different version of Python (and, of course, you don't have
write access to any of them). Rather than try to wade though Minerva's
global package soup, a better and more maintainable solution is to
create your own local ``site-packages`` directory. As outlined in
`PEP 370`_, this directory is conventionally called ``$HOME/.local``,
and it should contain the subdirectories ``bin`` and ``lib/pythonX.X``.
Whenever you install a Python package with ``python setup.py install``
you can choose to install to the local ``site-packages`` instead
of the global ``site-packages`` directory by including a ``--user``
flag in the command. For more information on local installation
check out http://docs.python.org/2/install/.

.. _`PEP 370`: http://www.python.org/dev/peps/pep-0370/

However, this isn't the whole story. Let's say you want to build
another Django project on Minerva. What happens if you want to use
a version different than the on used by the Multiscale Dashboard?
It would be a nightmare to try to install both in ``$HOME/.local``,
especially without an easy way to switch between them. To solve
this problem, you should use a tool called virtualenv, which creates
isolated Python packaging environments for each of your projects.
The syntax of virtualenv is a little ugly, so the Python community
created a set of wrapper scripts called virtualenvwrapper. While
not strictly necessary, I personally find virtualenvwrapper to be
immensely useful, and so I assume it's being used throughout this
document.

Finally, pip is a tool used to replace the standard ``python setup.py
install`` command. Pip makes installation easier because it downloads
the package from the Python Package Index (PyPI) in addition to
handling the build and installation. To install a package with pip,
just type ``pip install PACKAGE``, and to install it in the local
``site-packages`` directory, use ``pip install --user PACKAGE``.



Part 2: Getting the Dashboardngs Repo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This part is the most straightforward of them all--create a directory
structure in ``www`` and clone the bitbucket repo into it. The only
issue of note is that Minerva is very finicky about the names of
the ``static`` and ``media`` directories: it will *only* serve
static files and media files from subdirectories with those exact
names.


Part 3: Installing Django and Other Python Package Requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to run the Multiscale Dashboard, you need a minimum of two
Python packages: Django and MySQL-python. Additionally, the Multiscale
Dashboard uses a few third party packages, and has probably added
even more since this document was written. As mentioned in Part 1,
it is imperative to keep all installations local and away from the
global soup on Minerva. However, there is **one exception**:
MySQL-python. Because we have to use the MySQL server on Minerva,
it is much easier to just plug into the global MySQL-python connector.
I actually tried to hook into the Minerva MySQL with a local MySQL-
python connector, but it just proved too difficult.

The Multiscale Dashboard keeps track of all if its package requirements
in a ``requirements.txt`` file, located in the root directory of
the repo. Installing everything we need is as simple as the following
command: ``pip install -r requirements.txt``. If inside a virtualenv,
this will perform a virtualenv-specific install of every package
listed in that file. However, we want to make sure to use the global
version of MySQL-python, even though it is listed as a requirement.
The trick here is to know that pip will try to install every package
in ``requirements.txt``--*unless it senses that package on your
Python path*. Therefore, you need to make sure to manually add
MySQL-python to your Python path before running ``pip install -r``.


Part 4: Setting Up Your Environment Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to make the Multiscale Dashboard project flexible with
regards to location, I rely heavily on environment variables in my
settings files. This also has the benefit of keeping private
information, such as database passwords, out of source control. To
get a sense of where all these variables come into play, look at
the files ``pbg/settings/staging.py`` and ``pbg/settings/base.py``.

It is important to add your environment variables to *both* your
``bash_profile`` and ``.htaccess`` file. The ``bash_profile``
variables are used whenever accessing the project through the
terminal (such as when running ``manage.py`` commands), while the
``.htaccess`` variables are used whenever accessing the project
through your Minerva web account.


Troubleshooting
---------------

You may run into a issue when using ``manage.py``, where the program
complains that some Django module cannot be found. Two things could
be causing this:

1. You are not in a virtualenv. Try running
   ``$ workon dashboardngs``.
2. You did not you must include the settings file you want to
   use with the command.  You can do this by either specifying
   it in the command itself (``python manage.py COMMAND
   --settings=pbg.settings.staging``) or by permanently adding
   ``DJANGO_SETTINGS_MODULE`` to your ``bash_profile`` with the
   value ``pbg.settings.staging``.
