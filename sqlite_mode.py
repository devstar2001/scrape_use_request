import sqlite3
from sqlite3 import Error
import csv
import pandas as pd
import os
from os import listdir
from os.path import isfile, join

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    year = '2006'
    data_folder = 'playground/cleaned'
    db_location = 'playground/db/' + year + '.sqlite'
    create_connection(db_location)
    conn = sqlite3.connect(db_location)

    onlyfiles = [f for f in listdir(data_folder) if isfile(join(data_folder, f)) and year in f]
    for file_name in onlyfiles:
        table_name = 'date_' + file_name[:-4]
        df = pd.read_csv(data_folder + os.sep + file_name)
        df.to_sql(table_name, conn, if_exists="replace")
    conn.close()