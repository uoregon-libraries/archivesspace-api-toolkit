from cx_Freeze import setup, Executable

buildOptions = {
  "includes": ["idna.idnadata", "Queue.multiprocessing"],
  "include_files": ["settings.ini.example", "README.md"],
}
setup(
  name = "aspace",
  version = "0.1",
  description = "",
  options = {
    "build_exe": buildOptions,
  },
  executables = [Executable("app.py")]
)
