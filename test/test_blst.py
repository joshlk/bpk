#!/usr/bin/env python

from tempfile import mkdtemp
import os
import numpy as np
import pandas as pd

from blosc_store import *

def test_write_read():

    # Create DataFrame
    df = pd.DataFrame(np.random.rand(4, 5))
    df.columns = ['A', 'B', 'C', 'D', 'E']
    df.index = [0.1, 0.2, 0.3, 0.4]
    df['A'] = df['A'].astype('str')
    df['B'] = df['B'].astype('category')
    df['C'] = pd.to_datetime(1e18 * df['C'])
    df['D'] = (1e5 * df['D']).astype('uint')

    # Save to temp directory
    tmp_dir = mkdtemp()
    blst_path = os.path.join(tmp_dir, 'test_output.blst')

    to_blst(df, blst_path)
    df_2 = read_blst(blst_path)

    assert df.equals(df_2)

