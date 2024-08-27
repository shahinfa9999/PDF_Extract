from pdfminer.high_level import extract_text
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import io
import os
import csv

class BoyerMoore:
    def __init__(self, pattern):
        self.pattern = pattern
        self.pattern_length = len(pattern)
        self.bad_char_shift = self.preprocess_bad_char_shift()

    def preprocess_bad_char_shift(self):
        shift = {}
        for i in range(self.pattern_length - 1):
            shift[self.pattern[i]] = self.pattern_length - 1 - i
        return shift

    def search(self, text):
        text_length = len(text)
        skip = 0

        while text_length - skip >= self.pattern_length:
            i = self.pattern_length - 1
            while i >= 0 and self.pattern[i] == text[skip + i]:
                i -= 1
            if i < 0:
                return skip  # Return the position of the found word
            else:
                skip += self.bad_char_shift.get(text[skip + self.pattern_length - 1], self.pattern_length)
        return -1  # If the word is not found


# Extract text from the PDF
def extract_All_text(directory):
    text=[]
    for file in os.listdir(directory):
        if file.endswith('.pdf'):
            file_path = os.path.join(directory, file)
            pdf_text = extract_text(file_path)
            text.append((file, pdf_text))
    return text

# get 100 chaarcheters around the word
def extract_context(sentence, word, context_length=100):
    bm = BoyerMoore(word)
    start_index = bm.search(sentence)

    if start_index == -1:
        return "Word not found in the document."

    word_start = start_index
    word_end = start_index + len(word)
    
    context_start = max(0, word_start - context_length)
    context_end = min(len(sentence), word_end + context_length)
    
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
                        #output_words.append((file,(f"Error opening image: {e}")))
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

def csvwriter (directory,filename, output):
    file_path = os.path.join(directory, filename)
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Source", "Sentence found"])
        for item in output:
            for word in item:
                source,found = word
                writer.writerow([source, found])


            
directory = r'enter your directory here'
os.chdir(directory)
output=UI(directory,"enter word/phrase to look up")
csvwriter(directory,"output.csv",output)
