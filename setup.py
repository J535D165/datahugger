from pathlib import Path

from setuptools import find_packages
from setuptools import setup

# Extract version from datahugger module
for line in open(Path("datahugger", "__init__.py")):

    if line.startswith("__version__"):
        exec(line)
        break

setup(
    name="datahugger",
    version=__version__,  # noqa
    description="A simple tool to hug with research data.",
    author="Jonathan de Bruin",
    author_email="jonathandebruinos@gmail.com",
    url="",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    packages=find_packages(include=["datahugger", "datahugger.*"]),
    install_requires=["requests", "pyDataverse", "tqdm"],
    extras_require={"all": ["datasets"]},
    setup_requires=["flake8", "flake8-import-order"],
    tests_require=["pytest"],
    entry_points={"console_scripts": ["datahugger=datahugger.__main__:main"]},
)
