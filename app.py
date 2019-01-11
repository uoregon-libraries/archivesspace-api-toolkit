import configparser
import argparse
import aspace
import logging

from tasks import *

parser = argparse.ArgumentParser()
parser.add_argument("-y", "--yes", help="Supply Yes to all confirmation prompts", action="store_true")
args = parser.parse_args()

config = configparser.ConfigParser()
config.read('settings.ini')

client = (
  aspace.client.ASpaceClient
  .init_from_config(config)
  .wait_until_ready(
    check_interval=2.0,
    max_wait_time=200.0,
    authenticate_on_success=True,
  )
)

logger = logging.getLogger('archivespace')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('app.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

def print_menu(tasks):
  print("Choose an action:")
  print("")
  optnum = 1
  for task in tasks:
    print("%d) %s" % (optnum, task.prompt()))
    optnum += 1
  print("X) Exit")
  print("")

def main_menu():
  tasks = [
    UserDefinedTask(args, client, logger),
    BatchCreateTopContainer(args, client, logger)
  ]

  done = False
  val = None
  while not done:
    print_menu(tasks)

    try:
      val = input(">> ").upper()
    except EOFError:
      print("")
      val = "X"

    try:
      valnum = min(max(int(val) - 1, 0), len(tasks) - 1)
      tasks[valnum].run()
    except ValueError:
      pass

    if val == "X":
      done = True
      continue


if __name__ == "__main__":
  main_menu()
