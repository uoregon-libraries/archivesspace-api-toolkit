from tasks.generic import GenericTask
import json

# Batch export resources in EAD format. XML or PDF
class BatchExportEAD(GenericTask):

  def run(self):
    # Get repository ID
    while True:
      repo_id = self.repo_menu()
      if id:
        break

    while True:
      options = self.options_menu()
      if options:
        break

    data = None
    while True:
      json_file = self.json_menu()
      try:
        with open(json_file) as file:
          data = json.loads(file.read())
      except FileNotFoundError:
        print("File %s not found" % json_file)
        print("")
        data = None
      except json.JSONDecodeError:
        print("Invalid JSON in %s" % json_file)
      if data:
        break

    for resource_id in data:
      url = "/repositories/%s/resource_descriptions/%s.xml?include_unpublished=%s&include_daos=%s&numbered_cs=%s&ead3=%s"\
            % (repo_id, resource_id, options[0], options[1], options[2], options[3])
      # Export resource
      resp = super()._call(url, "get", None)
      with open("out/%s.xml" % (resource_id), "w") as file:
        file.write(resp.text)
        file.close()

  # Menu prompt
  def prompt(self):
    return "Batch export resources"

  # Query user for repository ID
  def repo_menu(self):
    print("Enter the repository ID to export from:")
    print("ie: 5")
    print("")
    try:
      id = input(">> ")
    except EOFError:
      return None
    return id if super()._confirm("Confirm ID: %s" % id) else None

  # Query user for export format
  def options_menu(self):
    unpublished = super()._confirm("Include unpublished records?", True)
    daos = super()._confirm("Include digital objects in dao tags?", True)
    tags = super()._confirm("Use numbered tags in ead?", True)
    ead = super()._confirm("Export using EAD3 schema?", True)
    return [unpublished, daos, tags, ead]

  # Query user for JSON data file
  def json_menu(self):
    print("Enter the path to your json file:")
    print("ie: data.json")
    print("")
    try:
      data = input(">> ")
    except EOFError:
      return None
    return data if super()._confirm("Confirm path: %s" % data) else None
