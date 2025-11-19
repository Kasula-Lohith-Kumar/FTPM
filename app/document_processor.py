import os
import re
import cv2
import fitz
import base64
import config
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import langchain_api_prompts as lap


def get_image_folder_path():
    cwd = os.getcwd()
    return os.path.join(cwd, config.IMAGE_FOLDER_PATH)


# Open the image file and encode it as a base64 string
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def extract_images_and_text_from_pdf(pdf_path):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    image_folder_path = get_image_folder_path()

    # Create the output folder if it doesn't exist
    if not os.path.exists(image_folder_path):
        os.makedirs(image_folder_path)

    # Initialize a variable to store the combined text
    combined_text = ""

    # Loop through each page
    for page_number in range(len(pdf_document)):
        page = pdf_document.load_page(page_number)
        text = page.get_text()

        # Add the text of the current page to combined_text
        combined_text += f"\n\nPage {page_number + 1}:\n{text}"

        # Get the images from the page
        image_list = page.get_images(full=True)

        # Extract and process each image
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_filename = f"page_{page_number+1}_img_{img_index+1}.{image_ext}"
            image_filepath = os.path.join(image_folder_path, image_filename)

            # Save the image to the output folder
            with open(image_filepath, "wb") as image_file:
                image_file.write(image_bytes)

            # Encode the image to base64
            base64_image = encode_image(image_filepath)

            # Use GPT-4o to describe the image and extract text
            image_description = lap.describe_image(base64_image)

            # Add the image description and reference to combined_text
            combined_text += f"\n\n[Image: {image_filename}]\n{image_description}"

            print(f"Processed {image_filename} on page {page_number + 1}")

    st.info("Combined images and text Processing complete.")

    # Return the combined text
    return combined_text

# Function to extract image references from the text
def extract_image_references(text):
    pattern = r"\[Image:\s*(.*?)\]"
    image_references = re.findall(pattern, text)
    return image_references


# Function to display an image using Matplotlib
def display_image(image_path):
    # Check if the image file exists
    if os.path.exists(image_path):
        # Load and display the image
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        plt.imshow(image_rgb)
        plt.axis('off')  # Hide axis
        plt.show()
    else:
        st.error(f"Image file {image_path} not found.")

def display_content(result):

    image_folder_path = get_image_folder_path()
    image_references = extract_image_references(
        result["source_documents"][0].page_content)
    
    for image_file in image_references:
        image_path = os.path.join(image_folder_path, image_file)
        print(f"Displaying {image_file}...")
        display_image(image_path)

def list_dir_content(path):
    # st.title("List Directory Contents (os.listdir)")
    file_list = None
    if st.button("List Files"):
        # 1. Get the list of files/directories in the current working directory
        try:
            file_list = os.listdir(path) # '.' represents the current directory
            
            # 2. Display the result, optionally as a table
            st.success("Found the following items:")
            
            # Create a simple DataFrame for a nice Streamlit table display
            df = pd.DataFrame(file_list, columns=['Item Name'])
            st.dataframe(df)
            
        except Exception as e:
            st.error(f"An error occurred: {e}")

    return file_list