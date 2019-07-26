import pandas as pd
import numpy as np
import os.path
import csv
import pickle
import datetime
from absolute_data_paths import relative_to_absolute

#%%
def read_raw_data(filename, column_file, samplename, dataset_name):
    filename = "../00_raw_data/" + filename
    path_to_file = relative_to_absolute(filename)
    columns = read_raw_columns(column_file)
    df = pd.read_csv(
        path_to_file, header=None, names=columns,
        low_memory=False, encoding="ansi", keep_default_na=True,
        na_values=["", "?", "NULL", "NA", "Nan"], decimal="."
                    )
    save_dataframe(df, dataset_name)
    return df


def read_raw_columns(filename):
    filename = "../01_data_understanding/" + filename
    path_to_file = relative_to_absolute(filename)
    column_txt = open(path_to_file, "r")
    line_list = column_txt.readlines()
    column_list = []
    for line in line_list:
        string = line
        string_list = string.split(":")
        name = str.replace(string_list[0], " ", "_")
        name = str.replace(name, "\\", "")
        column_list.append(name)
    return column_list


def load_dataframe_without_ignore(filename, column_file):
    # Determine which columns should be ignored
    column_file = "../01_data_understanding/" + column_file
    path_to_file = relative_to_absolute(column_file)
    column_txt = open(path_to_file, "r")
    line_list = column_txt.readlines()
    column_list = []
    for line in line_list:
        string = line
        string_list = string.split(":")
        if string_list[1][1:len(string_list[1]) - 2] == "ignore":
            column_list.append(string_list[0])

    # loading the dataframe and dropping the ignore-columns
    filename = "../00_raw_data/data_sets/" + filename
    path_to_file = relative_to_absolute(filename)
    df = pd.read_pickle(path_to_file)
    df.drop(column_list, axis=1, inplace=True)
    return df


def recreate_dtypes(dataframe, dtypes):
    i = 0
    for column in dataframe:
        if dtypes[i] == np.float64:
            dataframe[column] = pd.to_numeric(
                dataframe[column], errors='coerce')
        else:
            dataframe[column] = dataframe[column].astype(dtype=dtypes[i])
        i = i + 1
    return dataframe


def identify_column_type(type):
    # continuous
    # date
    # time
    # ignore
    # element1,element2,element3.
    # [ordered] element1, element2, element3.
    type = type[1:len(type) - 2]

    if type == "continuous":
        return np.float64
    if type == "date":
        return object
    if type == "time":
        return object
    if type.startswith("[ordered]"):
        categories = split_ordered_categories(type)
        return pd.CategoricalDtype(categories=categories, ordered=True)
    category_list = type.split(',')
    if len(category_list) > 1:
        return pd.CategoricalDtype(categories=category_list, ordered=False)
    return np.object


def split_ordered_categories(categories):
    category_list = []
    clean = categories[9:]
    splits = clean.split(',')
    for split in splits:
        category_list.append(split[1:])
    return category_list


def create_sample_excel(dataframe, samplename):
    from pandas import ExcelWriter
    # create a Excel sheet with the heads and the first 1000
    # lines for data understanding
    df = dataframe.iloc[:1000]
    samplename = "../01_data_understanding/" + samplename
    path_to_file = relative_to_absolute(samplename)
    xlsx_writer = ExcelWriter(path_to_file)
    df.to_excel(xlsx_writer, "Sheet1", index=False)
    xlsx_writer.save()


def create_csv_from_dataframe(dataframe, filename):
    filename = "../00_raw_data/" + filename
    path_to_file = relative_to_absolute(filename)
    df = dataframe
    # booleandf = df.select_dtypes(include=[bool])
    # booleanDictionary = {True: 'TRUE', False: 'FALSE'}
    # print(booleandf)
    # for column in booleandf:
    #     df[column] = df[column].map(booleanDictionary)
    df.to_csv(path_or_buf=path_to_file, index=False)


def create_dataframe_from_processed_csv(filename):
    filename = "../00_raw_data/" + filename
    path_to_file = relative_to_absolute(filename)
    df = pd.read_csv(
        path_to_file, low_memory=False
                    )
    return df


def save_dataframe(dataframe, filename):
    filename = "../00_raw_data/data_sets/" + filename
    path_to_file = relative_to_absolute(filename)
    dataframe.to_pickle(path_to_file)


def load_dataframe(filename):
    filename = "../00_raw_data/data_sets/" + filename
    path_to_file = relative_to_absolute(filename)
    df = pd.read_pickle(path_to_file)
    return df

# test if dataset is altered by type change
# df = read_raw_data("order_data.csv","order_columns.txt",
# "order.xlsx","order.pkl")
# print(df[["DoYouPurchaseForOthers","SendEmail",
# "ProductCode","New Bank Card"]])
#%% load dataframe
load_dataframe("clickstream_data.csv")