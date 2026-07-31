from setuptools import setup, find_packages

setup(
    name="stalker-cli",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "rich",
        "psutil",
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "stalker=stalker.main:main",
        ],
    },
)