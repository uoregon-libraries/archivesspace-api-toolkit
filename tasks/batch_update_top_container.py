from tasks.generic import GenericTask
import json
import time

# Batch update top containers based on json array of top container definitions
class BatchUpdateTopContainer(GenericTask):

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
        with open(json_file, mode="r", encoding="utf-8") as file:
          data = json.loads(file.read())
      except FileNotFoundError:
        print("File %s not found" % json_file)
        print("")
        data = None
      except json.JSONDecodeError:
        print("Invalid JSON in %s" % json_file)
      if data:
        break

    for top_container in data:
      # Update top container from url definition
      try:
        url = top_container['uri']
        super()._call(url, 'post', top_container)
      except KeyError:
        print("element 'uri' not defined in %s" % (top_container))

  # Menu prompt
  def prompt(self):
    return "Batch update top containers"

  # Query user for repository ID
  def repo_menu(self):
    print("Enter the repository ID to update in:")
    print("ie: 5")
    print("")
    try:
      id = input(">> ")
    except EOFError:
      return None
    return id if super()._confirm("Confirm ID: %s" % id) else None
