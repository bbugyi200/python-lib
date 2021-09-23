from functools import partial

# For accessing modules as attributes of 'bugyi' (e.g. 'bugyi.logging').
#
# DEPRECATED: Use `from bugyi import <MODULE>` or `from bugyi.<MODULE> import
# <NAME>` instead.
from . import debug, io, logging, xdg
from .cli import ArgumentParser
from .core import (
    catch,
    create_dir,
    efill,
    ewrap,
    mkfifo,
    secret,
    shell,
    signal,
)
from .meta import deprecated
from .subprocess import StillAliveException, create_pidfile
from .tools import notify, xkey, xtype


ArgumentParser = deprecated(
    ArgumentParser,
    "Importing 'ArgumentParser' directly from the 'bugyi' package is"
    " deprecated. Use 'from bugyi import cli' instead.",
)

_CORE_WARNING = (
    "Accessing / Importing the '{0}' function directly from the 'bugyi'"
    " package is deprecated. Use 'from bugyi.core import {0}' instead.".format
)
catch = deprecated(catch, _CORE_WARNING("catch"))
create_dir = deprecated(create_dir, _CORE_WARNING("create_dir"))
efill = deprecated(efill, _CORE_WARNING("efill"))
ewrap = deprecated(ewrap, _CORE_WARNING("ewrap"))
mkfifo = deprecated(mkfifo, _CORE_WARNING("mkfifo"))
secret = deprecated(secret, _CORE_WARNING("secret"))
shell = deprecated(shell, _CORE_WARNING("shell"))
signal = deprecated(signal, _CORE_WARNING("signal"))

_SUBPROCESS_WARNING = (
    "Importing '{}' directly from the 'bugyi' package is deprecated. Use"
    " 'from bugyi import subprocess as bsp' instead.".format
)
create_pidfile = deprecated(
    create_pidfile, _SUBPROCESS_WARNING("create_pidfile")
)

_TOOLS_WARNING = (
    "Importing '{0}' directly from the 'bugyi' package is deprecated. Use"
    " 'from bugyi.tools import {0}' instead.".format
)
notify = deprecated(partial(notify, up=1), _TOOLS_WARNING("notify"))
xkey = deprecated(xkey, _TOOLS_WARNING("xkey"))
xtype = deprecated(xtype, _TOOLS_WARNING("xtype"))
