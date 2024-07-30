import cv2
import numpy as np
from PIL import Image
import pytesseract
import os
import re
import pandas as pd
import spacy  # Import spaCy library for natural language processing
from spacy.matcher import Matcher  # Import Matcher class from spaCy's matcher module
import google.generativeai as genai
genai.configure(api_key="AIzaSyAIMwJrsdQ5GC3BaKH7xFJYyK14Ara-x_w")

# Set up the Tesseract executable path (adjust the path if necessary)
pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/TesseractOCR/tesseract.exe"
nlp = spacy.load('en_core_web_sm')  # Load English language model
matcher = Matcher(nlp.vocab)  # Initialize Matcher with spaCy's vocabulary
def process_image(image_path):
    # Load the image
    image = cv2.imread(image_path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply sharpening filter
    kernel = np.array([[0, -1, 0], 
                       [-1, 5, -1], 
                       [0, -1, 0]])
    sharpened = cv2.filter2D(gray, -1, kernel)
    
    # Apply edge detection
    edges = cv2.Canny(sharpened, 50, 150, apertureSize=3)
    
    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Sort contours by area (largest to smallest) and take the largest one
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:1]
    
    for contour in contours:
        # Get the bounding box of the largest contour
        x, y, w, h = cv2.boundingRect(contour)
        # Crop the image to the bounding box
        cropped_image = image[y:y+h, x:x+w]
    
    # Convert the cropped image to PIL format for OCR
    cropped_image_pil = Image.fromarray(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB))
    text = pytesseract.image_to_string(image)  # Use cropped image for OCR
    
    return text

# def extract_name(resume_text):
#     """Function to extract name from resume text using spaCy's Matcher."""
    

#     # Define name patterns for Matcher
#     patterns = [
#         [{'POS': 'PROPN'}, {'POS': 'PROPN'}],  # First name and Last name
#         [{'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS': 'PROPN'}],  # First name, Middle name, and Last name
#         [{'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS': 'PROPN'}]  # First name, Middle name, Middle name, and Last name
#     ]

#     for pattern in patterns:
#         matcher.add('NAME', patterns=[pattern])  # Add each pattern to the Matcher

#     doc = nlp(resume_text)  # Process the resume text with spaCy
#     matches = matcher(doc)  # Apply the Matcher to find name patterns

#     for match_id, start, end in matches:
#         span = doc[start:end]  # Get the matched span of text
#         return span.text  # Return the matched text (name)

#     return None  # Return None if no name is found

def extract_entities(text,image_url):
    student_name_pattern = r"Student Name - (.*)"
    organization_pattern = r"Organization - (.*)"
    date_from_pattern = r"Date from - (.*)"
    date_to_pattern = r"Date to - (.*)"
    Title_pattern  = r"Title - (.*)"
    sample_format='''
    Student Name - Falgun Patil

    Organization - International Institute of Information Technology

    Date from - 5 January - 2024

    Date to - 25 February - 2024

    Title - ESG Job Simulation
    '''
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(f"Extract entities from {text} use this sample format{sample_format} make sure the output folows the sample format exactly")
    print(response.text)
    student_name = re.search(student_name_pattern, response.text).group(1)
    organization = re.search(organization_pattern, response.text).group(1)
    date_from = re.search(date_from_pattern, response.text).group(1)
    date_to= re.search(date_to_pattern, response.text).group(1)
    title= re.search(Title_pattern, response.text).group(1)


    # Create a DataFrame
    data = {
        "Name of the student": [student_name if student_name else "none"  ],
        "Industry name": [organization  if organization  else "none" ],
        "Date from": [date_from if date_from else "none" ],
        "Date to": [date_to if date_to else "none" ],
        "Title": [title if title else "none" ],
        "Image URL": [image_url]  # Added Image URL to data dictionary
        # "Single dates": [dates if dates else "none" ],
        # "Durations": [durations if durations else "none" ]  
    }
    df = pd.DataFrame(data)

    # Specify the CSV file name
    csv_file = "entities.csv"
    
    # Write the DataFrame to a CSV file
    if os.path.exists(csv_file):
        df.to_csv(csv_file, mode='a', header=False, index=False)  # Append without header
    else:
        df.to_csv(csv_file, index=False)  # Write with header if file doesn't exist
        
    return csv_file
