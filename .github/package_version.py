#!/usr/bin/env python3

from importlib.machinery import SourceFileLoader
constants = SourceFileLoader(
  'constants',
  'pickledir/_constants.py').load_module()
print(constants.__dict__['__version__'])
