from tasks.generic import GenericTask
import json
import time

# Batch dump top containers based on repository number
class BatchExportTopContainer(GenericTask):

  def run(self):
    # Get repository ID
    while True:
      id = self.repo_menu()
      if id:
        break

    export_time = time.strftime("%Y-%m-%d-%H%M%S")

    # Get list of top container definitions
    top_containers = []
    cur_page = last_page = 1
    while cur_page <= last_page:
      url = "/repositories/%s/top_containers?page=%i" % (id, cur_page)
      data = super()._call(url, "get", None)
      data = data.json()
      top_containers += data["results"]
      last_page = data["last_page"]
      cur_page += 1
      with open("out/%s.json" % (export_time), mode="w", encoding="utf-8") as file:
        file.write(json.dumps(top_containers, indent=2, sort_keys=True))
        file.close()

  # Menu prompt
  def prompt(self):
    return "Batch export top containers"

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
    print("ie: data.json")
    print("")
    try:
      data = input(">> ")
    except EOFError:
      return None
    return data if super()._confirm("Confirm path: %s" % data) else None
