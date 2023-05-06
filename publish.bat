#pip install --upgrade setuptools wheel
#pip install --upgrade twine

rmdir /S /Q dist

python setup.py bdist_wheel
twine upload dist/* --verbose -ugeorge0st
