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
        data = self.json_menu()
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
