# Changelog for `bugyi.lib`

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog], and this project adheres to
[Semantic Versioning].

[Keep a Changelog]: https://keepachangelog.com/en/1.0.0/
[Semantic Versioning]: https://semver.org/


## [Unreleased](https://github.com/bbugyi200/python-lib/compare/0.11.0...HEAD)

No notable changes have been made.


## [0.11.0](https://github.com/bbugyi200/python-lib/compare/0.10.0...0.11.0) - 2021-12-20

### Removed

* **BREAKING CHANGE**: Sync with cc-python version `v2021.12.20` (drops Python3.7 support).


## [0.10.0](https://github.com/bbugyi200/python-lib/compare/0.9.0...0.10.0) - 2021-12-11

### Removed

* Remove `bugyi.sh` bash library.


## [0.9.0](https://github.com/bbugyi200/python-lib/compare/0.8.0...0.9.0) - 2021-12-11

### Added

* Add `bugyi.sh` bash library.


## [0.8.0](https://github.com/bbugyi200/python-lib/compare/0.7.0...0.8.0) - 2021-11-24

### Changed

* Use python-result library instead of `lib.result` module.


## [0.7.0](https://github.com/bbugyi200/python-lib/compare/0.6.1...0.7.0) - 2021-11-23

### Changed

* The `shell.*_popen()` functions now return a Process object.


## [0.6.1](https://github.com/bbugyi200/python-lib/compare/0.6.0...0.6.1) - 2021-10-04

### Fixed

* Fix `_path_to_module()` when `sys.path` contains `Path` objects.


## [0.6.0](https://github.com/bbugyi200/python-lib/compare/0.5.0...0.6.0) - 2021-10-01

### Added

* Add `io.colors` class.


## [0.5.0](https://github.com/bbugyi200/python-lib/compare/0.4.0...0.5.0) - 2021-09-28

### Changed

* Improve the `io.get_secret()` function.

### Miscellaneous

* Increase test coverage to >=30%.


## [0.4.0](https://github.com/bbugyi200/python-lib/compare/0.3.0...0.4.0) - 2021-09-26

### Removed

* Removed the `lib.cli` module, which has been migrated to the [clap](https://github.com/bbugyi200/clap) package.


## [0.3.0](https://github.com/bbugyi200/python-lib/compare/0.2.1...0.3.0) - 2021-09-25

### Changed

* Integrated the `logutils` package into this package.


## [0.2.1](https://github.com/bbugyi200/python-lib/compare/0.2.0...0.2.1) - 2021-09-25

### Miscellaneous

* Added `py.typed` file so mypy works with this package.


## [0.2.0](https://github.com/bbugyi200/python-lib/compare/0.1.0...0.2.0) - 2021-09-25

### Added

* Initialized package with initial module files (e.g. `cli.py`, `errors.py`, `meta.py`).


## [0.1.0](https://github.com/bbugyi200/python-lib/releases/tag/0.1.0) - 2021-09-23

### Miscellaneous

* First release.
