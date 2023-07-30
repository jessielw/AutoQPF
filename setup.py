import os

from setuptools import setup

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: MacOS",
    "Operating System :: POSIX :: Linux",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
]

with open(os.path.join(os.path.dirname(__file__), "README.md")) as fd:
    ext_long_desc = fd.read()

setup(
    name="AutoQPF",
    version="0.1.6",
    description="Generates QPF frame time codes to be used with x264/x265",
    long_description=ext_long_desc,
    long_description_content_type="text/markdown",
    url="https://github.com/jlw4049/AutoQPF",
    author="Jessie Wilson",
    author_email="jessielw4049@gmail.com",
    license="MIT",
    classifiers=classifiers,
    keywords="AutoQPF",
    packages=["auto_qpf"],
    install_requires=["pymediainfo"],
)
