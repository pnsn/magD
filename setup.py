from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="MagD",
    version="2.2",
    author="Jon Connolly",
    author_email="joncon@uw.edu",
    description="A map based packaged to analyze seimic network perfromance",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pnsn/magD",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
