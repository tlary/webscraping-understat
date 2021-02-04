from footyutils import *
import sqlite3

def run():
    browser = initialize_browser()
    bundesliga = scrape_league("Bundesliga", browser=browser, seasons=[2014, 2015, 2016, 2017, 2018, 2019])
    return bundesliga

if __name__ == "__main__":
    bundesliga = run()
    bundesliga.to_csv("bundesliga.csv")

bundesliga = pd.read_csv("bundesliga.csv")
bundesliga = bundesliga.drop("Unnamed: 0", 1)

# create / connect to database
con = sqlite3.connect("./soccerData.db")
# save pandas dataframe in soccerData.db file
bundesliga.to_sql("soccerData.db", con)

