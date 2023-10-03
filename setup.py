import os

import pkg_resources
from setuptools import setup, find_packages

version = "0.0.1"

with open("README.md") as file:
  readme = file.read()

setup(
  name="pitcheon",
  version=version,
  description="utility for tagging WAV files with pitch metadata",
  long_description=readme,
  long_description_content_type="text/markdown",
  url="https://github.com/ahihi/pitcheon",
  author="pulusound",
  author_email="miranda@pulusound.fi",
  packages=find_packages(),
  scripts = ["bin/pitcheon"],
  license="cc0",
  install_requires=[
    "numpy~=1.21",
    "scipy~=1.11",
    "wave-chunk-parser~=1.4.2",
    "wquantiles~=0.6.0"
  ],
  extras_require={
    "crepe": [
      "crepe>=0.0.12",
      "tensorflow>=2.8,<3"
    ]
  }
)
