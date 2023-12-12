"""
Tidal analysis per location and per year.
Store the result to database for later use.

HVEC, march 2022
"""
print("30_constit_calc commenced")
# General packages
import pandas as pd
import sqlite3 as sq
import time
from tqdm import tqdm
import os
import logging
import copy as cp

# Company packages
import hvec_support.sqlite as hv
import hvec_tide as tide


# Debugging and logging
logging.basicConfig(filename='RWS_constits.log', encoding='utf-8', level=logging.INFO, filemode = 'w')
logging.captureWarnings(capture = True)


names = (
    "Vlissingen",
    "Hoek van Holland",
    "IJmuiden Noordersluis",
    "IJmuiden buitenhaven",
    "IJmuiden Buitenhaven",
    "Den Helder",
    "Harlingen",
    "Delfzijl",
    "Lauwersoog",
    "Kornwerderzand buiten",
    "Den Oever buiten"
    "Maassluis"
    )


def initialise():
    """
    Apply a few settings before commencing

    Args:
        name, string: location
    """
    global conn_in, conn_out, names
    
    tqdm.pandas()

    dir = os.getenv("DATAPATH")
    file = 'RWS_data.db'
    conn_in = hv.connect_verbose(dir + file, detect_types = True)
    
    file = 'RWS_processed.db'
    try:
        os.remove(dir + file)
    except:
        pass
    
    conn_out = hv.connect_verbose(dir + file)
    return
    

def read_data(name):
    """
    Read observations for analysis

    Args:
        name, string: location
    """
    print('Reading data')
    sql = (
        "SELECT naam, tijd, tepoch_dy AS t, waarde/100 AS h, bron "
        "FROM 'RWS_Waterinfo' "
        "WHERE (naam IN {} AND grootheid == 'WATHTE' ) ".format(name)
    #    "AND bron!= 'Historische waterstandsdata. Verkregen van RWS DID ') ".format(name)
    )
    df = pd.read_sql(sql, conn_in)
    df.sort_values(by = 'tijd', inplace = True)
    df['year'] = df['tijd'].dt.year
    df = df[df['year'] < 2022]
    #df = df[df['tijd'].dt.year.isin([2019, 2020, 2021])]
    conn_in.close()
    return(df)


def patch_ijmuiden():
    """
    Station IJmuiden Noordersluis misses data. Differences between
    Noordersluis and Buitenhaven (also spelled as buitenhaven) are 
    negligible.

    So creating a station "IJmuiden"
    """
    tmp = cp.copy(df[
        df['naam'].isin(["IJmuiden Noordersluis", "IJmuiden buitenhaven", "IJmuiden Buitenhaven"])
    ])
    tmp.drop_duplicates(subset = 'tijd', inplace = True)
    tmp['naam'] = 'IJmuiden'
    df2 = df.append(tmp)
    return df2


def analyse_grouped_years(df, constit, step = 2):
    """
    Run tide analysis for multi-year periods
    """
    print(df['naam'].unique()[0])
    years = df['year'].unique()
    res = pd.DataFrame()

    for i, yr in enumerate(tqdm(years[step: len(years) + 1])):

        tmp = pd.DataFrame()
        data = df[df['year'].between(yr - step, yr)]  # Take trailing set
        
        coef = tide.run_utide_solve(data['t'], data['h'], meth_N = 'Bence',
            constit = constit,
            lat = 52, nodal = False, trend = False,
            method = 'robust', conf_int = 'none')

        if not(isinstance(coef, str)):
            tmp = pd.concat(
                [tmp, tide.parse_utide(coef, include_phase = False)]
            )
            tmp['year'] = [yr]
            tmp['year_start'] = [yr - step]
            
            res = pd.concat([res, tmp])

    return res


def wrap_up():
    """
    Before ending the script:
    - Close database
    - Say goodbye nicely
    """
    conn_out.execute("VACUUM")
    conn_out.close()
    print("Script finished.")
    print("Good bye!")
    time.sleep(5)    
    return


#================= main ===================
initialise()

cnst = {
    'short': ['M2', 'S2'],
    'vRijn': ['M2', 'S2', 'N2', 'K2', 'K1', 'O1', 'P1'],
    'PE': ['M2', 'S2', 'M4', 'SA', 'N2', 'O1', 'MS4']}

df = read_data(names)
df = patch_ijmuiden()

# Analyse on yearly intervals
const_yr = pd.DataFrame()

for ky in cnst.keys():
    os.system("cls")
    print('Constituent set: ', ky)

    tmp = df.groupby('naam').apply(
        lambda df: analyse_grouped_years(df, step = 0, constit = cnst[ky])
    )
    tmp['set'] = ky

    const_yr = pd.concat([const_yr, tmp])
 
    
# Store
const_yr.to_sql(
    name = 'const_yr',
    con = conn_out,
    if_exists = 'replace'
) 

wrap_up()