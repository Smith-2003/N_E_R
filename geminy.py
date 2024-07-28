# Import the Python SDK
import google.generativeai as genai
genai.configure(api_key="AIzaSyAIMwJrsdQ5GC3BaKH7xFJYyK14Ara-x_w")

model = genai.GenerativeModel('gemini-pro')

import re

student_name_pattern = r"Student Name - (.*)"
organization_pattern = r"Organization - (.*)"
date_from_pattern = r"Date from - (.*)"
date_to_pattern = r"Date to - (.*)"

sample_format='''
Student Name - Falgun Patil

Organization - International Institute of Information Technology

Date from - 5 January - 2024

Date to - 25 February - 2024
'''


text='''
TATA

Nikita Khamgal
ESG Job Simulation

Certificate of Completion
April 25th, 2024

Over the period of March 2024 to April 2024 Nikita khamgal has completed practical tasks in:

Understanding and analysing client needs
Understand and analyse the client

Assess sustainability solutions through a comparative analysis
Present a fitment matrix to the client

Enrolment Verification Code ZnSdrnLBPs,

PQ | User Verification Code C9tUgaqZwaSfdsMD j Issued by Forage

Tom Brunskill
CEO, Co -Founder of
Forage'''


response = model.generate_content(f"Extract entities from {text} use this sample format{sample_format} make sure the output folows the sample format exactly")
print(response.text)


student_name = re.search(student_name_pattern, response.text).group(1)
organization = re.search(organization_pattern, response.text).group(1)
date_from_month, date_from_year = re.search(date_from_pattern, response.text).groups()
date_to_month, date_to_year = re.search(date_to_pattern, response.text).groups()

print(student_name)  # Output: Falgun Patil
print(organization)  # Output: International Institute of Information Technology
print(date_from_month, date_from_year)  # Output: January 2024
print(date_to_month, date_to_year)  # Output: February 2024