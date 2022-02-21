# flask-arch
[![Build Status](https://travis-ci.org/ToraNova/viauth.svg?branch=master)](https://travis-ci.org/ToraNova/viauth)

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

* Authentication
    1. [Minimal Login (No Database)](examples/basic/__init__.py)
    2. [With SQLAlchemy](examples/persistdb/__init__.py)
    3. [Custom Userclass](examples/cuclass/__init__.py)
