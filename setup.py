from setuptools import setup

setup(name='magD',
      version='0.1.0',
      packages=['magD'],
      install_requires=[
          "numpy",
          "matplotlib",
          "geojson",
          "geobuf",
      ],
      entry_points={
          'console_scripts': [
              'magD = magD.__main__:main'
          ]
     },
)