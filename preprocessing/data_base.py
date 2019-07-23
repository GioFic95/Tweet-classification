import json
import os
import sys

import psycopg2

RES_DIR = os.path.join(os.path.dirname(sys.modules['__main__'].__file__), "res")


def config(filename='DB_config.json', section='standard'):
    """Read configuration parameters for the database"""
    config_file = os.path.join(RES_DIR, "config", filename)
    with open(config_file, 'r') as cf:
        db_config = json.load(cf)
        res = db_config[section]
        return res


def connect(query, clean, func):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        print('Result:')
        cur.execute(query)

        # display the PostgreSQL database results
        # res = cur.fetchone()
        # res = clean(res)
        # func(res)

        res_list = cur.fetchall()
        for res in res_list:
            clean_res = clean(res)
            func(clean_res)

        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')

