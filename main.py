"""
User will input 2 information:
    1. region url with list of the towns
        - list of regions you can find here (CZ only): https://volby.cz/pls/ps2017nss/ps3?xjazyk=CZ
        - you choose the region by clicking on "X" in "Vyber obce" column
    2. name of the csv file for data saving (without suffix ".csv")
"""

import requests
from bs4 import BeautifulSoup
import csv
import sys

def main():
    print(63 * "=")
    print("====================== WELCOME TO MY APP ======================")
    print(63 * "=")
    print("Do you want to know results of the 2017 elections in you region?")
    print("Please first visit https://volby.cz/pls/ps2017nss/ps3?xjazyk=CZ")
    print("And choose your region by clicking on 'X' in 'Vyber obce' column.")
    print(63 * "=")
    region_url = input("Now just copy the link and paste it here:")
    print(63 * "=")
    file_name = input("Please write a name of the file for data saving (no '.csv' suffix):")
    print(63 * "=")

    f = open(file_name + ".csv", mode="w")
    f_writer = csv.writer(f, delimiter=";")

    # base URL
    URL = "https://volby.cz/pls/ps2017nss/"
    web = requests.get(region_url)
    soup = BeautifulSoup(web.text, "html.parser")
    all_towns = soup.find_all("td", {'class': 'cislo'})
    statement_header = False

    for child in all_towns:
        # the list is going to be a row in csv file
        town_election_data = []
        town_election_data = get_id_and_name(child, town_election_data)
        town_soup = get_town_soup(URL, child)

        # get brutto results
        town_results = town_soup.find(id="ps311_t1")
        town_election_data = get_voters_envelopes_valid_votes(town_results, town_election_data)

        # get parties in the town
        parties = town_soup.find(id="inner").find_all("tr")

        # append votes for the parties
        town_election_data = get_party_votes(parties, town_election_data)

        if not statement_header:
            column_names = ["ID", "Name", "Registered voters", "Envelopes", "Valid Votes"]
            for line in parties:
                if not line.find("th"):
                    column_names.append(line.find_all("td")[1].string)
            f_writer.writerow(column_names)
            statement_header = True

        f_writer.writerow(town_election_data)

    f.close()
    print("DONE! Have a nice day.")

def get_id_and_name(child, list):
    list.append(child.find("a").string)
    list.append(child.parent.find_all()[2].string)
    return list

def get_town_soup(URL, child):
    town_url = requests.get(URL + child.find("a").attrs["href"])
    return BeautifulSoup(town_url.text, "html.parser")

def get_voters_envelopes_valid_votes(town_results, list):
    list.append(town_results.find("td", {"class": "cislo", "headers": "sa2"}).string)
    list.append(town_results.find("td", {"class": "cislo", "headers": "sa3"}).string)
    list.append(town_results.find("td", {"class": "cislo", "headers": "sa6"}).string)
    return list

def get_party_votes(parties, list):
    for line in parties:
        if not line.find("th"):
            list.append(line.find_all("td", {"class": "cislo"})[1].string)
    return list

if __name__ == '__main__':
    sys.exit(main())