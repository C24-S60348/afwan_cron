#apps/utils/data_helper.py
import csv
from .csv_helper import *

def af_afwangetdb(name="afwan", get="value"):
    data = af_getcsvdict("static/db/afwanDB.csv")
    for d in data:
        if d["name"] == name:
            return d[get]
    return "no data found"