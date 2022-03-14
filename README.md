# flask-arch
[![Build Status](https://app.travis-ci.com/ToraNova/flask-arch.svg?branch=master)](https://app.travis-ci.com/github/ToraNova/flask-arch)

A project for modular architecture using [flask](https://flask.palletsprojects.com/en/2.0.x/)

## installation
recommend to do this in a virtual environment!

### latest version
```bash
pip install git+git://github.com/toranova/flask-arch.git@master
```
### pypi release
```bash
pip install flask-arch
```

## testing the current build
```bash
runtest.sh
```

## examples
* barebones
    1. [simple architecture](examples/arch_basic/__init__.py)
* authentication
    1. [minimal login (no database)](examples/auth_basic/__init__.py)
    2. [with SQLAlchemy](examples/auth_database/__init__.py)
    3. [email account](examples/email_account/__init__.py)
    4. [user roles](examples/auth_withrole/__init__.py)
* starters
    1. [email login with roles + upload/download](examples/starter_1/__init__.py)
