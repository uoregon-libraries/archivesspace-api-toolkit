# ArchivesSpace API Toolkit
A CLI tool built to wrap the ArchivesSpace API in a user friendly menu.

## Setup
- Python 3, <3.7 if using cx_freeze to compile
- Setup a virtual environment: `python -m virtualenv venv`
- Start your virtualenv
  - Windows
    - cmd - `venv/Scripts/activate.bat`
    - powershell - `venv/Scripts/activate.ps1`
  - Linux/Mac: `source venv/Scripts/activate`
- Install module requirements: `make setup` or `pip install -r requirements.txt`
- Copy `settings.ini.example` to `settings.ini` and fill out

## Compile
Compilation is recommended for building for users that are not comfortable setting up virtual environment or Python and packages.

Compilation uses [cx_freeze](https://anthony-tuininga.github.io/cx_Freeze/) to build a distributable executable and library files. cx_freeze only builds for the platform you're compiling on. So, if your users are using Windows, build on Windows

- From your venv: `make compile` or `python setup.py build`
- Compilation is in `build/` directory
- cx_freeze will copy in `settings.ini.example` for the user to rename and fill out

## Running Without Compiling
ArchivesSpace API Toolkit works just fine without compiling:
`python app.py`

## Development
### Design
Everything is based around a CLI menu and Tasks. The top-level menu is generated in `/app.py` where Tasks are added to a menu list. A task is chosen from the menu and executed. Once the task completes the user is dumped back to the main menu

Tasks are defined in `/tasks/` and all inherit from the abstract base `GenericTask` class. `GenericTask` provides an abstract definition for `run()` and `prompt()` to be overwritten by child Tasks. `run()` defines sub-menus, and the action the task performs. `prompt()` is a simple string that is displayed from the main menu. `GenericTask` also provides a couple helper functions that most Tasks will need. `_confirm()` generates a confirmation dialog and returns T/F. `_call()` provides a simple way to call the ArchivesSpace API client with file and stream logging.

### Dependencies
Remember to do all development in a virtual environment. Once you've installed new packages, or deleted old ones, run `make freeze` or `pip freeze > requirements.txt` to freeze dependencies for the project.
