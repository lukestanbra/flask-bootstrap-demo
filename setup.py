from setuptools import find_packages, setup
from pathlib import Path

with open(Path().absolute() / 'requirements.txt') as fh:
  required= fh.readlines()

setup(
  name="flask-bootstrap-demo",
  version="0.1",
  packages=find_packages(),
  include_package_data=True,
  zip_safe=False,
  install_requires=required
)