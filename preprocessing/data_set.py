import csv
import json
import os
import re
import sys

import emoji
import pandas as pd

from preprocessing.data_base import connect
import babelnet.babel_parse as bp
import babelnet.babel_search as bs


RES_DIR = os.path.join(os.path.dirname(sys.modules['__main__'].__file__), "res")
IDS = []


def clean_row(res):
    """Remove noise from data"""
    print(res[0], " --- ", res[6])
    tweet_id = res[0]
    text = res[6].replace("RT ", " ").lower()
    stop_words = ["@", "#", '"']
    for sw in stop_words:
        text = text.replace(sw, "")
    space_words = [",", "\n"]
    for sw in space_words:
        text = text.replace(sw, " ")
    text = re.sub(r'|'.join(map(re.escape, emoji.UNICODE_EMOJI)), '', text)
    text = re.sub(r'(\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*)|(http.*?…)', '', text)   # remove URLs
    return tweet_id, text, ""


def build_dataset(filename):
    """Reads from database and write on filename, cleaning the dataset"""
    dataset_path = os.path.join(RES_DIR, filename)
    with open(dataset_path, 'w+', newline='', encoding='utf-8') as dataset_file:
        dswriter = csv.writer(dataset_file)
        dswriter.writerow(["id", "text", "label"])
        connect("select * from tweet", clean_row, dswriter.writerow)


def set_label(row):
    """Handle a single row of the dataset, to add its label"""
    text = row["text"]
    row_id = row["id"]

    if str(row_id) in IDS:
        print("\n--- row found:" + str(row_id))
        print(text)

        concept_file = os.path.join(RES_DIR, "concepts", str(row_id)+".json")
        with open(concept_file, 'r') as cf:
            concept = json.load(cf)
    else:
        print("\n---   " + str(row_id))
        print(text)

        disambiguation = bs.get_write_disambiguation(text, "IT", partial_match=True, out_file=row_id)
        concept = bp.extract_concept(disambiguation, out_file=str(row_id).replace(":", "_"))
    if not concept:
        row["label"] = ""
    else:
        # row["label"] = concept[0][0]
        row["label"] = str(concept)
    return row


def add_labels(old_dataset, new_dataset=""):
    """Add the labels to each row in the dataset"""
    if not new_dataset:
        new_dataset = old_dataset

    old_dataset_path = os.path.join(RES_DIR, old_dataset)
    new_dataset_path = os.path.join(RES_DIR, new_dataset)
    ds = pd.read_csv(old_dataset_path)
    # ds = ds[0:200]   # TODO solo per test
    global IDS
    path = os.path.join(RES_DIR, "concepts")
    IDS = [x[:-5] for x in os.listdir(path)]
    try:
        ds = ds.apply(set_label, axis=1)
    except ConnectionAbortedError:
        print("We need more coins!")
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise
    finally:
        ds.to_csv(new_dataset_path, index=False)
