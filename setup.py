from setuptools import setup, find_packages
import sys, os
from os.path import join
import imp
setupy_download_helper_path = join(
    os.path.dirname(os.path.abspath(__file__)), 'setupy_download_helper.py')
setupy_download_helper = imp.load_source(
    'setupy_download_helper', setupy_download_helper_path)

version = '2.14.1'
setupy_download_helper.CHROMEDRIVER_VERSION = version[:4]

setup(name='chromedriver',
      version=version,
      description="Tool for downloading chromedriver",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='chromedriver',
      author='Maksym Shalenyi (enkidulan)',
      author_email='supamaxy@gmail.com',
      url='',
      license='apache2.0 (http://www.apache.org/licenses/LICENSE-2.0)',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      cmdclass={
          'install': setupy_download_helper.InstallCommand,
          'bdist_egg': setupy_download_helper.BdistEggCommand,
          'develop': setupy_download_helper.DevelopCommand},
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
