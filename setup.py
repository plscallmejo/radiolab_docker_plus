from importlib.metadata import entry_points
import platform
from setuptools import setup

os_type = platform.system()
if os_type == 'Windows':
    requirements = ['docker', 'pypiwin32', 'pywin32']
else:
    requirements = ['docker']

setup(
   name='radiolabdocker-plus',
   version='v0.1.1b',
   author='Haoming Huang',
   author_email='fsplscallmejo@live.com',
   packages=['radiolabdocker'],
   entry_points={
       'console_scripts':[
           'radiolabdocker=radiolabdocker.CommandLine:cli',
           'radiolabdocker-plus=radiolabdocker.CommandLine:cli',
           'rdps=radiolabdocker.CommandLine:cli'
       ]
   },
   url='https://github.com/plscallmejo/radiolab_docker',
   license='LICENSE',
   description='Build and run radiolab_docker everywhere!',
   long_description=open('README.md').read(),
   include_package_data=True,
   install_requires=requirements
)
