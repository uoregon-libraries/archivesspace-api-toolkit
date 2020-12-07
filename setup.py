from cx_Freeze import setup, Executable

buildOptions = {
  "includes": ["idna.idnadata", "Queue.multiprocessing"],
  "include_files": ["settings.ini.example", "README.md", "out"],
}
setup(
  name = "aspace",
  version = "1.3.1",
  description = "",
  options = {
    "build_exe": buildOptions,
  },
  executables = [Executable("app.py")]
)
