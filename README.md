# flask-arch
[![Build Status](https://app.travis-ci.com/ToraNova/flask-arch.svg?branch=master)](https://app.travis-ci.com/github/ToraNova/flask-arch)

A project for modular architecture using [flask](https://flask.palletsprojects.com/en/2.0.x/)

## Installation
Recommend to do this in a virtual environment!

### Latest Version
```bash
pip install git+git://github.com/toranova/flask-arch.git@master
```
### pypi Release
```bash
pip install flask-arch
```

## Testing the current build
```bash
runtest.sh
```

## Examples
* Barebones
    1. [Simple architecture](examples/arch_basic/__init__.py)
* Authentication
    1. [Minimal Login (No Database)](examples/auth_basic/__init__.py)
    2. [With SQLAlchemy](examples/auth_database/__init__.py)
