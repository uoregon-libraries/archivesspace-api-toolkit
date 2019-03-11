import abc
from requests_toolbelt.utils import dump

class GenericTask(abc.ABC):

  def __init__(self, args, client, logger):
    self.args = args
    self.client = client
    self.logger = logger

  # Base case action to perform for this task
  @abc.abstractmethod
  def run(self):
    pass

  # Menu prompt
  @abc.abstractmethod
  def prompt(self):
    pass


  # Query user for JSON data file
  def json_menu(self):
    print("Enter the path to your json file:")
    print("ie: data.json")
    print("")
    try:
      data = input(">> ")
    except EOFError:
      return None
    return data if self._confirm("Confirm path: %s" % data) else None

  # Call aspace client w/ logging
  def _call(self, url, action, data):
    # Get HTTP verb action method (client.get())
    method_to_call = getattr(self.client, action)
    resp = method_to_call(url, json=data)
    print("")
    print("Response:")

    # Log output to file log and console
    resp_dump = dump.dump_response(resp)
    self.logger.debug(data)
    self.logger.info(resp_dump.decode('utf-8'))

    return resp

  # Ask user to confirm prompt
  def _confirm(self, prompt, override_args=False):
    if not self.args.yes or override_args:
      print(prompt)
      print("Y/(N)")
      try:
        confirm = input(">> ").upper()
      except EOFError:
        confirm = "N"
      print("")
    else:
      confirm = "Y"
    return confirm.startswith("Y")
