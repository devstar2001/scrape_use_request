import csv
import pandas as pd
import re
import os
from os import listdir
from os.path import isfile, join

data_folder = 'playground/old'
clean_folder = 'playground/cleaned'

# Function to clean the names
def Clean_names(Clean_name):
    # Search for opening bracket in the name followed by
    # any characters repeated any number of times
    if re.search('\).*', Clean_name):

        # Extract the position of beginning of pattern
        pos = re.search('\).*', Clean_name).start()

        # return the cleaned name
        return Clean_name[:pos+1]

    else:
        # if clean up needed return the same name
        return Clean_name

onlyfiles = [f for f in listdir(data_folder) if isfile(join(data_folder, f))]
for file_name in onlyfiles:
    df = pd.read_csv(data_folder + os.sep + file_name)
    df['office'] = df['office'].apply(Clean_names)
    df.to_csv(clean_folder + os.sep + file_name, index=False)


pass



