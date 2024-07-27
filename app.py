import cv2
import numpy as np
from PIL import Image
import pytesseract
import os
from flask import Flask, render_template, send_from_directory
from flask import Flask, render_template, send_from_directory
import re
import pandas as pd
import spacy  # Import spaCy library for natural language processing
from spacy.matcher import Matcher  # Import Matcher class from spaCy's matcher module

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] ='C:/Users/SMITH/Documents/N_E_R/uploads'

# Set up the Tesseract executable path (adjust the path if necessary)
pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/TesseractOCR/tesseract.exe"

def process_image(image_path):
    # Load the image
    image = cv2.imread(image_path)
    

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply sharpening filter
    kernel = np.array([[0, -1, 0], 
                       [-1, 5,-1], 
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
    text = pytesseract.image_to_string(image)
    
    return text

def extract_name(resume_text):
    """Function to extract name from resume text using spaCy's Matcher."""
    nlp = spacy.load('en_core_web_sm')  # Load English language model
    matcher = Matcher(nlp.vocab)  # Initialize Matcher with spaCy's vocabulary

    # Define name patterns for Matcher
    patterns = [
        [{'POS': 'PROPN'}, {'POS': 'PROPN'}],  # First name and Last name
        [{'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS': 'PROPN'}],  # First name, Middle name, and Last name
        [{'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS': 'PROPN'}]  # First name, Middle name, Middle name, and Last name
        # Add more patterns as needed
    ]

    for pattern in patterns:
        matcher.add('NAME', patterns=[pattern])  # Add each pattern to the Matcher

    doc = nlp(resume_text)  # Process the resume text with spaCy
    matches = matcher(doc)  # Apply the Matcher to find name patterns

    for match_id, start, end in matches:
        span = doc[start:end]  # Get the matched span of text
        return span.text  # Return the matched text (name)

    return None  # Return None if no name is found


def extract_entities(text,image_filename):
   
    # Define regex patterns
   
    company_name_pattern = re.compile(r'\b([A-Z][a-zA-Z]+(?: [A-Z][a-zA-Z]+){0,2})\b')
    duration_pattern = re.compile(r"from (\d{1,2} [A-Za-z]+ \d{4}) to (\d{1,2} [A-Za-z]+ \d{4})")
    date_pattern = re.compile(r'\b(\w+ \d{1,2}(?:st|nd|rd|th)?,? \d{4})\b')
    date_range_pattern = re.compile(r'\b(\w+ \d{4}) to (\w+ \d{4})\b')
    duration_pattern = re.compile(r'\b(\d+) (week|weeks?)\b', re.IGNORECASE)
   
        
    student_names=extract_name(text)

    company_names = [match for match in company_name_pattern.findall(text) if len(match.split()) <= 3]
    dates = date_pattern.findall(text)
    date_range = date_range_pattern.findall(text)
    durations = duration_pattern.findall(text)
   # Find from date and to date using the keyword "to"
    if date_range:
        from_date = date_range[0][0]
        to_date = date_range[0][1]
        
    else:
        from_date ="None"
        to_date = "None"
    # Create a DataFrame
    data = {
        "Name of the student": [student_names if student_names else "none"  ],
        "Industry name": [company_names if company_names else "none" ],
        "Date from": [from_date if from_date else "none" ],
        "Date to": [to_date if to_date else "none" ],
        "Single dates": [dates if dates else "none" ],
        "Durations": [durations if durations else "none" ]  
    }
    for key in data:
        if not data[key]:
            data[key] = ["null"]
        # (data, csv_file)
    df = pd.DataFrame(data)
    
    # Specify the CSV file name
    csv_file = "entities.csv"
    
     # Write the DataFrame to a CSV file
    if os.path.exists(csv_file):
        df.to_csv(csv_file, mode='a', header=False, index=False)  # Append without header
    else:
        df.to_csv(csv_file, index=False)  # Write with header if file doesn't exist
        
    return csv_file

@app.route('/')
def home():
    # Get the single image file from the upload folder
    image_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f))]
    
    if len(image_files) == 0:
        return "No image found in the directory."
    
    for img in image_files:
        # Assuming there is only one image in the directory
        image_file = img
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_file)
        image_filename= image_file.split(".")[0]
        # Process the image and extract text
        extracted_text = process_image(image_path)
    
        # Extract entities and save to CSV
        csv_file = extract_entities(extracted_text,image_filename)
    
    return render_template('index.html', image_file=image_file, extracted_text=extracted_text, csv_file=csv_file)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Run the application
if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])  # Create upload folder if it doesn't exist
    app.run(debug=True)
