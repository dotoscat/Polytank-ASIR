from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = ["pyglet", "polytanks", "codecs", "encodings", "asyncio"],
    excludes = ["tkinter", "PyQt5", "PIL", "setuptools"])

base = 'Console'

executables = [
    Executable('server.py', base=base)
]

setup(name='polytanks-server',
      version = '1.0',
      description = 'Servidor de Polytanks',
      options = dict(build_exe = buildOptions),
      executables = executables)
