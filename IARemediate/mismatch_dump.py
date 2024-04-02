#!/usr/bin/env python3
"""
Open the pickle files for the latest assets:
- item_mismatches
- mismatched_items_that_derived

print out the subset of item_mismatches which were derived
"""
import os
import pickle
import sys
from pathlib import Path

mism_derive_data_path = Path(os.getenv("DAGSTER_HOME"),"storage","mismatched_items_that_derived")
item_mism_data_path = Path(os.getenv("DAGSTER_HOME"),"storage","item_mismatches")

mism_derived = pickle.load(open(mism_derive_data_path, "rb"))
item_mism =  pickle.load(open(item_mism_data_path, "rb"))

ff = [{ 'item': x, 'mismatches' :item_mism[x]} for x in mism_derived]
#
# item_mism is
# {'item': 'bdrc-W1FEMC032584', 'mismatches': {'items not in bdrc-khmermanuscripts that should be:'}}

with open(Path(Path.home(), "dev", "ao-workflows", "../data", "mismatches.txt"), "w") as fout:
    for mism in ff:
        fout.write(f"{mism['item']:19}")
        newl=''
        sp  = ' '
        spad = f"{sp:1}"
        for mism_reason in mism['mismatches']:
            fout.write(f"{newl}{spad}{mism_reason}")
            newl='\n'
            spad = f'{sp:20}'
        fout.write(newl)
