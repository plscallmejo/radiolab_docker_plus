from setuptools import setup

setup(
   name='radiolabdocker',
   version='v1.2.0b',
   author='Haoming Huang',
   author_email='fsplscallmejo@live.com',
   packages=['radiolabdocker'],
   scripts=['bin/*'],
   url='http://pypi.python.org/pypi/???',
   license='LICENSE.txt',
   description='Build radiolab_docker everywhere!',
   long_description=open('README.txt').read(),
   install_requires=[
       "docker",
   ],
)