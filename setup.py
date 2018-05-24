from setuptools import setup

setup(name='magD',
      version='0.9.0',
      packages=['magD'],
      author='Jon Connolly',
      author_email='joncon@uw.edu',
      url='https://github.com/pnsn/magD',
      python_requires='~-3.5.2',
      dependency_links=['https://github.com/matplotlib/basemap/archive/v1.1.0.tar.gz'],
      install_requires=[
          'numpy',
          'pandas',
          'matplotlib',
          'obspy',
          'geographiclib',
        ],

)
