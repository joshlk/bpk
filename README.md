# Blosc store
A high performance compressed columnar data store for Pandas DataFrames.

If you are represented with the following dilemma, then blosc_store can help:
* You have a large table in [Pandas](http://pandas.pydata.org) (>5GB)
* You want to save it
* You want to preserve the Pandas datatypes (bool, numerical, datetime, category, string)
* BUT you can't use HDF due to large strings in some of the columns! ([OverflowError: value too large to convert to int](https://github.com/pandas-dev/pandas/issues/2773) error)
* **There are no other good alternatives**

I created blosc_store to meet this gap. The file format is very simple and builds upon bloscpack and CSVs.

For best performance gains convert columns which have a low number of unique items to the category datatype and dates
to datetime datatype.

## Details
The blst format is a folder and it contains:
* A `columns.txt` which is a table of column names and data type
* Numerical columns (bool, numbers and datetime) are serialised using bloscpack and saved individually with a `.bp` extension
* String columns are serialised individually as plain text file (CSV)
* Categories and settings are stored in a json file and the code are serialized with bloscpack

That’s it!

## Performance

Some random performance stats generated using a table I had in memory:
```
        Size    Read time
CSV     5.12GB  4mins, 8sec
blst    3.3GB   1min, 40sec     (did not convert dates or categories)
blst    1.26GB  40sec           (all columns converted)
```
