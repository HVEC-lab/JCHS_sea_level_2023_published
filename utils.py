"""
Support library for research into sea levels.
HVEC, 2022
"""

import os
import copy as cp
import sqlite3 as sq
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import hvec_support
from constants import PICTURES


# Settings
plt.rcParams['axes.grid'] = True
figsize = (20, 24)


names = [
    'Delfzijl',
    'Harlingen',
    'Den Helder',
    'IJmuiden',
    'Hoek van Holland',
    'Vlissingen'
]


Nmn = 2910


def read_data_rws(constit_set):
    """
    Read table with observed water levels; complete years only
    """
    # Connect database
    conn_str = os.getenv('DATAPATH') + 'RWS_JCHS.db'
    cnxn = sq.connect(conn_str, detect_types = True)

    sql = (
        "SELECT * "
        "FROM 'const_yr' "
        "WHERE naam IN ('Delfzijl', 'Harlingen', "
        "'Den Helder', 'IJmuiden',  "
        "'Hoek van Holland', 'Vlissingen') "
        "AND (count) "
    )
    df = pd.read_sql(sql, cnxn)
    cnxn.close()

    df.columns = df.columns.str.replace('_ampl', '')

    df = df[df['const_set'] == constit_set]

    df = df[df['year'] < 2022]

    df['M2+S2'] = df['M2'] + df['S2']
    return df


def read_data_psmsl():
    """
    Read data psmsl
    """
    # Connect database
    conn_str = os.getenv('DATAPATH') + 'PSMSL.db'
    cnxn = sq.connect(conn_str, detect_types = True)

    # Read table with observed water levels; complete years only
    sql = (
        "SELECT name, time, level, type, freq FROM data "
        "WHERE freq = 'annual' "
        "AND name IN ('DELFZIJL', 'HARLINGEN', "
        "'DEN HELDER', 'IJMUIDEN',  "
        "'HOEK VAN HOLLAND', 'VLISSINGEN') "
        "AND type = 'rlr'"
        )

    psmsl = pd.read_sql(sql, cnxn)
    cnxn.close()

    psmsl['level'] = psmsl['level']

    return psmsl


def read_data_ipcc():
    """
    Read specified data IPCC
    """
    # Connect database
    conn_str = os.getenv('DATAPATH') + 'IPCC.db'
    cnxn = sq.connect(conn_str, detect_types = True)
    sql = (
        "SELECT * "
        "FROM data "
        "WHERE name IN ('DELFZIJL', 'HARLINGEN', "
        "'DEN HELDER', 'IJMUIDEN',  "
        "'HOEK VAN HOLLAND', 'VLISSINGEN') "
        "AND (process == 'totalrates') "
        "AND scenario IN ('ssp126', 'ssp245') "
        "AND (confidence == 'medium') "
        "AND (year == 2020) ")

    df = pd.read_sql(sql, cnxn)
    cnxn.close()

    return df


def process_ipcc(df):
    """
    Select and process ipcc data
    """
    # Put name as first column
    cols = df.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    df = cp.deepcopy(df[cols])

    # add parameters
    df['90%_band'] = df['90%_high'] - df['median']
    #df['sigma'] = (df['90%_band'] / k).round(2)

    # Brush up
    df.sort_values(by = 'name', inplace = True)
    df = df.drop(columns = [
        'psmsl_id', 'process', 'confidence', '90%_low', '90%_high'])
    df['name'] = df['name'].str.title()

    df[['median', 'sigma', '90%_band']] = 100 * 1000 * df[['median', 'sigma', '90%_band']]
    return df


def graph_Rsqadj(df):
    """
    Graph of coefficients of determination of harmonic analysis
    """
    fig, ax = plt.subplots(nrows = 6, ncols = 1, sharex = True, sharey = True, figsize = figsize)
    for i, nm in enumerate(names):
        data = df[df['naam'] == nm]
        ax[i].plot(
            data['year'], data['Rsq_adj'], 'rx'
        )

        ax[i].set_ylabel('$R^{2}_{adjusted}$')
        ax[i].title.set_text(
            nm + ", the Netherlands; coefficient of determination of reconstructed tide")
        ax[i].set_ylim(0.5, 1)

    plt.xlabel('Year')
    plt.tight_layout()
    plt.savefig(f'{PICTURES}/Rsq_all.jpg')
    return


