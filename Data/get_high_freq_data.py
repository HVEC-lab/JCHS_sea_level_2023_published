"""
Short additional program getting high-frequency data for a single year and
putting it in a database.

HVEC-lab, 2023
"""

import pandas as pd
import sqlite3 as sq

from hvec_importers import rws
from hvec_support import sqlite as hvsq


# Create database
cnxn = sq.connect('data_single_year_high_freq.db', detect_types = True)

names = [
      'Vlissingen'
    , 'Hoek van Holland'
    , 'IJmuiden Noordersluis'
    , 'Den Helder'
    , 'Harlingen'
    , 'Delfzijl']

start = '2020-1-1'
end = '2020-12-31'
for nm in (names):
    print(nm)
    df = rws.data_single_name(name = nm, quantity = 'WATHTE', start = start, end = end, reduce = False)
    df.to_sql(name = 'data', con = cnxn, if_exists = 'append')
    hvsq.write_log(entry = f'High frequency data of {nm} stored', cnxn = cnxn)

hvsq.write_log(entry = 'Removing double entries', cnxn = cnxn)
hvsq.remove_doubles(cnxn = cnxn, table = 'data', columns = ['Naam', 'Tijdstip'])

hvsq.write_log(entry = 'Vacuum database', cnxn = cnxn)
cnxn.execute('VACUUM')
cnxn.close()
input("That's all folks!")
