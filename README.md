# ArchivesSpace API Toolkit
A CLI tool built to wrap the ArchivesSpace API in a user friendly menu.

## Users
### Setup
Currently, this tool is only built for Windows. If you are a Mac or Linux user, you can follow the developers `Setup` and `Running Without Compiling` instructions below
* Download latest build from [Here](https://github.com/uoregon-libraries/archivesspace-api-toolkit/releases/latest).
* Extract `build.zip` to wherever you want to run from
* Working from inside `build/exe.win-amd64-3.6`, copy `settings.ini.example` to `settings.ini` and fill in your aspace credentials
* Look in `examples` for example input files for each command

### Using the Toolkit
After setting up your Aspace credentials correctly, running `app.exe` will present you with a basic command line interface.
If you are receiving immediate crashes or error messages, make sure your `settings.ini` file is correct and well formatted

`>>` indicates the application is waiting for your input.
`#)` indicates an option, input the value left of the parens to select that option
`Y/(N)` or `(Y)/N` indicates a yes or no response. The parenthesized value is the default if nothing is entered. A `Yes` response is anything that starts with a `y` case-insensitive, everything else is a `No`.
The toolkit can be ran as `app.exe -y` or `app.exe --yes` to skip some of the more annoying `Y/N` questions, such as confirming paths.

All inputs will present you with a short instruction on what to input and give an example value.
When asked for a json file, refer to the corresponding example json to build an input file, then give an absolute or relative (to app.exe) path to your input file.
The easiest way to accomplish this is to create a file called `data.json` next to `app.exe` and always input the example: `data.json`

After all requested data is input, task will immediately begin and output a trace of the network traffic between the app and the Aspace API.

`<` indicates traffic out to Aspace
`>` indicates traffic in to the app. This is what you will be most interested in.
The last line of traffic in will likely be your output. It can be helpful to run your output through a beautifier like these: [JSON](https://jsonformatter.org/) | [XML](https://jsonformatter.org/xml-formatter)
Certain tasks will also dump your output to the `out` directly in a useful format.

#### Tasks
`1) Enter API endpoint and JSON file` Is a base case, where you can input a free form url to be prepended to your Aspace instance URL.
With this option, any arbitrary API query can be ran
See [API Docs](https://archivesspace.github.io/archivesspace/api/#routes-by-uri)

`2) Batch create top containers` Is a repetitive application of the [`POST /repositories/:repo_id/top_containers`](https://archivesspace.github.io/archivesspace/api/#create-a-top-container) endpoint

`3) Batch export top containers` Does a search for all top containers in the given repository, then is a repetitive application of the [`GET /repositories/:repo_id/top_containers/:id`](https://archivesspace.github.io/archivesspace/api/#get-a-top-container-by-id) endpoint. Data is dumped to `out/:id.json`

`4) Batch update top containers` Is a repetitive application of the [`POST /repositories/:repo_id/top_containers/:id`](https://archivesspace.github.io/archivesspace/api/#update-a-top-container) endpoint

`5) Batch export resources as EAD` Is a repetitive application of the [`GET /repositories/:repo_id/resource_descriptions/:id.xml`](https://archivesspace.github.io/archivesspace/api/#get-an-ead-representation-of-a-resource204) endpoint. Data is dumped to `out/:id.xml`

`6) Batch export resources as EAD for ArchivesWest` builds on `5)` by preparing the exported EAD for ingest into ArchivesWest. Only the following XML elements are kept: `ead/eadheader, ead/control, ead/archdesc/did, ead/archdesc/accessrestrict, ead/archdesc/controlaccess`. Then `archdesc/did/unittitle` is updated to link back to ArchivesSpace, `archdesc/dsc/c01/did/unittitle` is re-created to add another link in the archival object, finally `archdesc/accessrestrict` is searched for an ending paragraph that contains a link to the resource, if the last paragraph does not contain such a link a new paragraph is appended

`7) Batch update resources` Is a repetitive application of the [`POST /repositories/:repo_id/resources/:id`](https://archivesspace.github.io/archivesspace/api/#update-a-resource) endpoint

### Logging
All traffic in and out of the app is recorded to `app.log`. This can be extremely helpful in debugging or retrieving accidentally deleted resources.

## Developers

### Setup
- Python 3, <3.7 if using cx_freeze to compile
- Setup a virtual environment: `python -m virtualenv venv`
- Start your virtualenv
  - Windows
    - cmd - `venv/Scripts/activate.bat`
    - powershell - `venv/Scripts/activate.ps1`
  - Linux/Mac: `source venv/Scripts/activate`
- Install module requirements: `make setup` or `pip install -r requirements.txt`
- Copy `settings.ini.example` to `settings.ini` and fill out

### Compile
Compilation is recommended for building for users that are not comfortable setting up virtual environment or Python and packages.

Compilation uses [cx_freeze](https://anthony-tuininga.github.io/cx_Freeze/) to build a distributable executable and library files. cx_freeze only builds for the platform you're compiling on. So, if your users are using Windows, build on Windows

- From your venv: `make compile` or `python setup.py build`
- Compilation is in `build/` directory
- cx_freeze will copy in `settings.ini.example` for the user to rename and fill out

### Running Without Compiling
ArchivesSpace API Toolkit works just fine without compiling:
`python app.py`

### Development
#### Design
Everything is based around a CLI menu and Tasks. The top-level menu is generated in `/app.py` where Tasks are added to a menu list. A task is chosen from the menu and executed. Once the task completes the user is dumped back to the main menu

Tasks are defined in `/tasks/` and all inherit from the abstract base `GenericTask` class. `GenericTask` provides an abstract definition for `run()` and `prompt()` to be overwritten by child Tasks. `run()` defines sub-menus, and the action the task performs. `prompt()` is a simple string that is displayed from the main menu. `GenericTask` also provides a couple helper functions that most Tasks will need. `_confirm()` generates a confirmation dialog and returns T/F. `_call()` provides a simple way to call the ArchivesSpace API client with file and stream logging.

#### Dependencies
Remember to do all development in a virtual environment. Once you've installed new packages, or deleted old ones, run `make freeze` or `pip freeze > requirements.txt` to freeze dependencies for the project.
