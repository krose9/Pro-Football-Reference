from bs4 import BeautifulSoup
import urllib.request
import requests
import pandas as pd
import numpy as np


def getGameLinks(year, week_num, base_url='http://www.pro-football-reference.com/'):
    """
    1) Requests url concatenated from the base_url, year, and week number.
    2) Collects all link URLs where the display text is 'Final'. This assumes
        that these are all links to individual games from that week / year.
    """
    url = base_url+'years/'+str(year)+'/week_'+str(week_num)+'.htm'
    print('Requesting: {}'.format(url))
    request = urllib.request.Request(url)
    html = urllib.request.urlopen(request).read()
    soup = BeautifulSoup(html, 'lxml')

    game_links = []
    for i in soup.findAll('a'):
        if i.text == 'Final':
            game_links.append(base_url+i['href'])
    return game_links


def getGameResults(game_link, table_name):
    page = requests.get(game_link)
    df = pd.read_html(page.text.replace('<!--', ''), attrs={'id': table_name})
    return df


def getGamePage(game_link):
    page = requests.get(game_link)
    return page.text.replace('<!--', '')


def renameColumns(string):
    unname_str = 'Unnamed:'
    mapping = {
        'Def Interceptions': 'Interceptions',
        'Tm': 'Team',
        'Sk': 'Sack'
    }

    #Unnamed strings to blank
    if unname_str in string:
        string = ''

    #Map renamed strings
    if string in mapping.keys():
        return mapping[string]
    else:
        return string


def getTableData(page, table_names):
    data = {}
    for tbl in table_names:
        df = pd.read_html(page, attrs={'id': tbl})[0]

        #Rename columns and flatten multi-index
        if isinstance(df.columns, pd.core.indexes.multi.MultiIndex) == True:
            l1 = [renameColumns(x) for x in df.columns.get_level_values(0)]
            l2 = [renameColumns(x) for x in df.columns.get_level_values(1)]
            df.columns = [parent+child for parent, child in zip(l1, l2)]

        #Drop unnecessary rows
        if tbl in ['player_offense', 'player_defense']:
            df.drop(labels=df[df['Player'] == 'Player'].index,
                    axis=0, inplace=True)
            df.dropna(subset=['Player'], inplace=True)

        #Standardize column naming coventions
        if tbl == 'scoring':
            col_names = df.columns.tolist()
            col_names[-2], col_names[-1] = 'Away', 'Home'
            df.columns = col_names
            # df = df[df['Detail'].str.contains('field goal')]

        if tbl == 'pbp':
            df = df.loc[:, ['Location', 'Detail']]
            df = df[~df['Detail'].str.contains('Quarter')]
            df = df[~df['Detail'].str.contains('Detail')]
            df = df[df['Detail'].str.contains(
                'field goal|touchdown|field goal|conversion succeeds|extra point')]

        # if tbl == 'player_defense':
        #     print(df.columns)

        data[tbl] = df
    return data


if __name__ == "__main__":
    year = 2020
    week = 19
    game_links = getGameLinks(year, week)
    print(game_links)

    tables = ['player_offense', 'player_defense', 'scoring', 'pbp']

    output = {}
    for gm in game_links:
        print(f'Processing: {gm}')
        page = getGamePage(gm)
        data = getTableData(page, tables)

        for tbl in data.keys():
            if tbl in output.keys():
                output[tbl].append(data[tbl])
            else:
                output[tbl] = [data[tbl]]

    for key in output.keys():
        df_combined = pd.concat(output[key])
        df_combined.to_csv(f'datasets/{key}_{year}wk{week}.csv', index=False)
