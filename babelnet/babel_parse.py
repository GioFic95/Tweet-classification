import json
import os
import sys
from collections import defaultdict, Counter

import babelnet.babel_search as bs


RES_DIR = os.path.join(os.path.dirname(sys.modules['__main__'].__file__), "res")


def prettify(json_file):
    """Rewrite the json file with correct indentation"""
    json_file = os.path.join(RES_DIR, json_file)

    with open(json_file, 'r+') as jf:
        parsed = json.load(jf)
        out = json.dumps(parsed, indent=4, sort_keys=True)
        # print(out)
        jf.seek(0)
        jf.write(out)


def senses(json_senses):
    """Parse Json object or file and return the corresponding list of senses"""
    goal = []
    senses_list = json_senses

    if type(json_senses) is str:
        json_file = os.path.join(RES_DIR, json_senses)
        print(json_file)
        if os.path.exists(json_file):
            with open(json_file, 'r', encoding='utf-8') as j:
                senses_list = json.load(j)
        else:
            raise ValueError("This string is not a valid path")
        
    for d in senses_list:
        goal += [d['properties']['simpleLemma']]
    
    print(len(goal), goal)
    goal = [x.replace("_", " ").lower() for x in goal]
    goal = set(goal)
    print(len(goal), goal)
    return goal


def synset(json_synset):
    """Parse Json object or file and return the corresponding list of meaningful fields of the synset"""
    goal = []
    synset_list = json_synset

    if type(json_synset) is str:
        json_file = os.path.join(RES_DIR, json_synset)
        print(json_file)
        if os.path.exists(json_file):
            with open(json_file, 'r', encoding='utf-8') as j:
                synset_list = json.load(j)
        else:
            raise ValueError("This string is not a valid path")
        
    for d in synset_list['categories']:
        goal += [d['category']]

    goal += synset_list['domains'].keys()

    for d in synset_list['glosses']:
        for t in d['tokens']:
            goal += [t['word']]

    goal += synset_list['lnToOtherForm']['EN']
    
    print(len(goal), goal)
    goal = [x.replace("_", " ").lower() for x in goal]
    goal = set(goal)
    print(len(goal), goal)
    return goal


def disambiguated_synsets(json_disambiguation, write=False):
    """Parse the result of the Babelfy disambiguation to get babelSynsetIDs, and make a query for those IDs,
    retrieving main fields"""
    goal = []
    synset_list = json_disambiguation

    if type(json_disambiguation) is str:
        json_file = os.path.join(RES_DIR, json_disambiguation)
        print(json_file)
        if os.path.exists(json_file):
            with open(json_file, 'r', encoding='utf-8') as j:
                synset_list = json.load(j)
        else:
            raise ValueError("This string is not a valid path")

    for d in synset_list:
        try:
            goal += [d["babelSynsetID"]]
        except:
            print("Unexpected error with babelfy parsing:", d, sys.exc_info()[0])
            raise
    print(goal)

    new_goal = []
    for g in goal:
        goal_entry = dict()

        path = os.path.join(RES_DIR, "synset")
        ids = [x[:-5].replace("_", ":") for x in os.listdir(path)]

        if g in ids:
            print("synset found:", g)
            json_g = g.replace(":", "_") + ".json"
            json_file = os.path.join(path, json_g)
            with open(json_file, 'r', encoding='utf-8') as j:
                syn_g = json.load(j)
        else:
            if write:
                out_synset_file = g.replace(":", "_")
            else:
                out_synset_file = ""
            syn_g = bs.get_write_synset(g, out_synset_file)

        error = syn_g.get("message", "")
        if error == "BabelSynset not found.":
            # raise ValueError("BabelSynset not found.")   # TODO handle this exception
            continue
        elif error == "Your key is not valid or the daily requests limit has been reached. Please visit" \
                      "http://babelnet.org.":
            raise ConnectionAbortedError("limit reached")
        elif error:
            raise ValueError(error)
        else:
            # syn_g = bs.get_write_synset(g, g.replace(":", "_"))   # debug
            goal_entry["main_sense"] = syn_g.get("mainSense", "")
            goal_entry["is_key_concept"] = syn_g.get("bkeyConcepts", "")
            categories_g = []
            for c in syn_g.get("categories", []):
                categories_g += [c["category"].replace("_", " ").lower()]
            goal_entry["categories"] = categories_g
            domains_g = []
            for d in syn_g.get("domains", []):
                domains_g += [d.replace("_", " ").lower()]
            goal_entry["domains"] = domains_g
            new_goal += [goal_entry]

    return new_goal


def extract_concept(json_disambiguation, k=3, to_print=False, out_file=None):
    """Establish the main concepts of the text"""
    ds = disambiguated_synsets(json_disambiguation, True)
    if to_print:
        out = json.dumps(ds, indent=4, sort_keys=True)
        print(out)
    if out_file:
        out_file = os.path.join(RES_DIR, "concepts", out_file + ".json")
        # print(out_file)
        with open(out_file, 'w+') as jf:
            out = json.dumps(ds, indent=4, sort_keys=True)
            jf.write(out)

    summary = Counter()
    for entry in ds:
        for c in entry["domains"]:
            summary[c] += 1
            if entry["is_key_concept"]:
                summary[c] += 1

    print(summary)
    # summary_max = max(summary, key=lambda key: summary[key])
    return summary.most_common(k)
