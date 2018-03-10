from distutils.core import setup
import py2exe

setup(options = {"py2exe": {"bundle_files": 2}},
      windows = [{"script": "Sudoku.py",
                  "icon_resources": [(1, "Files/logo.ico")],
                  "dest_base": "Sudoku"}])
