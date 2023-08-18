import configparser
import functools
import glob
import io
import itertools
import multiprocessing.pool
import os
import platform
import re
import setuptools
import setuptools.extension
import subprocess
import sys
from distutils.command.clean import clean as _clean
from distutils.errors import CompileError
from distutils.util import get_platform
from setuptools.command.build_clib import build_clib as _build_clib
from setuptools.command.build_ext import build_ext as _build_ext
from setuptools.command.sdist import sdist as _sdist
from setuptools.extension import Extension

try:
    from Cython.Build import cythonize
except ImportError as err:
    cythonize = err

try:
    import ngsreads.lib
except ImportError as err:
    ngsreads = err

# --- Constants -----------------------------------------------------------------

SETUP_FOLDER = os.path.relpath(os.path.realpath(os.path.join(__file__, os.pardir)))


# --- Utils ------------------------------------------------------------------

def _eprint(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)

def _patch_osx_compiler(compiler, machine):
    # On newer OSX, Python has been compiled as a universal binary, so
    # it will attempt to pass universal binary flags when building the
    # extension. This will not work because the code makes use of CPU
    # specific SIMD extensions.
    for tool in ("compiler", "compiler_so", "linker_so"):
        flags = getattr(compiler, tool)
        i = next((i for i in range(1, len(flags)) if flags[i-1] == "-arch" and flags[i] != machine), None)
        if i is not None:
            flags.pop(i)
            flags.pop(i-1)

def _detect_target_machine(platform):
    if platform == "win32":
        return "x86"
    return platform.rsplit("-", 1)[-1]

def _detect_target_cpu(platform):
    machine = _detect_target_machine(platform)
    if re.match("^mips", machine):
        return "mips"
    elif re.match("^(aarch64|arm64)$", machine):
        return "aarch64"
    elif re.match("^arm", machine):
        return "arm"
    elif re.match("(x86_64)|(x86)|(AMD64|amd64)|(^i.86$)", machine):
        return "x86"
    elif re.match("^(powerpc|ppc)", machine):
        return "ppc"
    return None

def _detect_target_system(platform):
    if platform.startswith("win"):
        return "windows"
    elif platform.startswith("macos"):
        return "macos"
    elif platform.startswith("linux"):
        return "linux_or_android"
    elif platform.startswith("freebsd"):
        return "freebsd"
    return None


# --- Commands ------------------------------------------------------------------

class sdist(_sdist):
    """A `sdist` that generates a `pyproject.toml` on the fly."""

    def run(self):
        # build `pyproject.toml` from `setup.cfg`
        c = configparser.ConfigParser()
        c.add_section("build-system")
        c.set("build-system", "requires", str(self.distribution.setup_requires))
        c.set("build-system", "build-backend", '"setuptools.build_meta"')
        with open("pyproject.toml", "w") as pyproject:
            c.write(pyproject)
        # run the rest of the packaging
        _sdist.run(self)


