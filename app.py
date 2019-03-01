import configparser
import argparse
import time
import logging
import requests

from asnake.client import ASnakeClient

from tasks import *

def print_menu(tasks):
  print("Choose a task:")
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
    BatchCreateTopContainer(args, client, logger),
    BatchExportTopContainer(args, client, logger),
    BatchUpdateTopContainer(args, client, logger),
    BatchExportEAD(args, client, logger),
    BatchUpdateResource(args, client, logger),
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
  parser = argparse.ArgumentParser()
  parser.add_argument("-y", "--yes", help="Supply Yes to all confirmation prompts", action="store_true")
  args = parser.parse_args()

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

  config = configparser.ConfigParser()
  config.read('settings.ini')

  try:
    client = ASnakeClient(baseurl=config['aspace_credentials']['api_host'],
                          username=config['aspace_credentials']['username'],
                          password=config['aspace_credentials']['password'])
  except KeyError as e:
    logger.error('settings.ini does not exist or is invalid')
    raise e

  # Simple sanity check to make sure client is setup
  try:
    resp = client.get('/')
    if not resp.ok:
      resp.raise_for_status()
  finally:
    logger.error('Unable to contact ArchivesSpace instance')

  main_menu()
