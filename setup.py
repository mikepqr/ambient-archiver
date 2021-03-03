import pathlib

from setuptools import find_packages, setup

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="ambient-archiver",
    version="0.1.1",
    description="Archive your data from ambientweather.net",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mikepqr/ambient-archiver",
    author="Mike Lee Williams",
    author_email="mike@mike.place",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="weather",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=["requests", "click"],
    entry_points={
        "console_scripts": [
            "ambient=ambient.cli:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/mikepqr/ambient-archiver/issues",
        "Source": "https://github.com/mikepqr/ambient-archiver",
    },
)
