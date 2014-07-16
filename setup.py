import os
import multiprocessing

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = ['flask',
            'flask-wtf',
            'flask-migrate',
            'flask-sqlalchemy',
            'flask-babel',
            'flask-login',
            'flask-principal',
            'flask-script',
            'path.py']
test_requires = ['pytest', 'pytest-cov']

setup(name='flask-starter',
      version='0.1',
      description='Starting template for flask applications',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          'Development Status :: 4 - Alpha',
          'License :: OSI Approved :: BSD',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
      ],
      author='Mathias Weber',
      author_email='mathew.weber@gmail.com',
      license='bsd',
      test_suite='pytest',
      packages=find_packages(),
      install_requires=requires,
      tests_require=test_requires)
