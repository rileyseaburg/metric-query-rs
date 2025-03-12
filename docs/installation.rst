Installation
===========

This page provides instructions for installing the Metric Query Library.

Prerequisites
------------

Before installing the Metric Query Library, ensure you have the following prerequisites:

* Python 3.8 or higher
* Rust 1.55 or higher
* pip (Python package installer)

Installing from PyPI
-------------------

The simplest way to install the Metric Query Library is from PyPI:

.. code-block:: bash

    pip install metric_query_library

Installing from Source
---------------------

To install the Metric Query Library from source, follow these steps:

1. Clone the repository:

   .. code-block:: bash

       git clone https://github.com/your-organization/metric-query-rs.git
       cd metric-query-rs/metric-query-library

2. Install the package:

   .. code-block:: bash

       pip install .

   This will use maturin to compile the Rust code and install the Python package.

Development Installation
-----------------------

For development, you may want to install the package in editable mode:

.. code-block:: bash

    pip install -e .

This allows you to modify the source code and have the changes immediately available without reinstalling the package.

Verifying Installation
---------------------

To verify that the installation was successful, you can run a simple Python script:

.. code-block:: python

    import metric_query_library
    
    # Print the version
    print(metric_query_library.__version__)

Troubleshooting
--------------

If you encounter issues during installation, check the following:

* Ensure you have the correct version of Rust installed
* Check that your Python version is 3.8 or higher
* Make sure you have the necessary build tools installed for your platform

For platform-specific issues:

Windows
~~~~~~~

On Windows, you may need to install the Microsoft Visual C++ Build Tools:

.. code-block:: bash

    pip install --upgrade setuptools wheel
    pip install --upgrade maturin

macOS
~~~~~

On macOS, you may need to install the Xcode Command Line Tools:

.. code-block:: bash

    xcode-select --install

Linux
~~~~~

On Linux, you may need to install additional development packages:

.. code-block:: bash

    # Ubuntu/Debian
    sudo apt-get install build-essential python3-dev

    # Fedora/RHEL
    sudo dnf install gcc python3-devel