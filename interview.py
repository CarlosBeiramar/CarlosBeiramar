import requests
import pandas
import os

API_laureate = "https://api.nobelprize.org/v1/laureate.json"
API_countries = "http://api.nobelprize.org/v1/country.json"

'''
    check if the APIS are available, if the status code is 200
'''
def check_apis():
    try:
        output_laureate = requests.get(API_laureate)
        laureate = output_laureate.json()
    except:
        raise Exception(f"ERROR: {API_laureate} status code: {requests.get(API_laureate).status_code}\n")
    try:
        output_country = requests.get(API_countries)
        countries = output_country.json()
    except:
        raise Exception(f"ERROR: {API_countries} status code: {requests.get(API_countries).status_code}\n")
    return laureate, countries


'''
    receives a list of dictionaries and filter string
    return string with all elements separated by ;
'''
def get_filters(l,s):
    output = set()
    for dictionary in l:
        output.add(dictionary.get(s))
    return ';'.join(output)


'''
    get country's name using the bornCountryCode of each row in the laureate dataframe
'''
def get_country(df_countries ,countrycode):
    for _, row in df_countries.iterrows():
        if 'code' in row["countries"] and row["countries"]['code'] == countrycode:
            return row['countries']['name']
    return "CountryNotFound"


'''
    this function receives the dataframes as parameter
    and return a result dataframe with the specific columns
'''
def edit_dataframes(laureate, countries):

    df_laureate = pandas.DataFrame(laureate.get("laureates"))
    df_countries = pandas.DataFrame(countries)

    # Create name column
    if "firstname" and "surname" in df_laureate.columns:
        df_laureate["name"] = df_laureate["firstname"] + " " +  df_laureate["surname"]
    else:
        raise Exception("Column firstname or surname not found\n")

    if "prizes" in df_laureate.columns:
        # Create unique_prize_years column
        df_laureate["unique_prize_years"] = df_laureate["prizes"].apply(lambda x : get_filters(l = x, s = "year"))
        # Create unique_prize_categories column
        df_laureate["unique_prize_categories"] = df_laureate["prizes"].apply(lambda x : get_filters(l = x, s = "category"))
    else:
        raise Exception("Column prizes not found\n")


    # Create country column
    if "bornCountryCode" in df_laureate.columns:
        df_laureate["country"] = df_laureate["bornCountryCode"].apply(lambda x : get_country(df_countries, x))

    # result dataframe with specific coloumns
    result = df_laureate[['id', 'name', 'born', 'unique_prize_years', 'unique_prize_categories', 'gender', 'country']]
    return result

'''
    receives one dataframe and write it in the csv file
    after checking if the file is empty or not
'''
def write_to_csv(result):

    if os.path.exists("output.csv") and os.stat("output.csv").st_size > 0:
        with open("output.csv", "w+") as file:
            file.truncate(0)
            result.to_csv(file, index=False)
    else:
        with open("output.csv", "w") as file:
            result.to_csv(file, index=False)

def main():
   laureate, countries = check_apis()
   result = edit_dataframes(laureate, countries)
   write_to_csv(result)

main()