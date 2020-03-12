# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.0.4] - 2020-03-12
### Added
- Retroactively added a changelog, even though this project isn't ready

### Changed
- Improved CSS by reducing redundant elements via better selectors; unfortunately, some redundancy could not be removed

## [0.0.3] - 2020-03-03
### Fixed
- For `send_file()`, I incorrectly used `app` (instance of `flask.Flask`) instead of `flask`; fixed by importing `from flask`
- The first `subprocess.Popen()` call is now waited
- ImageMagick `convert` was missing a `-` argument for receiving input from `pipe`

## [0.0.2] - 2020-02-22
### Changed
- Added empty directories with contents to be ignored
    - `previews` will now contain all preview scans
    - Likewise, `scans` will contain all full scans
- `scan()` has less redundancy; common options are moved at the root of the conditional (`else: ... if 'scan in request.form:`)
- `run_command()` now accepts `target` and `fmt` for arguments; this makes `scan()` more modular

### Fixed
- The Preview button is now disabled if ImageMagick `convert` is not detected
- `--mode` should now be in-line with `'Color'`; because scans by default are in black & white, this argument should only appear if selected by the user

## [0.0.1] - 2020-02-20
### Added
- Initial version
