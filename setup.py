import pathlib
from setuptools import setup

ROOT = pathlib.Path(__file__).parent
README = (ROOT / "README.md").read_text()

setup(
    name='paramap',
    version='0.1.5',
    description='Easily map flat dictionaries to object representations',
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/GrayTable/paramap',
    author='Kamil Biel',
    author_email='hello@kamilbiel.com',
    license='MIT',
    packages=['paramap'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    zip_safe=False
)
