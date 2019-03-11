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
    while True:
      data = self.json_menu()
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
