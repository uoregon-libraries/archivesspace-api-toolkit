from tasks.generic import GenericTask
import json

# Batch create top containers based on json array of top container definitions
class BatchCreateTopContainer(GenericTask):

  def run(self):
    # Get repository ID
    while True:
      id = self.repo_menu()
      if id:
        break

    # Get list of top container definitions
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

    url = "/repositories/%s/top_containers" % (id)

    for tc in data:
      # Create top container
      super()._call(url, "post", tc)

  # Menu prompt
  def prompt(self):
    return "Batch create top containers"

  # Query user for repository ID
  def repo_menu(self):
    print("Enter the repository ID to create the top containers in:")
    print("ie: 5")
    print("")
    try:
      id = input(">> ")
    except EOFError:
      return None
    return id if super()._confirm("Confirm ID: %s" % id) else None

  # Query user for JSON data file
  def json_menu(self):
    print("Enter the path to your json file:")
    print("ie: /data.json")
    print("")
    try:
      data = input(">> ")
    except EOFError:
      return None
    return data if super()._confirm("Confirm path: %s" % data) else None
