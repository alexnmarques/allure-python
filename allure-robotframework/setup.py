import os,sys
from setuptools import setup
from pkg_resources import require, DistributionNotFound, VersionConflict

PACKAGE = "allure-robotframework"
VERSION = "2.2.4b1"

classifiers = [
    'Development Status :: 4 - Beta',
    'Framework :: Robot Framework',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Topic :: Software Development :: Quality Assurance',
    'Topic :: Software Development :: Testing',
]

install_requires = [
    "robot>=3.0.2",
    "six>=1.9.0",
    "allure-python-commons==2.2.4b1"
]


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def main():
    setup(
        name=PACKAGE,
        version=VERSION,
        description="Allure robot framework integration",
        url="https://github.com/allure-framework/allure-python",
        author="QAMetaSoftware, Stanislav Seliverstov",
        author_email="sseliverstov@qameta.io",
        license="Apache-2.0",
        classifiers=classifiers,
        keywords="allure reporting robot framework",
        long_description=read('README.rst'),
        packages=["allure_robotframework"],
        package_dir={"allure_robotframework": "src"},
        install_requires=install_requires
    )

if __name__ == '__main__':
    main()

