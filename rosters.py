import os
import requests
import pandas as pd
from prompt import prompt_save_location
from config.teams import teams, playoff_teams


def get_rosters(year, output_file=True):
    """
    Webscrape playoff team rosters from Pro Football Reference

    Params
        year - a string value for the season of interest
        output_file - a boolean to determine if a file gets saved
    
    Return
        Pandas dataframe with roster data
    """
    year = str(year)

    # Get this year's playoff teams from config file
    current_year_playoff_teams = playoff_teams[year]

    # Get team attributes from config file
    playoff_team_attrs = {team: attrs for team, attrs in teams.items() if team in current_year_playoff_teams}

    # Positions of interest
    eligible_pos = ['WR', 'TE', 'QB', 'RB', 'FB', 'K', 'RB/WR']

    # For each playoff team get roster data from Pro Football Reference
    rosters = []
    for key, val in playoff_team_attrs.items():
        url = f'https://www.pro-football-reference.com/teams/{key}/{year}_roster.htm'
        print(f"Fetching: {url}")
        page = requests.get(url)
        df = pd.read_html(page.text.replace('<!--',''))[1] # Replace the value that interrupts HTML parsing
        df = df[df['Pos'].isin(eligible_pos)][['Player', 'Pos', 'G']]
        df['Team'] = val['teamFull'] # Add full team name ex: Buffalo Bills
        df['TeamMascot'] = df['Team'].apply(lambda x: x.split(' ')[-1]) # Mascot only
        df['TeamShort'] = val['teamShort'] # Abbreviated team name
        df['TeamKey'] = key.upper() # Pro football reference abbrev, these are weird
        rosters.append(df)
        
    df_combined = pd.concat(rosters)
    df_combined.columns = [c.lower() for c in df_combined.columns]

    if output_file:
        save_dir = prompt_save_location()
        file_path = os.path.join(save_dir, f"rosters{year}.csv")
        df_combined.to_csv(file_path, index = False)
        print("Output File Successfully Created!")
        print(f"Destination: {file_path}")

    return df_combined


if __name__ == "__main__":
    year = '2020'
    df = get_rosters(year, output_file=True)
    print(df)
