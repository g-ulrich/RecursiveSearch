
from distutils.core import setup

import py2exe
setup(options = {"py2exe": { "excludes": ["sqlite3", "tkinter", "scipy", "numpy", "pandas"]}},
      console=['app.py'])