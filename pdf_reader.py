from pdfminer.high_level import extract_text
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import io
import os
import csv

os.chdir(directory)

# Extract text from the PDF
def extract_All_text(directory):
    text=[]
    for file in os.listdir(directory):
        if file.endswith('.pdf'):
            file_path = os.path.join(directory, file)
            pdf_text = extract_text(file_path)
            text.append((file, pdf_text))
    return text

# get 200 chaarcheters around the word
def extract_context(sentence, word, context_length=200):
    # Find the starting index of the specified word
    start_index = sentence.find(word)
    
    if start_index == -1:
        return "Word not found in the sentence."

    # Calculate the start and end indices for context extraction
    word_start = start_index
    word_end = start_index + len(word)
    
    # Calculate the start and end indices of the substring
    context_start = max(0, word_start - context_length)
    context_end = min(len(sentence), word_end + context_length)
    
    # Extract the substring
    context = sentence[context_start:context_end]
    
    return context

def extract_images_and_text_from_pdf(directory):
    output_words=[]
    for file in os.listdir(directory):
        if file.endswith('.pdf'):
            file_path = os.path.join(directory, file)
            pdf_document = fitz.open(file_path)
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                image_list = page.get_images(full=True)
                
                for image_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = pdf_document.extract_image(xref)
                    image_bytes = base_image["image"]
                    
                    if not image_bytes:
                        print("No image data found.")
                        continue
                    
                    try:
                        # Open image using PIL
                        image = Image.open(io.BytesIO(image_bytes))
                        # Perform OCR on the extracted image
                        custom_config = r'--oem 3 --psm 6'
                        text = pytesseract.image_to_string(image, config=custom_config)
                        output_words.append((file,text))
                        # Print the extracted text
                        print(f'Page {page_num + 1}, Image {image_index + 1}:')
                        print('--- End of Image ---')
                    except Exception as e:
                        output_words.append((file,(f"Error opening image: {e}")))
                        continue
    return output_words
def find_paragraph(words:list, word_to_find):
    results=[]
    for i in range (len(words)):
        file,content=words[i]
        results.append((file,extract_context(content,word_to_find)))
    return results

# Example Usage
def UI(directory, word_to_find):
    output=[]
    words_in_pdf= extract_All_text(directory)
    words_in_pdf_img=extract_images_and_text_from_pdf(directory)
    words = find_paragraph(words_in_pdf,word_to_find)
    output.append((words))
    img_words=find_paragraph(words_in_pdf_img,word_to_find)
    output.append((img_words))
    return output
print(UI(directory,"random word"))

#if __name__ == "__main__":
