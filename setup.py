import codecs
import re
import sys
import syncli

from setuptools import setup, find_packages

INSTALL_REQUIRES = [
    "requests>=2.27.0",
]

# if "win32" in str(sys.platform).lower():
#     # Terminal colors for Windows
#     INSTALL_REQUIRES.append("colorama>=0.2.4")

# EXTRAS_REQUIRE = {
#     "tests": ["pytest", "IPython"],
#     "lint": [
#         "flake8==3.9.2",
#         "flake8-bugbear==20.11.1",
#         "pre-commit~=2.20.0",
#     ],
# }
# EXTRAS_REQUIRE["dev"] = EXTRAS_REQUIRE["tests"] + EXTRAS_REQUIRE["lint"] + ["tox"]


def find_version(fname):
    """Attempts to find the version number in the file names fname.
    Raises RuntimeError if not found.
    """
    version = ""
    with codecs.open(fname, "r", encoding="utf-8") as fp:
        reg = re.compile(r'__version__ = [\'"]([^\'"]*)[\'"]')
        for line in fp:
            m = reg.match(line)
            if m:
                version = m.group(1)
                break
    if not version:
        raise RuntimeError("Cannot find version information")
    return version


def read(fname):
    with codecs.open(fname, "r", encoding="utf-8") as fp:
        content = fp.read()
    return content


setup(
    name="syncli",
    version=find_version("syncli/__version__.py"),
    description="Instana Synthetic CLI",
    long_description=read("README.md"),
    author="Rong Zhu Shang, Swetha Lohith",
    author_email="shangrz@cn.ibm.com, Swetha.Lohith@ibm.com",
    url="https://github.com/instana/synthetic-synctl",
    install_requires=INSTALL_REQUIRES,
    # extras_require=EXTRAS_REQUIRE,
    python_requires=">=3.6",
    license="MIT",
    zip_safe=False,
    keywords="Instana Synthetic CLI",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Environment :: Console",
    ],
    packages=find_packages(include=["syncli"]),
    entry_points={
        "console_scripts": [
            "synctl = syncli.cli:main"
            ]
        },
    tests_require=["pytest"],
    project_urls={
        "Bug Reports": "https://github.com/instana/synthetic-synctl/issues",
        "Source": "https://github.com/instana/synthetic-synctl",
    },
)
