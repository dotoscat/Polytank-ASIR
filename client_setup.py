from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = ["pyglet", "polytanks", "codecs", "encodings", "selectors"],
    excludes = ["tkinter", "PyQt5", "PIL", "setuptools"]
    , include_files="assets")

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('main.py', base=base, targetName = 'cliente.exe')
]

setup(name='polytanks-cliente',
      version = '1.0',
      description = 'Cliente de Polytanks',
      options = dict(build_exe = buildOptions),
      executables = executables)
