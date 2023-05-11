import os
import pandas as pd
from hvec_support import sqlite as hvsq
import utide


def test_utide():
    os.chdir(os.getenv('DATAPATH'))
    cnxn = hvsq.connect_verbose(r'RWS_data.db', detect_types = True)
    sql = (
    'SELECT * FROM RWS_Waterinfo WHERE '
    'naam IN ("Harlingen") '
    'AND year IN (1955) '
    )
    df = pd.read_sql(sql, cnxn)


    sol = utide.solve(df['tijd'], df['waarde'], lat = 52)
    
