from setuptools import setup, find_namespace_packages

setup(
    name="comrade",
    version="1.0.0",
    py_modules=["main"],
    packages=find_namespace_packages(),
    entry_points={
        "console_scripts": [
            "comrade=main:main",
        ],
    },
)