from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='freeplane_schema',
    version='0.1.1',
    description='Python representation of the Freeplane XML schema',
    long_description=readme,
    author='Michel JACQUES',
    author_email='mmichelm.jacques@gmail.com',
    url='https://github.com/abovetheborg/freeplane_schema',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
