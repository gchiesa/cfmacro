=============================
Cloud Formation Macro Toolkit
=============================


.. image:: https://img.shields.io/pypi/v/cfmacro.svg
        :target: https://pypi.python.org/pypi/cfmacro

.. image:: https://img.shields.io/travis/gchiesa/cfmacro.svg
        :target: https://travis-ci.org/gchiesa/cfmacro

.. image:: https://readthedocs.org/projects/cfmacro/badge/?version=latest
        :target: https://cfmacro.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/gchiesa/cfmacro/shield.svg
     :target: https://pyup.io/repos/github/gchiesa/cfmacro/
     :alt: Updates



A CloudFormation Toolkit to easily implement processors for Cloudformation Macro


* Free software: MIT license
* Documentation: https://cfmacro.readthedocs.io.

Why CFMacro
-----------

When you do Infrastructure as Code the main goal it's always to create modularity in your code
and be able to reuse the patterns and template as much as possible.

Some template though requires additional implementations for a specific use and with the current AWS Cloudformation
capabilities, you cannot make such generic templates to be real blueprints.

With CFMacro you can incorporate a macro transform to the template in order to pre-process the template
while creating the change set with all the customisation you need.


Features
--------

* Implements a processor engine that enables you to plug multiple processor at time and render the
  result template by using only one lambda function.
* Processors are easy to implement and associate to specific Custom Resource type so you can extend
  this framework with your own additional processors.
* Includes **SgProcessor**, a powerful and very flexible Security Group rules generator.


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
