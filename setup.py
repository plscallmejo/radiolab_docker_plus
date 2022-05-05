from setuptools import setup

setup(
   name='radiolabdocker',
   version='v1.2.0b',
   author='Haoming Huang',
   author_email='fsplscallmejo@live.com',
   packages=['radiolabdocker'],
   scripts=['bin/radiolabdocker'],
   url='https://github.com/plscallmejo/radiolab_docker',
   license='LICENSE',
   description='Build radiolab_docker everywhere!',
   long_description=open('README.md').read(),
   include_package_data=True,
   install_requires=[
       "docker",
       "dockerpty"
   ],
)