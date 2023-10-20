rem pip install --upgrade setuptools wheel
rem pip install --upgrade twine

rmdir /S /Q dist
rmdir /S /Q build

rem 'setup.py bdist_wheel' is deprecated recommendation is to use 'python -m build'
rem python -m build --wheel
rem py -m build

rem helper 'https://www.scivision.dev/python-minimal-package/'
rem https://pypa-build.readthedocs.io/en/latest/
rem https://github.com/pypa/build
python -m build --sdist --wheel

rem  --no-isolation
rem --sdist, -s - build a source distribution (disables the default behavior)
rem --wheel, -w - build a wheel (disables the default behavior)


rem twine upload is supported
twine upload dist/* --verbose -u__token__
