"""
Nathan Deininger, Makhayla Icard, Sloan Ritter
DSC 200-001 Fall 2023 Data Wrangling
Lab 7 Parts 2 & 3
Explanation: This program implements the solution to parts 2 and 3 of Lab 7. This code
             has two different functions, each corresponding to parts 2 and 3, respectively.
             The function for part two reads from https://toscrape.com/ and saves the content
             of one of the pages to a csv file called group_1_task2.csv. The function for part 3
             reads from https://vincentarelbundock.github.io/Rdatasets/datasets.html and
             https://realpython.github.io/fake-jobs/ and stores the contents of each page into their
             own CSV files, while also printing the number of rows and columns to the screen.
"""
import requests as req
import pandas as pd
from bs4 import BeautifulSoup
import random as rd
import os

# Set directory to where this Python script is to avoid weird errors
script_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_directory)


def part_two():
    # Get page from website
    page = req.get('https://books.toscrape.com/')
    # Extract the content
    pageContent = page.content
    soup = BeautifulSoup(pageContent, 'html.parser')
    # Find all job listings with the specified class
    jobElements = soup.find_all("li", class_="col-xs-6 col-sm-4 col-md-3 col-lg-3")
    header = ["Title", "Price", "Rating", "URL"]
    rows = []
    # Iterate through each job element and extract relevant information
    for jobElement in jobElements:
        newRow = []
        titleAnchor = jobElement.find('a', title=True)
        title = titleAnchor['title']
        price = jobElement.find('p', class_='price_color').text.strip() 
        rating = jobElement.find('p', class_='star-rating')['class'][1] 
        url = titleAnchor['href']
        # Add extracted data to newRow
        newRow.append(title)
        newRow.append(price)
        newRow.append(rating)
        newRow.append(url)
        rows.append(newRow)

    # Create a DataFrame using extracted data and header
    df = pd.DataFrame(rows, columns=header)
    # Write the DataFrame to a CSV file
    df.to_csv(' group_1_task2.csv', index=False)


def part_three_a():
    url_a = "https://vincentarelbundock.github.io/Rdatasets/datasets.html"
    page1 = req.get(url_a)
    soup = BeautifulSoup(page1.text, 'html.parser')

    # Store header in a listen
    tableHeader = soup.find('tr', class_='firstline').find_all('th')
    header = []
    for item in tableHeader:
        header.append(item.text.strip())
    
    # Get all the rows
    rows = []
    allRows = soup.find_all('tr')[1:]  # Be sure to skip first row or it gets weird
    for row in allRows:
        # Find all the td elements in the row
        rowCells = row.find_all('td', class_='cellinside')
        if rowCells:
            newRow = []
            # Get the text from each cell
            for cell in rowCells:
                if cell.get_text().strip() != "CSV" and cell.get_text().strip() != "DOC":
                    newRow.append(cell.get_text().strip())
            # Only append rows that contain data
            if newRow:
                # Get the URLs from the cells
                for aTag in row.find_all('a'):
                    href = aTag.get('href')
                    newRow.append(href)
                rows.append(newRow)

    # Write the data to a CSV with pd dataframe
    df = pd.DataFrame(rows, columns=header)
    df.to_csv('group1_Lab7_part3a.csv', index=False)

    # Download a random linked CSV file from the dataset
    randUrlIndex = rd.randint(0,len(rows))
    url = rows[randUrlIndex][10]
    randCSVdata = req.get(url)
    csvData = randCSVdata.text
    # Now you can save or process the CSV data
    with open('group1_Lab7_part3a_randomCSVData.csv', 'w') as csvFile:
        csvFile.write(csvData)
        csvFile.close()
    # Output number of rows & cols
    print("The total number of rows for part 3a: {}".format(len(rows)))
    print("The total number of cols for part 3a: {}".format(len(header)))


def part_three_b():
    # Define URL to scrape
    url_b = "https://realpython.github.io/fake-jobs/"
    # Get the contents of the page and parse through it
    page2 = req.get(url_b)
    soup2 = BeautifulSoup(page2.content, "html.parser")

    results = soup2.find(id="ResultsContainer")

    # Find all the job listings within "ResultsContainer"
    job_elements = results.find_all("div", class_="card-content")
    rows = []
    header = ["job_title", "company_name", "city", "state", "posting_date"]
    # Iterate through each job element and extract relevant information
    for job_element in job_elements:
        elements = []
        title = job_element.find("h2", class_="title")
        company = job_element.find("h3", class_="company")
        location = job_element.find("p", class_="location")
        # Split the city and state
        city, state = location.text.split(",")
        date = job_element.find("p", class_="is-small has-text-grey" )
        # Add extracted data to elements
        elements.append(title.text.strip())
        elements.append(company.text.strip())
        elements.append(city.strip())
        elements.append(state.strip())
        elements.append(date.text.strip())
        rows.append(elements)
    # Create a DataFrame using extracted data and header
    df2 = pd.DataFrame(rows, columns=header)
    # Write DataFrame to CSV file
    df2.to_csv("group1_lab7_part3b.csv", index= False)

    # Print total number of rows and columns in the DataFrame
    print("The total number of rows for part 3b: {}".format(len(rows)))
    print("The total number of cols for part 3b: {}".format(len(header)))


def main():
    part_two()
    part_three_a()
    part_three_b()


main()