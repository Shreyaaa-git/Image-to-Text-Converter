import os
import io
import cv2
import numpy as np
from google.cloud import vision_v1 as vision
from PIL import Image

# Function to perform image analysis using Google Vision API
def image_analysis(image_path):
    try:
        client = vision.ImageAnnotatorClient()

        with io.open(image_path, 'rb') as img_file:
            content = img_file.read()

        img = vision.Image(content=content)
        response = client.text_detection(image=img)

        if response.error.message:
            raise Exception(f"API Error: {response.error.message}")

        return response

    except Exception as e:
        print(f"Error in image_analysis: {e}")
        return None

# Function to retrieve text from the API response
def get_text(response):
    try:
        text_annotations = response.text_annotations
        if text_annotations:
            return text_annotations[0].description
        return ""

    except Exception as e:
        print(f"Error in get_text: {e}")
        return ""

# Function to detect and crop visual elements using OpenCV
def detect_visual_elements(image_path):
    try:
        img = cv2.imread(image_path)
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, binary_img = cv2.threshold(gray_img, 150, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        elements = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            elements.append(img[y:y+h, x:x+w])

        return elements

    except Exception as e:
        print(f"Error in detect_visual_elements: {e}")
        return []

# Function to generate HTML content from text and visual elements
def generate_html_content(text, visual_elements):
    try:
        html_content = "<html><head><style>img {max-width: 100%; height: auto;} body {font-family: Verdana, sans-serif;}</style></head><body>"

        for paragraph in text.split('\n'):
            if paragraph.strip():
                html_content += f"<p>{paragraph}</p>"

        for idx, element in enumerate(visual_elements):
            img_filename = f"element_{idx}.png"
            cv2.imwrite(img_filename, element)
            html_content += f'<img src="{img_filename}" alt="Element {idx}"><br>'

        html_content += "</body></html>"
        return html_content

    except Exception as e:
        print(f"Error in generate_html_content: {e}")
        return ""

# Function to write HTML content to a file
def write_html_file(html_content, output_filename='output.html'):
    try:
        with open(output_filename, 'w') as file:
            file.write(html_content)
        print(f"HTML content successfully written to {output_filename}")

    except Exception as e:
        print(f"Error in write_html_file: {e}")

# Main function to handle the process flow
def process_image(image_path):
    try:
        # Step 1: Perform image analysis
        response = image_analysis(image_path)
        if response is None:
            print("Image analysis failed.")
            return

        # Step 2: Extract text from response
        extracted_text = get_text(response)
        if not extracted_text:
            print("No text detected in the image.")
            return

        # Step 3: Detect visual elements in the image
        visual_elements = detect_visual_elements(image_path)
        if not visual_elements:
            print("No visual elements detected.")
            return

        # Step 4: Generate HTML content
        html_content = generate_html_content(extracted_text, visual_elements)
        if not html_content:
            print("Failed to generate HTML content.")
            return

        # Step 5: Write HTML content to a file
        write_html_file(html_content)

    except Exception as e:
        print(f"Error in process_image: {e}")

# Entry point of the script
if __name__ == "__main__":
    image_path = 'img2.jpg'
    if not os.path.exists(image_path):
        print(f"The image file {image_path} does not exist.")
    else:
        process_image(image_path)
