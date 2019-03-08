import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rapidminer",
    version="0.0.1",
    author="Ruturaj Nene",
    author_email="rnene@rapidminer.com",
    description="A package with utility functions to work with RapidMiner server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ruturajnene/python_rapidminer_util",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)