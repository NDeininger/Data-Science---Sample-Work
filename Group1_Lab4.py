"""
Group 1 - Nathan Deininger, Makhayla Icard, Sloan Ritter
DSC 200-001 Data Wrangling
Fall 2023
Explanation: This code is intended to process an Excel file containing UN statistics about the prevelance
      of different categories of child abuse in all the world's countries. The data is to be processed
      using either the openpyxl or xlrd libraries, and the data should be output into a CSV file.
      The format for the CSV data output is as follows in this example:
      CountryName          CategoryName           CategoryValue
      -----------------------------------------------------------
      Afghanistan        Child Labor - total           x
      Afghanistan        Child Labor - male            x
      Afghanistan        Child Labor - female          x
      Afghanistan        Child Marriage - by 15        X
      ...Remaining Afghanistan category rows...
      Albania            Child Labor - total           x
      ...
      ...Repeat for all countries
"""

# Library Imports
import openpyxl as op
from csv import writer

# Open Excel File, get worksheet from workbook
wb = op.load_workbook("Lab4Data.xlsx", read_only=True, data_only=True)
ws = wb["Table 9 "]

# Define header row & Create list to store CSV Rows
header = ["CountryName", "CategoryName", "CategoryTotal"]
rows = []

# Create a list containing the 14 possible category names
categoryNames = ["Child Labor (%) - Total", "Child Labor (%) - Male", "Child Labor (%) - Female",
                 "Child Marriage (%) - By 15", "Child Marriage (%) - By 18", "Birth Registration (%) - Total",
                 "Female Genital Mutilation (%) - Women", "Female Genital Mutilation (%) - Girls",
                 "Female Genital Mutilation (%) - Support For Practice", "Justification of Wife Beating (%) - Male",
                 "Justification of Wife Beating (%) - Female", "Violent Discipline (%) - Total",
                 "Violent Discipline (%) - Male", "Violent Discipline (%) - Female"]

counter = 15
# Top level loop - iterate through each country
while counter <= 211:
    curRow = ws[str(counter)]
    # Inner level loop - iterate through the 14 possible values
    #   *Note: Cells that contain values are every other one starting at column E (index 4)
    for cell in range(4, 32, 2):
        newRow = []
        # Check to see if cell value is empty '0' or '–' (special en dash, not normal -), if so, pass loop iteration
        if '–' == curRow[cell].value or '– ' == curRow[cell].value or ' –' == curRow[cell].value or ' – ' == curRow[cell].value or curRow[cell].value == 0:
            continue
        else:  
            # write country to new row
            newRow.append(curRow[1].value)
            # write category name to new row from categoryNames
            index = (cell - 4) // 2
            newRow.append(categoryNames[index])
            # get category value, write to new row
            newRow.append(curRow[cell].value)
            # Append new row to rows list
            rows.append(newRow)
    counter += 1

# Open CSV Output file
with open("Group1_Output.csv", 'w', newline='') as wFilePtr:
    # Write new rows to CSV file
    writerObj = writer(wFilePtr)
    writerObj.writerow(header)
    writerObj.writerows(rows)
    # Close Csv file
    wFilePtr.close()

# Close Excel file
wb.close()

#Print number of rows
print("The number of rows: " + str(len(rows)))