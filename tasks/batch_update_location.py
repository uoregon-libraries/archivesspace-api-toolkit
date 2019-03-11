from tasks.generic import GenericTask
import json
import time

# Batch update locations based on json array of location definitions
class BatchUpdateLocation(GenericTask):

  def run(self):
    # Get list of location definitions
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

    for location in data:
      # Update location from url definition
      try:
        url = location['uri']
        super()._call(url, 'post', location)
      except KeyError:
        print("element 'uri' not defined in %s" % (location))

  # Menu prompt
  def prompt(self):
    return "Batch update locations"
