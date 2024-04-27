"""
Nathan Deininger, Makhayla Icard, Sloan Ritter
DSC 200-001 Fall 2023 Data Wrangling
Lab 6 Parts 1 & 2
Explanation: This program implements two data operation functions and a menu function to complete Lab 6.
             Specifically, function1 takes our 3 data files from Lab 5 and merges them together,
             ensuring they are merged to an appropriate level of granularity to make the 3 datasets
             compatible with each other. Function 2 takes the provided Lab6Data and cleans it, which 
             includes checking for repeated observations and features, inconsistent data, and others.
             Finally, a menu function is provided to allow the user to choose which function they 
             want to use. 
"""
# Library Imports
import pandas as pd
import os


# Implements the solution to Part 1 of Lab6
def function1():
    # Ensure base directory is directory of python code
    script_directory = os.path.dirname(os.path.realpath(__file__))
    os.chdir(script_directory)

    # Extract personal income per capita data
    countyPerCapitaData_Header = ["Area", "Per capita personal income 2019 (dollars)",
                                  "Per capita personal income 2020 (dollars)",
                                  "Per capita personal income 2021 (dollars)", "County rank in state"]
    countyPerCapitaData = pd.read_excel("part1_data/countypercapitaincomeData.xlsx", sheet_name="Table 1", usecols="A:E", skiprows=5, nrows=3217)
    countyPerCapitaData.columns = countyPerCapitaData_Header
    countyPerCapitaData['State'] = ""

    # Add state labels to each row
    curState = ""
    for index, row in countyPerCapitaData.iterrows():
        if row["County rank in state"] == "--" and row["Area"] != "Valdez-Cordova Census Area2":
            curState = row["Area"]
        else:
            row['State'] = curState
    countyPerCapitaData = countyPerCapitaData.replace('', '--')
    countyPerCapitaData.dropna(subset=['Area'], inplace=True)

    # Extract education data
    colsToKeep = ["State Name", "State", "Area name", "Less than a high school diploma, 2017-21",
                  "High school diploma only, 2017-21", "Some college or associate's degree, 2017-21",
                  "Bachelor's degree or higher, 2017-21",
                  "Percent of adults with less than a high school diploma, 2017-21",
                  "Percent of adults with a high school diploma only, 2017-21",
                  "Percent of adults completing some college or associate's degree, 2017-21",
                  "Percent of adults with a bachelor's degree or higher, 2017-21"]
    educationData = pd.read_excel("part1_data/Education.xlsx", sheet_name="Education 1970 to 2021", skiprows=3,
                                  nrows=3206)

    # Add state labels to each row
    educationData['State Name'] = "--"
    curStateName = ""
    curState = ""
    for index, row in educationData.iterrows():
        if row["State"] != curState:
            curState = row["State"]
            curStateName = row["Area name"]
        else:
            educationData.loc[index, 'State Name'] = curStateName

    educationData = educationData[colsToKeep].copy()
    educationData.drop(0, inplace=True)
    educationData['Area name'] = educationData['Area name'].str.replace(' County', '').str.replace(' Parish', '')

    # Extract Unemployment Data
    unemploymentData = pd.read_excel("part1_data/unemploymentData.xlsx", nrows=3142)
    unemploymentData.drop(columns=["Local_Area_Unemployment_Statistics_Code", "State_FIPS_Code", "County_FIPS_Code",
                                   "Data_Collection_Period"], inplace=True)
    unemploymentData = unemploymentData.rename(columns={'State': "area name"})
    unemploymentData['area name'] = unemploymentData['area name'].str.replace(' County', '').str.replace(' Parish', '')
    unemploymentData['State_Abbreviation'] = unemploymentData['State_Abbreviation'].str.strip()

    # Merge education and unemployment data together
    mergedData = pd.merge(educationData, unemploymentData, left_on='Area name', right_on='area name', how='inner')
    mergedData = mergedData[mergedData['State'] == mergedData['State_Abbreviation']]
    mergedData.drop(['State', 'State_Abbreviation', 'area name'], axis=1, inplace=True)

    # Merge with income data
    mergedData = pd.merge(mergedData, countyPerCapitaData, left_on='Area name', right_on='Area', how='inner')
    mergedData = mergedData[mergedData['State'] == mergedData['State Name']]
    mergedData.drop(['Area', 'State'], axis=1, inplace=True)

    mergedData.to_csv("Group1_Lab6_Part1.csv", index=False)


