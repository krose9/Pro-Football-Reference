import requests
import pandas as pd

def renameColumns(string):
    unname_str = 'Unnamed:'
    mapping = {
        'Tm':'Team',
    }
        
    #Unnamed strings to blank
    if unname_str in string:
        string = ''
        
    #Map renamed strings
    if string in mapping.keys():
        return mapping[string]
    else:
        return string


def getSeasonStats(year):
    url = f'https://www.pro-football-reference.com/years/{year}/fantasy.htm'
    print('Getting data from: {}'.format(url))
    page = requests.get(url)
    tbl = pd.read_html(page.text)[0]

    if isinstance(tbl.columns, pd.core.indexes.multi.MultiIndex):
            l1 = [renameColumns(x) for x in tbl.columns.get_level_values(0)]
            l2 = [renameColumns(x) for x in tbl.columns.get_level_values(1)]
            tbl.columns = [parent+child for parent, child in zip(l1,l2)]

    tbl = tbl[tbl['Player'] != 'Player']

    return tbl


def main(year):
    out = getSeasonStats(year)
    out.to_csv(f'datasets/FantasySeasonStats_{year}.csv', index = False)


if __name__ == "__main__":
    main(2020)