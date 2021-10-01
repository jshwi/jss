"""
setup
=====

``setuptools`` for package.
"""
from setuptools import setup, find_packages

with open("README.rst") as file:
    README = file.read()


setup(
    name="jss",
    version="0.1.0",
    description="A Flask web application",
    long_description=README,
    long_description_content_type="text/x-rst",
    author="Stephen Whitlock",
    author_email="stephen@jshwisolutions.com",
    url="https://github.com/jshwi/jss",
    license="MIT",
    platforms="GNU/Linux",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    keywords=["python3.8", "flask", "webapp"],
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "appdirs==1.4.4",
        "click==8.0.1",
        "email-validator==1.1.3",
        "environs==9.3.3",
        "flask==2.0.1",
        "flask-bootstrap==3.3.7.1",
        "flask-caching==1.10.1",
        "flask-debugtoolbar==0.11.0",
        "flask-login==0.5.0",
        "flask-mail==0.9.1",
        "flask-migrate==3.1.0",
        "flask-misaka==1.0.0",
        "flask-moment==1.0.2",
        "flask-pagedown==0.4.0",
        "flask-sqlalchemy==2.5.1",
        "flask-static-digest==0.2.1",
        "flask-wtf==0.15.1",
        "gunicorn==20.1.0",
        "itsdangerous==2.0.1",
        "psycopg2==2.9.1",
        "pyjwt==2.1.0",
        "redis==3.5.3",
        "rq==1.10.0",
        "sqlalchemy-utils==0.37.8",
        "werkzeug==2.0.1",
    ],
    python_requires=">=3.8",
)
