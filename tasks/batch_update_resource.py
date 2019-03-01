from tasks.generic import GenericTask
from tasks.batch_update_top_container import BatchUpdateTopContainer
import json
import time

# Batch update resources based on json array of resource definitions
class BatchUpdateResource(BatchUpdateTopContainer):
  # Menu prompt
  def prompt(self):
    return "Batch update resources"
