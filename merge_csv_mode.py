import os
import pandas as pd
from os import listdir
from os.path import isfile, join

year = '2006'
data_folder = 'playground/'
onlyfiles = [f for f in listdir(data_folder) if isfile(join(data_folder, f)) and year in f]
merge_file_name = data_folder + os.sep + 'all' + os.sep + year + '_all.csv'
df = []
for count, file_name in enumerate(onlyfiles):
    df.append(pd.read_csv(data_folder + file_name))

result = pd.concat(df, ignore_index=True)
result.to_csv(merge_file_name, index=False)
pass