Making this doc
===============

Get Sphinx
----------

`Get Sphinx <https://www.sphinx-doc.org/en/master/tutorial/getting-started.html>`_


Github
------


.. code-block:: bash

    # Open this project
    cd docs
    git checkout gh-pages

Build
-----

.. code-block:: bash

    git pull origin gh-pages
    # Bring in any doc changes
    git merge main gh-pages
    # Make the docs
    ./make.sh

Review
------

.. code-block:: bash

   # open the generated html in your browser
   open build/html/index.html

Commit
------

.. code-block:: bash

    git commit
    git push [origin] [gh-pages]

Review Github progress
----------------------



