import requests
import pandas as pd

from .config.teams import teams, playoff_teams

_YEAR = '2020'

def main(year, output_file=False):
    current_year_playoff_teams = playoff_teams[year]
    playoff_team_attrs = {team: attrs for team, attrs in teams.items() if team in current_year_playoff_teams}

    rosters = []
    for key, val in playoff_team_attrs.items():
        url = f'https://www.pro-football-reference.com/teams/{key}/{_YEAR}_roster.htm'
        print(url)
        page = requests.get(url)
        df = pd.read_html(page.text.replace('<!--',''))[1]
        df = df[df['Pos'].isin(['WR','TE','QB','RB','FB','K','RB/WR'])][['Player','Pos','G']]
        df['Team'] = val['teamFull']
        df['TeamMascot'] = df['Team'].apply(lambda x: x.split(' ')[-1])
        df['TeamShort'] = val['teamShort']
        df['TeamKey'] = key.upper()
        rosters.append(df)
        
    df_combined = pd.concat(rosters)
    df_combined.columns = [c.lower() for c in df_combined.columns]

    if output_file:
        df_combined.to_csv(f'datasets/rosters{_YEAR}.csv', index = False)
        print("Output File Successfully Created!")

    return df_combined


if __name__ == "__main__":
    df = main(_YEAR, output_file=True)
    print(df)
