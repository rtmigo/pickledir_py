from importlib.machinery import SourceFileLoader
from pathlib import Path
from setuptools import setup

constants = SourceFileLoader('constants',
                             'pickledir/_constants.py').load_module()

setup(
    name="pickledir",
    version=constants.__dict__['__version__'],
    author="Artёm IG",
    author_email="ortemeo@gmail.com",
    url='https://github.com/rtmigo/pickledir_py#readme',

    install_requires=[],
    packages=['pickledir'],

    description="File-based key-value storage. Keys are strings, values are "
                "objects pickle serializable.",

    keywords="cache pickle file directory".split(),

    long_description=(Path(__file__).parent / 'README.md').read_text(),
    long_description_content_type='text/markdown',

    license='MIT',

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
    ],
)
