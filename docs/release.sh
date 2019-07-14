#!/bin/sh

# Execute this from the top-level directory.

# I think these packages are required:
# autodoc>=0.5.0
# docutils>=0.14
# numpydoc>=0.9.1
# Sphinx>=2.1.2

# Make documentation
sphinx-apidoc -f -o docs/ atomic_store/ atomic_store/tests/
mv docs/modules.rst docs/index.rst
make -C docs html
rm docs/_build/html/py-modindex.html

# I think these packages are required:
# setuptools>=41.0.1
# twine>=1.13.0
# wheel>=0.32.3

python3 setup.py sdist bdist_wheel
echo "Should execute the rest manually."
exit 1

# Via test:
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
firefox https://test.pypi.org/project/atomic_store
# Install from test:
python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps atomic_store

# Via prod:
twine upload dist/*
firefox https://pypi.org/project/atomic_store
