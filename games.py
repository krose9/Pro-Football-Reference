import os
from bs4 import BeautifulSoup
import urllib.request
import requests
import pandas as pd
import numpy as np
from prompt import prompt_save_location


def _rename_columns(string):
    """
    1) Relabels 'Unnamed:' string created in Pandas multi level index to blank so that names
    can be collapsed and concatenated later.
    2) Relabel statistics
    """
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


def _get_game_links(year, week):
    """
    Collects all link URLs where the display text is 'Final'. This assumes
    that these are all links to individual games from that week / year.
    """
    # Construct the url for a week results page
    base_url = "http://www.pro-football-reference.com/"
    url = f"{base_url}years/{year}/week_{week}.htm"

    # Get page soup
    print('Requesting: {}'.format(url))
    request = urllib.request.Request(url)
    html = urllib.request.urlopen(request).read()
    soup = BeautifulSoup(html, 'lxml')

    # The word final holds the hyperlink to the page box score
    # Get the links
    game_links = []
    for i in soup.findAll('a'):
        if i.text == 'Final':
            game_links.append(base_url+i['href'])

    return game_links


def _get_game_page(game_link):
    """Return the html page text after replacing problem text"""
    page = requests.get(game_link)
    return page.text.replace('<!--', '')


def _get_table_data(page, table_type):
    """
    
    Return:
        A dictionary with table type as a key and the data as the value
    """
    data = {}
    for tbl in table_type:
        df = pd.read_html(page, attrs={'id': tbl})[0]

        #Rename columns and flatten multi-index
        if isinstance(df.columns, pd.core.indexes.multi.MultiIndex) == True:
            l1 = [_rename_columns(x) for x in df.columns.get_level_values(0)]
            l2 = [_rename_columns(x) for x in df.columns.get_level_values(1)]
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

        data[tbl] = df

    return data


def get_games(year, week):

    year = str(year)
    week = str(week)
    table_types = ['player_offense', 'player_defense', 'scoring', 'pbp'] # table_types to iterate

    game_links = _get_game_links(year, week)

    print("All game links:")
    print(game_links,"\n")


    output = {}
    for game in game_links:
        # Get box score page
        print(f'Processing: {game}')
        page = _get_game_page(game)

        # Get dictionary of data table types
        data = _get_table_data(page, table_types)

        # 
        for tbl in data.keys():
            # If key exists (because of anther game processed) then append data frames
            if tbl in output.keys():
                output[tbl].append(data[tbl])
            else:
                output[tbl] = [data[tbl]] # If key not exist, make it

    save_dir = prompt_save_location()
    for key in output.keys():
        # Construct the destination path
        file_path = os.path.join(save_dir, f"{key}_{year}wk{week}.csv")

        df_combined = pd.concat(output[key])
        df_combined.to_csv(file_path, index=False)
        
if __name__ == "__main__":
    get_games(year=2020, week=19)


