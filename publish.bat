rem pip install --upgrade setuptools wheel
rem pip install --upgrade twine

rmdir /S /Q dist
rmdir /S /Q build

rem 'setup.py bdist_wheel' is deprecated recommendation is to use 'python -m build'
python setup.py bdist_wheel

rem FULL DESCRIPTION
rem https://packaging.python.org/en/latest/tutorials/packaging-projects/
rem new way 'pyproject.toml' + 'python -m build.'

rem or https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html
rem SAMPLE https://github.com/pypa/sampleproject/blob/main/pyproject.toml


rem So keep the version only in the pyproject.toml and use this in your python code:
rem import importlib.metadata
rem __version__ = importlib.metadata.version(__package__ or __name__)

rem twine upload is supported
twine upload dist/* --verbose -ugeorge0st
