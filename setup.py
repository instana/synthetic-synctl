import codecs
import re

from setuptools import setup, find_packages

INSTALL_REQUIRES = [
    "requests>=2.27.0",
]

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
    name="synctl",
    version=find_version("synctl/__version__.py"),
    description="Instana Synthetic CLI",
    long_description=read("DESCRIPTION.md"),
    long_description_content_type="text/markdown",
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
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.12",
        "Environment :: Console",
    ],
    packages=find_packages(include=["synctl"]),
    entry_points={
        "console_scripts": [
            "synctl = synctl.cli:main"
            ]
        },
    tests_require=["pytest"],
    project_urls={
        "Bug Reports": "https://github.com/instana/synthetic-synctl/issues",
        "Source": "https://github.com/instana/synthetic-synctl",
        'Documentation': 'https://github.com/instana/synthetic-synctl#readme',
    },
)