# Implements the solution to Part 2 of Lab6
def function2():
    # Ensure base directory is directory of python code
    script_directory = os.path.dirname(os.path.realpath(__file__))
    os.chdir(script_directory)

    # Get directory of data file, load the dataset
    filePath = input("Enter the file path of your dataset: ")
    lab6Data = pd.DataFrame(pd.read_csv(filePath))

    print("\nThere are {} entries in the initial data file.".format(len(lab6Data)))

    # Drop duplicate columns
    lab6Data.drop(columns=['education_1', 'occupation_1', 'workclass_1'], inplace=True)

    print("\nInitiating data cleaning process")
    print("---------------------------------")

    # Check for and eliminate duplicate entries, while keeping first instance
    print("Searching for duplicate entries...")
    duplicates = lab6Data.duplicated()
    print("{} duplicates detected, dropping them from dataset...".format(duplicates.sum()))
    lab6Data = lab6Data.drop_duplicates().reset_index(drop=True)
    print("{} entries now in the dataset.".format(len(lab6Data)))

    # Check for entries with missing values, and drop all entries missing 1 or more values
    print("\nSearching for entries with missing values...")
    rowsMissingValues = []
    for index, row in lab6Data.iterrows():
        if ' ?' in row.values or row.isna().any():
            rowsMissingValues.append(row)
    rowsMissingValuesDf = pd.DataFrame(rowsMissingValues)
    missingValuesIndex = rowsMissingValuesDf.index.tolist()
    print("{} entries with missing data detected, dropping them from dataset...".format(len(missingValuesIndex)))
    lab6Data.drop(missingValuesIndex, inplace=True)
    print("{} entries now in the dataset.".format(len(lab6Data)))

    print("\nSearching for invalid entries that aren't in the provided enumerated values...")

    # Look for invalid options in non-numerical columns with enumerated values
    validOptions = {
        'workclass': {"Private", "Self-emp-not-inc", "Self-emp-inc", "Federal-gov", "Local-gov", "State-gov",
                      "Without-pay", "Never-worked"},
        'education': {"Bachelors", "Some-college", "11th", "HS-grad", "Prof-school", "Assoc-acdm", "Assoc-voc", "9th",
                      "7th-8th", "12th", "Masters", "1st-4th", "10th", "Doctorate", "5th-6th", "Preschool"},
        'marital_status': {"Married-civ-spouse", "Divorced", "Never-married", "Separated", "Widowed",
                           "Married-spouse-absent", "Married-AF-spouse"},
        'occupation': {"Tech-support", "Craft-repair", "Other-service", "Sales", "Exec-managerial", "Prof-specialty",
                       "Handlers-cleaners", "Machine-op-inspct", "Adm-clerical", "Farming-fishing", "Transport-moving",
                       "Priv-house-serv", "Protective-serv", "Armed-Forces"},
        'relationship': {"Wife", "Own-child", "Husband", "Not-in-family", "Other-relative", "Unmarried"},
        'race': {"White", "Asian-Pac-Islander", "Amer-Indian-Eskimo", "Other", "Black"},
        'sex': {"Female", "Male"},
        'native-country': {"United-States", "Cambodia", "England", "Puerto-Rico", "Canada", "Germany",
                           "Outlying-US(Guam-USVI-etc)", "India", "Japan", "Greece", "South", "China", "Cuba", "Iran",
                           "Honduras", "Philippines", "Italy", "Poland", "Jamaica", "Vietnam", "Mexico", "Portugal",
                           "Ireland", "France", "Dominican-Republic", "Laos", "Ecuador", "Taiwan", "Haiti", "Columbia",
                           "Hungary", "Guatemala", "Nicaragua", "Scotland", "Thailand", "Yugoslavia", "El-Salvador",
                           "Trinadad&Tobago", "Peru", "Hong", "Holand-Netherlands"}
    }

    colsToCheck = ['workclass', 'education', 'marital_status', 'occupation', 'relationship', 'race', 'sex',
                   'native-country']

    # Get rows with invalid options
    invalidRows = []

    # Remove any leading and trailing whitespace
    for col in colsToCheck:
        lab6Data[col] = lab6Data[col].str.strip()

    # Iterate over the columns and check for invalid options
    for index, row in lab6Data.iterrows():
        for col in colsToCheck:
            options = validOptions[col]
            if row[col] not in options:
                invalidRows.append(index)
                break

    # Delete the invalid rows
    lab6Data = lab6Data.drop(invalidRows, axis=0)
    print("{} rows found with invalid entries, dropping them from dataset...".format(len(invalidRows)))
    print("{} entries now in dataset.".format(len(lab6Data)))

    # Print final number of entries
    print("\nData cleaning process complete.")
    print("Final dataset contains {} entries.".format(len(lab6Data)))

    # Write new dataset to csv file
    newFileName = "Group1_Lab6Data_Cleaned.csv"
    print("\nWriting cleaned dataset to {}".format(newFileName))
    lab6Data.to_csv(newFileName, index=False)
    print("Data has been written to new file.")
    print("\nLab6 Part 2 complete!")


# Implements the menu feature
def menu():
    print("Hello, would you like to complete part 1 or part 2 of the lab?")

    # Get user's choice
    choice = input("Please enter 1 or 2: ")

    # Validate the input
    while choice != '1' and choice != '2':
        choice = input("Invalid option, please enter '1' or '2' only: ")

    # Execute the proper function based on the choice
    if choice == '1':
        function1()
    else:
        function2()


menu()
