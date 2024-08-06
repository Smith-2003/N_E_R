# st.set_page_config(
#     page_title="Multipage App",
#     page_icon="👏",
# )

# st.title("Main Page")
# st.sidebar.success("Select a page above.")
# if "my_input" not in st.session_state:
#     st.session_state["my_input"]=""
# my_input= st.text_input("Input a text here",st.session_state["my_input"])
# submit = st.button("Submit")
# if submit:
#     st.session_state["my_input"]=my_input
#     st.write("you have entered: ",my_input)


import streamlit as st
import os
import fitz  # PyMuPDF

# Define the directory to save uploaded files and text files
upload_directory = "uploaded_pdfs"
text_directory = "extracted_texts"
os.makedirs(upload_directory, exist_ok=True)  # Create the upload directory if it doesn't exist
os.makedirs(text_directory, exist_ok=True)  # Create the text directory if it doesn't exist

# Streamlit file uploader
uploaded_files = st.file_uploader("Choose PDF files", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        # Save the uploaded file to the specified directory
        file_path = os.path.join(upload_directory, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Saved {uploaded_file.name} to {upload_directory}")

        # Extract text from the PDF
        text = ""
        try:
            # Open the PDF file using PyMuPDF
            pdf_document = fitz.open(file_path)
            for page in pdf_document:
                text += page.get_text()  # Extract text from each page
            pdf_document.close()

            # Save extracted text to a .txt file
            text_file_name = os.path.splitext(uploaded_file.name)[0] + ".txt"
            text_file_path = os.path.join(text_directory, text_file_name)
            with open(text_file_path, "w", encoding="utf-8") as text_file:
                text_file.write(text)
            st.success(f"Extracted text saved to {text_file_name} in {text_directory}")

            # Display extracted text in a text area
            st.subheader(f"Extracted Text from {uploaded_file.name}:")
            st.text_area("Text Output", text, height=300)

            # Add download button for the extracted text file
            st.download_button(
                label=f"Download {text_file_name}",
                data=text,
                file_name=text_file_name,
                mime="text/plain",
            )
            
        except Exception as e:
            st.error(f"Error extracting text from {uploaded_file.name}: {e}")