# def extract_entities(text):
#     # Define regex patterns
#     # company_name_pattern = re.compile(r'\b([A-Z][a-zA-Z]+(?: [A-Z][a-zA-Z]+){0,2})\b')
#     duration_pattern = re.compile(r"from (\d{1,2} [A-Za-z]+ \d{4}) to (\d{1,2} [A-Za-z]+ \d{4})")
#     date_pattern = re.compile(r'\b(\w+ \d{1,2}(?:st|nd|rd|th)?,? \d{4})\b')
#     date_range_pattern = re.compile(r'\b(\w+ \d{4}) to (\w+ \d{4})\b')
#     duration_pattern = re.compile(r'\b(\d+) (week|weeks?)\b', re.IGNORECASE)
#      # Initialize SpaCy and Matcher for company name extraction
#     companies = [
#         "Motion Cut", "Fortinet", "Edu Skills", "Synetic Business School", "TATA",
#         "National Educational Alliance for Technology", "All India Council for Technical Education",
#         "Microchip", "SS&C Blue Prism", "Google for Developers", "AWS Academy",
#         "Mercedes-Benz India Private Limited", "Z Scaler", "Bharti Airtel Ltd.", 
#         "Government of India", "India Edu Programs"
#     ]
    
#     nlp = spacy.load("en_core_web_sm")
#     matcher = Matcher(nlp.vocab)
    
#     # Define patterns for Matcher based on company names
#     company_patterns = [{"label": company, "pattern": [{"LOWER": token.lower()} for token in company.split()]} for company in companies]

#     # Add patterns to Matcher
#     for pattern in company_patterns:
#         matcher.add(pattern["label"], [pattern["pattern"]])

#     # Find matches using the Matcher
#     doc = nlp(text)
#     matches = matcher(doc)

#     # Extract matched company names
#     company_names = []
#     for match_id, start, end in matches:
#         matched_company = doc[start:end].text
#         company_names.append(matched_company)

#     student_names = extract_name(text)
#     dates = date_pattern.findall(text)
#     date_range = date_range_pattern.findall(text)
#     durations = duration_pattern.findall(text)

#     # Find from date and to date using the keyword "to"
#     if date_range:
#         from_date = date_range[0][0]
#         to_date = date_range[0][1]
#     else:
#         from_date = "None"
#         to_date = "None"

#     # Create a DataFrame
#     data = {
#         "Name of the student": [student_names if student_names else "none"  ],
#         "Industry name": [company_names if company_names else "none" ],
#         "Date from": [from_date if from_date else "none" ],
#         "Date to": [to_date if to_date else "none" ],
#         "Single dates": [dates if dates else "none" ],
#         "Durations": [durations if durations else "none" ]  
#     }

#     # Handle empty data
#     for key in data:
#         if not data[key]:
#             data[key] = ["null"]

#     df = pd.DataFrame(data)
    
#     # Specify the CSV file name
#     csv_file = "entities.csv"
    
#     # Write the DataFrame to a CSV file
#     if os.path.exists(csv_file):
#         df.to_csv(csv_file, mode='a', header=False, index=False)  # Append without header
#     else:
#         df.to_csv(csv_file, index=False)  # Write with header if file doesn't exist
        
#     return csv_file

def main():
    upload_folder = r"C:\Users\SMITH\Documents\GitHub\N_E_R\uploads"
    
    
    # Get the single image file from the upload folder
    image_files = [f for f in os.listdir(upload_folder) if os.path.isfile(os.path.join(upload_folder, f))]
    
    
    if len(image_files) == 0:
        print("No image found in the directory.")
        return
    
    for img in image_files:
        # Assuming there is only one image in the directory
        image_path = os.path.join(upload_folder, img)

        #link for image
        image_url = f"http://localhost/uploads/{img}"
        
        # Process the image and extract text
        extracted_text = process_image(image_path)
        
        # Extract entities and save to CSV
        csv_file = extract_entities(extracted_text,image_url)
        print(f"Entities extracted and saved to {csv_file}")
    print (extracted_text)

if __name__ == '__main__':
    main()