class build_ext(_build_ext):
    """A `build_ext` that disables optimizations if compiled in debug mode."""

    def initialize_options(self):
        _build_ext.initialize_options(self)
        self.target_machine = None
        self.target_system = None
        self.target_cpu = None

    def finalize_options(self):
        _build_ext.finalize_options(self)
        # fix detection of CPU count for parallel build
        if self.parallel is not None:
            self.parallel = int(self.parallel)
        if self.parallel == 0:
            self.parallel = os.cpu_count()
        # detect platform options
        self.target_machine = _detect_target_machine(self.plat_name)
        self.target_system = _detect_target_system(self.plat_name)
        self.target_cpu = _detect_target_cpu(self.plat_name)
        # transfer arguments to the build_clib method
        self._clib_cmd = self.get_finalized_command("build_clib")
        self._clib_cmd.debug = self.debug
        self._clib_cmd.force = self.force
        self._clib_cmd.verbose = self.verbose
        self._clib_cmd.define = self.define
        self._clib_cmd.include_dirs = self.include_dirs
        self._clib_cmd.compiler = self.compiler
        self._clib_cmd.parallel = self.parallel
        self._clib_cmd.plat_name = self.plat_name
        self._clib_cmd.target_machine = self.target_machine
        self._clib_cmd.target_system = self.target_system
        self._clib_cmd.target_cpu = self.target_cpu


    # --- Build code ---

    def build_extension(self, ext):
        # show the compiler being used
        _eprint(f"building {ext.name} for {self.plat_name} with {self.compiler.compiler_type} compiler")
        # add debug symbols if we are building in debug mode
        if self.debug:
            ext.define_macros.append(("NGSR_DEBUG", 1))
            if self.compiler.compiler_type in {"unix", "cygwin", "mingw32"}:
                ext.extra_compile_args.append("-g")
            elif self.compiler.compiler_type == "msvc":
                ext.extra_compile_args.append("/Z7")
            if sys.implementation.name == "cpython":
                ext.define_macros.append(("CYTHON_TRACE_NOGIL", 1))
        else:
            ext.define_macros.append(("CYTHON_WITHOUT_ASSERTIONS", 1))
        # remove universal binary CFLAGS from the compiler if any
        if self.target_system == "macos":
            _patch_osx_compiler(self.compiler, self.target_machine)
        # add core library source files
        if isinstance(ngsreads, ImportError):
            raise RuntimeError("failed to import ngsreads") from ngsreads
        ext.include_dirs.insert(0, os.fspath(ngsreads.lib.get_include()))
        # ext.sources.extend(os.fspath(x) for x in ngsreads.lib.get_sources())
        # build the extension as normal
        _build_ext.build_extension(self, ext)

    def build_extensions(self):
        # check `cythonize` is available
        if isinstance(cythonize, ImportError):
            raise RuntimeError("Cython is required to run `build_ext` command") from cythonize
        # check `ngsreads` is available
        if isinstance(ngsreads, ImportError):
            raise RuntimeError("Failed to import ngsreads") from ngsreads

        # compile the C library if not done already
        if not self.distribution.have_run.get("build_clib", False):
            self._clib_cmd.run()

        # use debug directives with Cython if building in debug mode
        cython_args = {
            "include_path": [os.fspath(ngsreads.lib.get_include()), "include", SETUP_FOLDER],
            "nthreads": self.parallel,
            "compiler_directives": {
                "cdivision": True,
                "nonecheck": False,
            },
            "compile_time_env": {
                "SYS_IMPLEMENTATION_NAME": sys.implementation.name,
                "SYS_VERSION_INFO_MAJOR": sys.version_info.major,
                "SYS_VERSION_INFO_MINOR": sys.version_info.minor,
                "SYS_VERSION_INFO_MICRO": sys.version_info.micro,
                "TARGET_CPU": self.target_cpu,
                "TARGET_SYSTEM": self.target_system,
                "DEFAULT_BUFFER_SIZE": io.DEFAULT_BUFFER_SIZE,
            }
        }
        if self.force:
            cython_args["force"] = True
        if self.debug:
            cython_args["annotate"] = True
            cython_args["compiler_directives"]["cdivision_warnings"] = True
            cython_args["compiler_directives"]["warn.undeclared"] = True
            cython_args["compiler_directives"]["warn.unreachable"] = True
            cython_args["compiler_directives"]["warn.maybe_uninitialized"] = True
            cython_args["compiler_directives"]["warn.unused"] = True
            cython_args["compiler_directives"]["warn.unused_arg"] = True
            cython_args["compiler_directives"]["warn.unused_result"] = True
            cython_args["compiler_directives"]["warn.multiple_declarators"] = True
        else:
            cython_args["compiler_directives"]["boundscheck"] = False
            cython_args["compiler_directives"]["wraparound"] = False

        # cythonize the extensions
        self.extensions = cythonize(self.extensions, **cython_args)
        for ext in self.extensions:
            ext._needs_stub = False

        # build the extensions as normal
        _build_ext.build_extensions(self)


class clean(_clean):
    """A `clean` that removes intermediate files created by Cython."""

    def run(self):
        source_dir = os.path.join(os.path.dirname(__file__), "ngsreads")
        patterns = ["*.html"]
        if self.all:
            patterns.extend(["*.so", "*.c", "*.cpp"])
        for pattern in patterns:
            for file in glob.glob(os.path.join(source_dir, pattern)):
                _eprint("removing {!r}".format(file))
                os.remove(file)
        _clean.run(self)

# --- Setup ---------------------------------------------------------------------

setuptools.setup(
    ext_modules=[
        Extension(
            "ngsreads.align.bwa",
            language="c++",
            sources=[
                os.path.join("vendor", "bwa", "bntseq.c"),
                os.path.join("vendor", "bwa", "bwt.c"),
                os.path.join("vendor", "bwa", "utils.c"),
            ],
            include_dirs=[
                "include",
                SETUP_FOLDER],
            libraries=[],
        ),
    ],
    cmdclass={
        "sdist": sdist,
        "build_ext": build_ext,
        "clean": clean,
    },
)