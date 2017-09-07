from setuptools import setup

setup(name='magD',
      version='0.1.0',
      packages=['magD'],
      install_requires=[
          "numpy"
          ],
      entry_points={
          'console_scripts': [
              'magD = magD.magD.py',
              'obs = obs.obs.py'
          ]
     },
)