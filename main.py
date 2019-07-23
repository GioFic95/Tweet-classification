import os
import sys
import time

# import nltk.tokenize.repp as tokenize
from nltk import word_tokenize

import babelnet.babel_parse as bp
import babelnet.babel_search as bs
import preprocessing.data_base as db
import preprocessing.data_set as ds


# TEMP_DIR = os.path.join(os.path.dirname(sys.modules['__main__'].__file__), "temp")
# NLTK_DIR = "C:\\Users\\super\\AppData\\Roaming\\nltk_data\\tokenizers"


def test_babel_search():
    my_ids = bs.get_synset_ids("line+code", "EN")
    print(my_ids)

    bs.get_write_senses("line+code", "EN", "line_code")

    for my_id in my_ids:
        bs.get_write_synset(my_id, my_id.replace(":", "_"))


def test_babel_read():
    bp.prettify("babelfy.json")
    print("from files")
    print("senses:")
    bp.senses("sense.json")
    print("synset:")
    bp.synset("synset.json")


def test_search_read():
    print("from results")
    print("senses:")
    sen = bs.get_write_senses("line+code", "EN")
    bp.senses(sen)
    print("synset:")
    my_ids = bs.get_synset_ids("line+code", "EN")
    syn = bs.get_write_synset(my_ids[0])
    bp.synset(syn)


def test_disambiguation():
    # example = "BabelNet is both a multilingual encyclopedic dictionary and a semantic network"
    # disambiguation = bs.get_write_disambiguation(example, "EN", "example")
    # ds = bp.disambiguated_synsets(disambiguation)
    # print(ds)
    # ds = bp.disambiguated_synsets("example__babelfy.json")
    # concept = bp.extract_concept("example__babelfy.json", True)

    text = "Con la legge sul PostMortem, approvata al Senato, la medicina ha uno strumento in più, di cui " \
           "beneficeremo tutti. Con il voto della Camera, presto finalmente doteremo l’Italia di uno strumento che i " \
           "medici e i ricercatori aspettano da anni."
    disambiguation = bs.get_write_disambiguation(text, "IT", "5stelle_medicina")
    concept = bp.extract_concept(disambiguation, False, "5stelle_medicina")

    # text = word_tokenize(text)
    # text = " ".join(text)
    # print(text)
    # disambiguation = bs.get_write_disambiguation(text, "IT", "5stelle_medicina_2")
    # concept = bp.extract_concept(disambiguation, False, "5stelle_medicina_2")
    print(concept)


if __name__ == '__main__':
    # test_babel_search()
    # test_babel_read()
    # test_search_read()
    # syn = bs.get_write_synset("bn:00015267n", "cane")
    # test_disambiguation()

    # bs.get_write_synset("bn:00024636n", "bn_00024636n_bis")
    # ds.build_dataset("dataset8.csv")

    start_time = time.time()
    ds.add_labels("dataset8.csv", "dataset10.csv")
    print("\n--- %s seconds ---" % round(time.time() - start_time, 3))
