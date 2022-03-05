from setuptools import find_packages, setup

_version = '0.0.6'

setup(
    name='flask-arch',
    version=_version,
    description='a modular architecture project for bootstrapping on the flask web development microframework',
    packages=find_packages(),
    author='Chia Jason',
    author_email='chia_jason96@live.com',
    url='https://github.com/toranova/flask-arch/',
    download_url='https://github.com/ToraNova/flask-arch/archive/refs/tags/v%s.tar.gz' % _version,
    license='MIT',
    include_package_data=True,
    zip_safe=False,
    keywords = ['Flask'],
    install_requires=[
        'flask',
        'flask-login',
        'sqlalchemy',
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
