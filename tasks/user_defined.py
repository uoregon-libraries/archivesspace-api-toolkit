from tasks.generic import GenericTask
import json

# User defined endpoint, action, and data
class UserDefinedTask(GenericTask):

  def run(self):
    # Get endpoint URL
    while True:
      url = self.url_menu()
      if url:
        break
    # Get HTTP verb
    while True:
      action = self.action_menu()
      if action:
        break
    # Get POST data if applicable
    data = None
    if action == 'post':
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
    # Run client request and output
    super()._call(url, action, data)

  # Menu prompt
  def prompt(self):
    return "Enter API endpoint and JSON file"

  # Query user for endpoint URL
  def url_menu(self):
    print("Enter the endpoint you would like to query:")
    print("ie: /repositories/5")
    print("")
    try:
      url = input(">> ")
    except EOFError:
      return None
    return url if super()._confirm("Confirm URL: %s" % url) else None

  # Query user for HTTP verb
  def action_menu(self):
    print("Choose an action:")
    print("")
    print("1) GET")
    print("2) POST")
    print("3) DELETE")
    try:
      action = input(">> ").upper()
    except EOFError:
      return None
    try:
      actionnum = int(action)
      if actionnum == 1:
        action = "get"
      elif actionnum == 2:
        action = "post"
      elif actionnum == 3:
        action = "delete"
      else:
          print("%d is not a valid number" % actionnum)
          print("")
          action = None
    except ValueError:
      print("Please enter a number")
      print("")
      action = None
    return action

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
