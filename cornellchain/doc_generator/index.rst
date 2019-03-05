Welcome to Cornell Chain's documentation!
=========================================

.. toctree::
   :maxdepth: 3

   self
   blockchain


Setting Up
==========

To install Cornell Chain, simply install Python 3.6 as specified in the homework, and Python "Pip" for Python 3.6.
YOU MUST BE USING PYTHON 3.6+, or we will not support any language-related errors encountered.  We will be testing
your code on Python 3.6.

Then, run ``sudo python3 -m pip install -r requirements.txt`` to install all the requirements locally.

After installing the requirements, ``python3 add_random_pow_blockchain.py`` will populate your database with a fresh
random proof of work blockchain; its execution should yield no errors.

To run the web interface where you can interact with your blockchain, understand it, and debug your solutions to
the homework, run ``python3 run_webapp.py``.  Browsing to `localhost:5000` in your browser should then yield 
a screen that looks like this:

.. figure:: webapp.png
   :scale: 50 %
   :alt: The working web interface for Cornell Chain post-setup.

   The working web interface for Cornell Chain post-setup.


Database Management
===================

To clear the database, simply remove all contents of the ``database`` folder; you may need to do this if the database
becomes corrupted or you wish to regenerate it for any reason.

You can also change the database location on disk by editing the ``config.py`` file.

We recommend testing that, after your solution is complete, you can delete the database and regenerate it using the provided
scripts.  Failure to test this may cause you to miss errors.


Running Tests
=============

To run a single test, use Python module run format from the root homework directory (e.g. - ``python3.6 -m tests.hash`` to run the hash test).
To run all tests, run ``python3.6 run_all_tests.py`` in the root homework directory.


Additional Documentation and Support
====================================

Above are links to the full documentation of all the provided blockchain modules.

For questions, we will post a Slack channel link on the CMS assignment.
