from tasks.generic import GenericTask
import json
import time

# Batch update locations based on json array of location definitions
class BatchUpdateLocation(GenericTask):

  def run(self):
    # Get list of location definitions
    while True:
      data = self.json_menu()
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
