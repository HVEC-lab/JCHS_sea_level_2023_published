"""
# =============================================================================
# Import historische waterstanden naar SQLite
# =============================================================================
Door: H.G. Voortman
Datum: 19 november 2019

# =============================================================================
# Versiehistorie
# =============================================================================
20191119- Nieuwe sheet gebaseerd op "Import KNMI daggegevens", H.G. Voortman

# =============================================================================
# Beschrijving van de sheet
# =============================================================================
- 19e eeuwse waterstandsregistraties van zes kuststations zijn verkregen 
  van de RWS Servicedesk
- Per station zijn twee bestanden geleverd met deels overlappende data
- We willen deze data in dezelfde structuur vastleggen als de data die
  regulier van Waterinfo wordt gedownload
- De sheet verondersteld dat er een database-structuur voor RWS-data is
  aangemaakt in normaal-vorm
# =============================================================================
# Gebruikte bronnen
# =============================================================================
1. Meetgegevens vanaf 1900: https://waterinfo.rws.nl <br>
2. Meetgegevens voor 1900: mailwisseling met de RWS Servicedesk, voorjaar 2019

# =============================================================================
# Stappen
# =============================================================================
0. Importeer modules
1. Stel werkdirectory in
2. Haal lijst met te verwerken bestanden op
3. Loop in een cyclus alle bestanden af:
    3a. Lees in
    3b. Voeg locatiecode toe
    3c. Schrijf naar database
    3d. Verplaats bestand naar map "verwerkt"
# =============================================================================
# Open issues
# =============================================================================
- Instellen datapad als systeemvariabele

# =============================================================================
# Risico's
# =============================================================================
 - Collegiale controle ontbreekt
"""
#%% 0. Import modules
import pandas as pd
import os
import sqlite3 as sq
import datetime as dt
import hvec_support.sqlite as hvsq


def get_earliest_date():
  """ 
  Avoid importing overlapping data by getting the
  earliest date present in the old data
  """
  sql = 'SELECT tijd FROM "RWS_Waterinfo" WHERE naam = "%s" '%station
  date = pd.read_sql(sql, cnxn).min().squeeze()
  return date

os.chdir(os.getenv('DATAPATH') + r'/downloadspecs')

#%% 20. Connect to database
cnxn = sq.connect('../RWS_data.db', detect_types = True)
#crsr = cnxn.cursor()

#%% 30. Get list of files
print("Create file list")
file_list = []
for file in os.listdir():
    if ((file.endswith('.txt'))):
        file_list.append(file)
        print(file)

#%% 4. Cycle over all available files
for file in file_list:
    # Determine name of tide station
    f = open(file)
    station = f.readline()
    station = station.strip('\n')
    print(station)
    
    # Skip lines until date is found for the first time
    skip_cnt = 1
    while True:
        string = f.readline()
        skip_cnt = skip_cnt + 1
        if string.startswith('01-'):
            skip_cnt = skip_cnt - 1
            break
    f.close() # Close file
    
    # Now read data, knowing the lines to skip
    df = pd.read_csv(file, skiprows = skip_cnt, delim_whitespace = True,
                     parse_dates = [[0, 1]],
                     usecols = [0, 1, 3]
                     )
    
    #%% Add a few additional columns
    df.columns = ['tijd', 'waarde']
    df["naam"] = station
    df["bron"] = 'Historische waterstandsdata. Verkregen van RWS DID '
    'in het voorjaar van 2019 door H.G. Voortman'
    df["grootheid"] = 'WATHTE'
    df["eenheid"] = 'cm'
    df["kwalico"] = 'Historische data'
    df["statuswaarde"] = 'Niet beschikbaar'
    df["meetapparaat"] = 999
    df["bemonsteringsapparaat"] = 999
    df['year'] = df['tijd'].dt.date
    df['tepoch_dy'] = (df["tijd"]-dt.datetime.utcfromtimestamp(0)).dt.total_seconds()/86400.

    date_early = get_earliest_date() # Earliest date in data already downloaded
    #df = df[df['tijd'] < date_early]

    df.to_sql("RWS_Waterinfo", cnxn, if_exists = 'append', index = False)
    print(file)
    
    #%% Move file
    #os.rename(file, r"../verwerkte downloads/" + file)
    
    #%% Update log
    dt_today = dt.date.today()
    bron = 'RWS'
    note = 'Bestand '+file+' geimporteerd'
    entry = pd.DataFrame([dt_today, bron, note])
    entry = entry.transpose()
    entry.columns = ["Date", "Source", "Note"]
    entry.to_sql("Logboek_databeheer", cnxn, if_exists = 'append', 
                 index = False)

print("Remove doubles and vacuum")
sql = (
        "DELETE FROM 'RWS_Waterinfo' "
        "WHERE rowid NOT IN ("
            "SELECT MIN(rowid) " 
            "FROM 'RWS_Waterinfo' " 
            "GROUP BY naam, tijd)"
            )
    
cnxn.execute(sql)
cnxn.commit()
#cnxn = sq.connect('../RWS_data.db')
cnxn.execute("VACUUM")
cnxn.close()
# End script