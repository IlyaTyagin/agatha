from pathlib import Path
from agatha.util.misc_util import Record
import json
from agatha.construct.document_parsers import document_record
import re

"""
Parses JSON files that conform to this schema:

https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/2020-03-13/json_schema.txt

"""

def json_path_to_record(json_path:Path)->Record:
  json_path = Path(json_path)
  assert json_path.is_file()
  with open(json_path, 'rb') as json_file:
    json_data = json.load(json_file)

  record = document_record.new_document_record()

  try:
    record["pmid"] = json_data["paper_id"]
    record["title"] = json_data["metadata"]["title"]
    for author in json_data["metadata"]["authors"]:
      name = f"{author['first']} {author['last']}"
      record["authors"].append(name)

    if "abstract" in json_data:
      for abstract_text in json_data["abstract"]:
        record["text_data"].append(dict(
          text=abstract_text["text"],
          type="abstract:raw"  # Note, section names for covid data are bad
        ))

    if "body_text" in json_data:
      for body_text in json_data["body_text"]:
        record["text_data"].append(dict(
          text=body_text["text"],
          type="body:raw",
        ))

    if "ref_entries" in json_data:
      for _, reference_entry in json_data["ref_entries"].items():
        record["text_data"].append(dict(
          text=reference_entry["text"],
          type="ref:"+reference_entry["type"].lower()
        ))

  except Exception as e:
    print(json_data["paper_id"])
    raise e

  document_record.assert_valid_document_record(record)
  return record