def graph_z0(df, psmsl):
    """
    Graph mean sea level
    """
    _, ax = plt.subplots(nrows = 6, ncols = 1, sharex = True, sharey = True, figsize = figsize)
    for i, nm in enumerate(names):
        data = df[np.logical_and(df['naam'] == nm, df['count'] < Nmn)]

        ax[i].set_ylim([-0.5, 0.5])
        
        ax[i].plot(
            data['year'], data['z0'], 'ro',
            label = 'Mean sea level from tide analysis. N < ' + str(Nmn) + ' points per year',
            markersize = 8, mfc = 'none')

        ax[i].plot(
            data['year'], data['zmean'], 'k^',
            label = 'Arithmetic mean sea level. N < ' + str(Nmn) + ' points per year',
            markersize = 8, mfc = 'none')

        data = df[np.logical_and(df['naam'] == nm, df['count'] >= Nmn)]

        ax[i].plot(
            data['year'], data['z0'], 'ro',
            label = 'Mean sea level from tide analysis. N > ' + str(Nmn) + ' points per year',
            markersize = 8)

        ax[i].plot(
            data['year'], data['zmean'], 'k^',
            label = 'Arithmetic mean sea level. N > ' + str(Nmn) + ' points per year',
            markersize = 8)


        mn = data[data['year']>=1990]['zmean'].mean()
        data = psmsl[psmsl['name'] == nm.upper()]

        mn2 = data[data['time']>=1990]['level'].mean()
        delta = mn2 - mn

        ax[i].plot(
            data['time'], data['level'] - delta, 'bx',
            label = 'PSMSL',
            markersize = 5, mfc = 'none')
        ax[i].set_ylabel('Level (CD +m)')
        ax[i].title.set_text(nm + ", the Netherlands; mean sea level")

    plt.xlabel('Year')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{PICTURES}/MSL_all.jpg')
    return


def graph_amplitudes(df):
    """
    Graph of tidal amplitude; summed M2 and S2
    """
    _, ax = plt.subplots(nrows = 6, ncols = 1, sharex = True, sharey = False, figsize = figsize)
    for i, nm in enumerate(names):
        data = df[df['naam'] == nm]
        
        mu = (data['M2'] + data['S2']).mean()

        data = data[df['count'] < Nmn]

        ax[i].plot(
            data['year'], data['M2+S2'], 'rs',
            label = 'Summed amplitude M2 and S2, N < '+ str(Nmn),
            markersize = 8, mfc = 'none')

        data = df[np.logical_and(df['naam'] == nm, df['count'] >= Nmn)]

        ax[i].plot(
            data['year'], data['M2+S2'], 'rs',
            label = 'Summed amplitude M2 and S2, N < '+ str(Nmn),
            markersize = 8)

        data = df[df['naam'] == nm]
        
        ax[i].plot(
            data['year'], data['M2'], 'kx',
            label = 'Amplitude of M2'
        )

        ax[i].plot(
            data['year'], data['S2'], 'b^',
            label = 'Amplitude of S2'
        )

        ax[i].set_ylabel('Amplitude (m)')
        ax[i].set_xlabel('Year')

        ax[i].title.set_text(nm + ", the Netherlands; tide")
        ax[i].set_ylim(0, mu+0.6)
        
        if nm in ['Den Helder', 'Harlingen']:
            ax[i].fill_betweenx(y = [0, mu+0.6], x1 = 1928, x2 = 1932, color = 'gray', alpha = 0.5)
            # ax[i].vlines(x = 1940, ymin = 0, ymax = mu+0.6, linestyle = '--')
        
    ax[i].legend(loc = 'best')
    plt.tight_layout()
    plt.savefig(f'{PICTURES}/M2+S2_all.jpg')
    return


def graph_windeffect(df):
    """
    Graph of calculated wind effect
    """
    _, ax = plt.subplots(nrows = 6, ncols = 1, sharex = True, sharey = False, figsize = figsize)
    for i, nm in enumerate(names):
        data = df[df['naam'] == nm]
        
        mu = (data['smean']).mean()

        data = data[df['count'] < Nmn]

        ax[i].plot(
            data['year'], data['smean'], 'rs',
            label = 'Yearly mean wind effect, N < '+ str(Nmn),
            markersize = 8, mfc = 'none')

        data = df[np.logical_and(df['naam'] == nm, df['count'] >= Nmn)]

        ax[i].plot(
            data['year'], data['smean'], 'rs',
            label = 'Yearly mean wind effect, N < '+ str(Nmn),
            markersize = 8)

        data = df[df['naam'] == nm]
        
        ax[i].set_ylabel('Difference with tide (m)')
        ax[i].set_xlabel('Year')

        ax[i].title.set_text(nm + ", the Netherlands; wind effect")
        ax[i].set_ylim(mu - 0.1, mu+0.1)
                
    ax[i].legend(loc = 'best')
    plt.tight_layout()
    plt.savefig(f'{PICTURES}/windeffect_all.jpg')
    return


#====================
if __name__ == '__main__':
    df = read_data_rws(constit_set = 'Ftested3')
    graph_amplitudes(df)
    plt.show()
