"""
Nathan Deininger, Makhayla Icard, Sloan Ritter
DSC 200-001 Fall 2023 Data Wrangling
Lab 5 Part 1
Explanation: This program extracts data from a PDF file containing
    UN statistics about the prevalence of different categories of child
    abuse in all the world's countries. The data is output into a CSV
    file.
Note: This code was written using PyPDF2.8.1, any 3.x.x versions will NOT work!
"""

# Library Imports
from csv import writer
import PyPDF2

#Set data file name
fileName = "data/Table9.pdf"

#Open PDF, begin data extraction
with open(fileName, "rb") as pt:
    text = PyPDF2.PdfReader(pt)

    entries = []
    #Filter and sort data into useful format
    for pg_num, page in enumerate(text.pages):
        sample_text = (page.extractText().replace("\n   ", ' ').replace('TABLE 9    CHILD PROTECTION', '')
                       .replace('TABLE 9      CHILD PROTECTION>>', '').replace(' y ', ' ')
                       .replace(' n ', ' ').replace(' x ', ' ').replace(' v ', ' ')
                       .replace(' x,y ', ' ').replace('   ', ' ').replace('    ', ' ').
                       replace('  ', ' ')).split("\n")
        if pg_num == 0:
            entries.append(sample_text[1])
        else:
            entries.append(sample_text[2])

    #Extract all of the country names from the data
    countries = []
    country = ""
    for entry in entries:
        for charIndex, char in enumerate(entry):
            if ((not char.isalpha() and char != ' ' and char != ')' and char != '(' 
                 and char != '\'' and char != '-' and char != '’') or char == '–'):
                if country:
                    countries.append(country)
                country = ""
            else:
                country+= char
    
    filtered_countries = []
    for country in countries:
        if country != ' ':
            filtered_countries.append(country.strip())
    
    #Extract all of the 14 values for each of the countries
    country_values = []
    value = ""
    for entry in entries:
        for char in entry:
            if (char.isalpha() or char == ' '):
                if value:
                    country_values.append(value)
                value = ""
            else:
                value += char

    filtered_country_values = []
    for value in country_values:
        if value != '(' and value != ')' and value != '’' and value != '-':
            filtered_country_values.append(value)

    pt.close()

# Define header row and create list to store CSV rows
header = ["CountryName", "CategoryName", "CategoryTotal"]

# Create list containing 14 category names
categoryNames = ["Child Labor (%) - Total", "Child Labor (%) - Male", "Child Labor (%) - Female",
                 "Child Marriage (%) - By 15", "Child Marriage (%) - By 18", "Birth Registration (%) - Total",
                 "Female Genital Mutilation (%) - Women", "Female Genital Mutilation (%) - Girls",
                 "Female Genital Mutilation (%) - Support For Practice", "Justification of Wife Beating (%) - Male",
                 "Justification of Wife Beating (%) - Female", "Violent Discipline (%) - Total",
                 "Violent Discipline (%) - Male", "Violent Discipline (%) - Female"]

# Open CSV Output file
with open("group_1_Lab5.csv", "w", newline='') as wFilePtr:
    # Write new rows to CSV file
    writerObj = writer(wFilePtr)
    writerObj.writerow(header)

    #Create rows to write to CSV
    rows = []
    valueNum = 0
    for country in filtered_countries:
        newRow  = []
        for i in range(14):
            #Filter out junk data and keep relevant entries
            if (filtered_country_values[valueNum] != '0' and filtered_country_values[valueNum] != '–'):
                newRow.append(country)
                newRow.append(categoryNames[i])
                newRow.append(filtered_country_values[valueNum])
                rows.append(newRow)
                newRow = []
            valueNum+=1

    #Write the rows to the CSV file
    writerObj.writerows(rows)

    # Close CSV file
    wFilePtr.close()

# Print number of rows
print("Number of rows: {} (not including header)".format(len(rows)))
