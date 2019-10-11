import json
import os
import sys

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

RES_DIR = os.path.join(os.path.dirname(sys.modules['__main__'].__file__), "res")
ID_URL = "https://babelnet.io/v5/getSynsetIds?lemma=%s&searchLang=%s&key=%s"
SENSES_URL = "https://babelnet.io/v5/getSenses?lemma=%s&searchLang=%s&key=%s"
SYNSET_URL = "https://babelnet.io/v5/getSynset?id=%s&key=%s"
BABELFY_URL = "https://babelfy.io/v1/disambiguate?text=%s&lang=%s&key=%s"


def get_key(filename, key_name):
    """Read the value of the Babelnet/Babelfy key"""
    config_file = os.path.join(RES_DIR, "config", filename)
    with open(config_file, 'r') as cf:
        db_config = json.load(cf)
        res = db_config[key_name]
        return res


KEY = get_key("keys.json", "KEY4")


def get_synset_ids(lemma, lang):
    """Returns the id of each sense of the lemma"""
    url = ID_URL % (lemma, lang, KEY)
    r = requests.get(url)
    resp = r.json()
    ids = [x['id'] for x in resp]
    return ids


def get_write_senses(lemma, lang, out_file=""):
    """Returns all the senses of the lemma"""
    url = SENSES_URL % (lemma, lang, KEY)
    r = requests.get(url)
    resp = r.json()

    if out_file is not "":
        out_file = os.path.join(RES_DIR, "senses", out_file + ".json")
        with open(out_file, 'w+') as jf:
            out = json.dumps(resp, indent=4, sort_keys=True)
            jf.write(out)

    return resp


def get_write_synset(syn_id, out_file=""):
    """Returns the synset of the specified ID"""
    url = SYNSET_URL % (syn_id, KEY)
    # r = requests.get(url)

    req = requests.Request('GET', url)
    req = req.prepare()
    sess = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    sess.mount('http://', adapter)
    sess.mount('https://', adapter)
    r = sess.send(req)

    resp = r.json()

    if out_file is not "":
        out_file = os.path.join(RES_DIR, "synset", out_file + ".json")
        with open(out_file, 'w+') as jf:
            out = json.dumps(resp, indent=4, sort_keys=True)
            jf.write(out)

    return resp


def get_write_disambiguation(text, lang, out_file="", partial_match=False):
    """Returns the Babelfy disambiguation of the text"""
    url = BABELFY_URL % (text, lang, KEY)
    if partial_match:
        url += "&match=PARTIAL_MATCHING"
    req = requests.Request('GET', url)
    req = req.prepare()
    sess = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    sess.mount('http://', adapter)
    sess.mount('https://', adapter)
    resp = sess.send(req)
    resp.encoding = "gzip"
    resp = resp.json()

    if out_file is not "":
        out_file = os.path.join(RES_DIR, "disambiguation", str(out_file) + ".json")
        with open(out_file, 'w+') as jf:
            out = json.dumps(resp, indent=4, sort_keys=True)
            jf.write(out)

    return resp

