from setuptools import setup

with open("readme-pypi.md", 'r') as fh:
    long_description = fh.read()

setup(
    name='qtap',
    version='0.1.1',
    packages=['qtap'],
    url='https://github.com/kushalkolar/qtap',
    license='GPL v3.0',
    author='Kushal Kolar',
    author_email='kushalkolar@alumni.ubc.ca',
    description='Automatic Qt parameter entry widgets using function signatures ',
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>=3.6',
)
