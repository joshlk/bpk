#!/usr/bin/env python

import os
import shutil
import pandas as pd
import bloscpack as bp

try:
    import ujson as json
except:
    import json

"""
For reading and writing to the blosc store blst format. Nuances that users should take note:
* String column names are always saved as strings irrespective of there original data-type (e.g. int)
* DataFrame index is currently not preserved
* Datatypes currently supported: strings, numerical, datetime, categorical (with string and numeric)
"""

def to_blst(df, path):
    """
    Save a DataFrame using blst format

    :param df: DataFrame to save
    :type df: pandas.DataFrame
    :param path: The path to save to the blst store to. It uses a directory but you are still recommended to use a
    '.blst' extension
    :type path: str
    :return:
    """

    # Ensure not multi-index
    if isinstance(df.columns, pd.MultiIndex):
        raise NotImplementedError("MultiIndex columns not supported")

    # Delete directory if already exists and make folder
    if os.path.isdir(path):
        shutil.rmtree(path)

    os.makedirs(path)

    # Save column file
    column_meta_file = os.path.join(path, 'columns.txt')
    column_meta = df.dtypes.reset_index()
    column_meta.columns = ['col', 'dtype']
    column_meta.to_csv(column_meta_file, sep='\t', index=False)

    # Save each column
    for col in df.columns:
        dtype = str(df.dtypes[col])

        if dtype == 'object':   # String
            file = os.path.join(path, "{}.csv".format(col))
            df[[col]].to_csv(file, index=False, header=False)

        elif dtype == 'category':
            meta_file = os.path.join(path, "{}.meta.json".format(col))
            file = os.path.join(path, "{}.bp".format(col))

            # Meta file which contains the categories
            meta = {
                'categories': df[col].cat.categories.tolist(),
                'ordered': df[col].cat.ordered
            }

            with open(meta_file, 'w') as f:
                json.dump(meta, f)

            bp.pack_ndarray_file(df[col].cat.codes.values, file)

        else:   # Numeric and datetime dtype
            file = os.path.join(path, "{}.bp".format(col))
            bp.pack_ndarray_file(df[col].values, file)

def read_blst_columns(path):
    """
    Read the columns and datatype of a blst store
    :param path: Path to blst store
    :return: DataFrame of columns and dtypes
    """
    column_meta_file = os.path.join(path, 'columns.txt')
    column_meta = pd.read_table(column_meta_file)
    return column_meta

def read_blst(path, columns='ALL'):
    """
    Read a blst data store and return a DataFrame

    :param path: Path to blst data store. Give the directory location
    :param columns: Which columns to read and in which order. Give 'ALL' to read all columns.
    :return: Read data
    :rtype: pandas.DataFrame
    """

    # Read the columns
    column_meta = read_blst_columns(path)
    column_meta_dict = column_meta.set_index('col')['dtype'].to_dict()

    # Check columns integrity
    if columns != 'ALL':
        for col in columns:
            if col not in column_meta_dict:
                raise KeyError("'{}' not a column".format(col))
    else:
        columns = column_meta['col']

    # Read each column
    for i, col in enumerate(columns):
        dtype = column_meta_dict[col]

        if dtype == 'object':   # String
            file = os.path.join(path, "{}.csv".format(col))
            col_df = pd.read_csv(file, header=None, names=[col])

        elif dtype == 'category':
            meta_file = os.path.join(path, "{}.meta.json".format(col))
            file = os.path.join(path, "{}.bp".format(col))

            with open(meta_file, 'r') as f:
                meta = json.load(f)

            col_df = bp.unpack_ndarray_file(file)
            col_df = pd.Categorical.from_codes(col_df, meta['categories'],
                                               ordered=meta['ordered'])
            col_df = pd.Series(col_df, name=col).to_frame()

        else:   # Numeric and datetime dtype
            file = os.path.join(path, "{}.bp".format(col))
            col_df = bp.unpack_ndarray_file(file)
            col_df = pd.Series(col_df, name=col).to_frame()

        if i == 0:
            df = col_df
        else:
            df[col] = col_df

    return df
