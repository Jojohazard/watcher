from setuptools import setup, Extension
from Cython.Build import cythonize

extensions = [
    Extension("watcher_main", ["src/main.py"]),
]

setup(
    name="watcher",
    ext_modules=cythonize(
        extensions,
        compiler_directives={"language_level": "3"},
    ),
)
