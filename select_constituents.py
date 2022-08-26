# General packages
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3 as sq
import numpy as np
import datetime as dt
import os
import copy as cp
from tqdm import tqdm

import hvec_tide as tide
import hvec_stat.gof as gof

Nmx = 10

def set_constit(data):

    os.system('cls')
    print(data['naam'].unique()[0])
    cnt = 0

    # Set the full model
    # Run tidal analysis with automatic constituent selection

    res = pd.DataFrame()

    # Set the full model
    # Run tidal analysis with automatic constituent selection
    coef = tide.run_utide_solve(data['t'], data['h'], meth_N = 'Bence',
        lat = 52, nodal = False, trend = False,
        method = 'robust', conf_int = 'none')

    # Augment data with calculated timeseries with all constituents    
    data = tide._timeseries_segment(
        data, col_datetime = 'tijd', col_h = 'h', lat = 52,
        nodal = False, trend = False, method = 'robust', 
        conf_int = 'none')
    
    h = data['h']
    hfull = data['h_astr']
    const_full = coef.name.tolist()

    print('Full model (first 30): ', const_full[:30])
    print('Rsq adj of full model: ', np.round(coef.Rsq_adj, 2))

    kfull = 2 * len(const_full) + 1

    const = ['M2']  # constituents known to be relevant in NL
    const_full.remove(const[0])

    # Test partial models
    i = -1

    for n in range(40):

        i+=1
        Rsq_max = 0
        
        for cnst in (const_full[:Nmx]):
            # Add one constituent at a time, storing the one mostly improving the model
            # in terms of Rsq_adj
            const_tst = cp.copy(const)
            const_tst.append(cnst)

            coef = tide.run_utide_solve(data['t'], data['h'], meth_N = 'Bence',
                constit = const_tst,
                lat = 52, nodal = False, trend = False,
                method = 'robust', conf_int = 'none')

            Rsq_adj = coef.Rsq_adj
            if Rsq_adj > Rsq_max:
                Rsq_max = Rsq_adj
                cnst_best = cnst  # store best constituent

        const.append(cnst_best) # Add best constituent to set...
        const_full.remove(cnst_best) # ... and remove it from the remaining set

        # Timeseries from reduced model
        hred = tide._timeseries_segment(data,
            constit = const,
            col_datetime = 'tijd', col_h = 'h', lat = 52,
            nodal = False, trend = False, method = 'robust', 
            conf_int = 'none')['h_astr']

        # F-test
        kred = 2 * len(const) + 1

        p = gof.Ftest_red(
            ydata = h,
            ymodel_full = hfull,
            ymodel_red = hred,
            kfull = kfull,
            kred = kred,
            method = 'Bence'
            )['p']

        print(cnst_best, np.round(Rsq_max, 4), np.round(p, 2))
          
        res.at[i, 'name'] = data['naam'].unique()[0]
        res.at[i, 'count'] = coef.count
        res.at[i, 'constits'] = str(const)
        res.at[i, 'N_const'] = len(const)
        res.at[i, 'Rsq'] = Rsq_adj
        res.at[i, 'p'] = p

        #if (p > 0.99): 
        #    break

    return res


# Connect database
conn_str = os.getenv('DATAPATH') + 'RWS_data.db'
cnxn = sq.connect(conn_str, detect_types = True)

names = (
    "Vlissingen",
    "Hoek van Holland",
    "IJmuiden Noordersluis",
#    "IJmuiden buitenhaven",
#    "IJmuiden Buitenhaven",
    "Den Helder",
    "Harlingen",
    "Delfzijl",
    "Lauwersoog",
    "Kornwerderzand buiten",
    "Den Oever buiten"
    "Maassluis"
)

# Read and select data
sql = (
    "SELECT naam, tijd, waarde/100 AS h, tepoch_dy AS t, bron "
    "FROM 'RWS_Waterinfo' "
    "WHERE (naam IN {} AND grootheid == 'WATHTE' ) ".format(names)
)
print('Read data')
df = pd.read_sql(sql, cnxn)
df['year'] = df['tijd'].dt.year
df = df[df['year'].between(1903, 1903)]

res = df.groupby('naam').apply(
    lambda df: set_constit(df)
)

res.reset_index(inplace = True, drop = True)
#res = res[['name', 'N_const', 'Rsq', 'p']]

cnxn = sq.connect(r'../results/select_constit.db', detect_types = True)
res.to_sql(name = 'results', con = cnxn, if_exists = 'replace')

cnxn.close()
print("That's all, folks!")