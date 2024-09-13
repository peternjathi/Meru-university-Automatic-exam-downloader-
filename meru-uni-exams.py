import requests
from bs4 import BeautifulSoup

url = "https://www.meru.ac.ke/exams"  # Replace with the actual URL

response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

# Find exam information based on HTML structure
exams = soup.find_all("div", class_="exam-info")

for exam in exams:
    date = exam.find("span", class_="exam-date").text
    time = exam.find("span", class_="exam-time").text
    venue = exam.find("span", class_="exam-venue").text
    # Store the extracted information in a CSV file or database
    print(f"Date: {date}, Time: {time}, Venue: {venue}")
