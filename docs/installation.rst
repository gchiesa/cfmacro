.. highlight:: shell

============
Installation
============


Use in a lambda package
-----------------------

You need to package the lambda together with the cfmacro library and its own requirements.

CFMacro also includes a utility to package your lambda with dependent requirements in order to be used
in AWS Cloudformation.

In order to prepare the lambda you need to install the library on your local development machine first.



Install via PIP
---------------

To install Cloud Formation Macro Toolkit, run this command in your terminal:

.. code-block:: console

    $ pip install --user cfmacro

This is the preferred method to install Cloud Formation Macro Toolkit, as it will always install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


Install From sources
--------------------

The sources for Cloud Formation Macro Toolkit can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/gchiesa/cfmacro

Or download the `tarball`_:

.. code-block:: console

    $ curl  -OL https://github.com/gchiesa/cfmacro/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install


.. _Github repo: https://github.com/gchiesa/cfmacro
.. _tarball: https://github.com/gchiesa/cfmacro/tarball/master
