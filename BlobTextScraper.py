from io import BytesIO
import docx
import pandas as pd
import ezodf
from odf import text, teletype
from odf.opendocument import load
import PyPDF2
import tempfile
import textract
import os
import json
from bs4 import BeautifulSoup
from PIL import Image
import easyocr


class BlobTextExtractor():
    # Class constructor
    # Not currently used
    def __init__(self):
        pass

    # Processes a DataFrame containing attachment data and returns a df with extracted text
    # Results include scraped column = 1 if text extraction is successful, 0 otherwise.
    # Unsuccessful extractions return None for the scrapedText column
    def process_records(self, records):
        results = []
        for index, record in records.iterrows():
            try:
                msgID = record['msgID']
                attachmentName = record['attachmentName']
                attachmentType = record['attachmentType']
                attachmentSize = record['attachmentSize']
                attachmentBlob = record['attachmentBlob']
            except Exception as e:
                print(f"An error occurred when trying to load data from records: {e}")
                print("Skipping problematic record, trying next record...")
                continue
            if attachmentName.endswith('.odt'):
                extracted_text, scraped = self.odt_extract(attachmentBlob)
            elif attachmentName.endswith('.ods'):
                extracted_text, scraped = self.ods_extract(attachmentBlob)
            elif attachmentName.endswith('.html') or attachmentType == 'text/html':
                extracted_text, scraped = self.html_extract(attachmentBlob)
            elif attachmentName.endswith('.png'):
                extracted_text, scraped = self.png_extract(attachmentBlob)
            elif attachmentName.endswith('.jpg'):
                extracted_text, scraped = self.jpg_extract(attachmentBlob)
            elif attachmentName.endswith('.xls'):
                extracted_text, scraped = self.xls_extract(attachmentBlob)
            elif attachmentName.endswith('.xlsx'):
                extracted_text, scraped = self.xlsx_extract(attachmentBlob)
            elif attachmentName.endswith('.pdf'):
                extracted_text, scraped = self.pdf_extract(attachmentBlob)
            elif attachmentName.endswith('.docx'):
                extracted_text, scraped = self.docx_extract(attachmentBlob)
            elif attachmentName.endswith('.doc'):
                extracted_text, scraped = self.doc_extract(attachmentBlob)
            else:
                print(f"Unable to identify file type for attachment: {attachmentName}")
                print("Returning None for extracted_text.")
                extracted_text, scraped = None, 0
            result_entry = {
                'msgID': msgID,
                'attachmentName': attachmentName,
                'attachmentType': attachmentType,
                'attachmentSize': attachmentSize,
                'scraped': scraped,
                'scrapedText': extracted_text
            }
            results.append(result_entry)
        
        results_df = pd.DataFrame(results)
        return results_df

    # Checks if a given blob is correctly formatted
    # Returns correctly formatted blob
    def blob_validate(self, blob):
        # Check if blob has 0x prefix, remove if so
        if blob[:2] == '0x':
            blob = blob[2:]
        return blob
    
    # Util function that takes a file path and converts the file into a hexadecimal blob
    # Used for testing purposes
    def to_hex_blob(self, file_path):
        try:
            with open(file_path, 'rb') as file:
                try:
                    # Read the binary content of the file
                    binary_content = file.read()
                    # Convert binary content to hexadecimal string
                    hex_blob = binary_content.hex()
                    return hex_blob
                except Exception as e:
                    print(f"An error occurred when attempting to convert file {file_path} to a hex blob: {e}")
                    return None
        except Exception as e:
            print(f"An error occurred when attempting to open file {file_path}: {e}")
            return None

    # Extracts text from a .odt (Open Document Text) file hexadecimal blob.
    # Returns extracted raw text and scraped indicator
    # Scraped = 1 if successful, 0 otherwise. raw text = None if unsuccessful
    def odt_extract(self, blob):
        blob = self.blob_validate(blob)
        try:
            # Convert hexadecimal blob to bytes
            blob_bytes = bytes.fromhex(blob)
            # Create a BytesIO object from the bytes
            bytes_mem_obj = BytesIO(blob_bytes)
            # Load the ODT document using odfpy
            odt_doc = load(bytes_mem_obj)
        except Exception as e:
            print(f"An error occurred when trying to read the blob and load as ODT doc: {e}")
            return None, 0
        try:
            # Extract text content from the document
            text_content = ""
            for para in odt_doc.getElementsByType(text.P):
                text_content += teletype.extractText(para)
            return text_content, 1
        except Exception as e:
            print(f"An error occurred when trying to extract ODT doc text: {e}")
            return None, 0

    # Extracts contents from a .ods (Open Document Spreadsheet) file hexadecimal blob
    # Returns extracted contents as a JSON object. JSON object contains an array with an entry for each sheet in the doc
    # Scraped = 1 if successful, 0 otherwise. raw text = None if unsuccessful
    def ods_extract(self, blob):
        blob = self.blob_validate(blob)
        try:
            # Convert hexadecimal blob to bytes
            blob_bytes = bytes.fromhex(blob)
            # Create a BytesIO object from the bytes
            bytes_mem_obj = BytesIO(blob_bytes)
            # Open the ODS document using ezodf
            ods_doc = ezodf.opendoc(bytes_mem_obj)
        except Exception as e:
            print(f"An error occurred when trying to read the blob and load as ODS doc: {e}")
            return None, 0
        try:
            # Create a dictionary to store sheet data
            sheets_data = {}
            # Iterate over all sheets
            for sheet_index, sheet in enumerate(ods_doc.sheets):
                # Read data from the sheet into a DataFrame
                data = []
                for row in sheet.rows():
                    # List comp extracts the content from each cell in the row and stores in row_data
                    row_data = [cell.value for cell in row]
                    data.append(row_data)
                # Create a DataFrame from the data
                df = pd.DataFrame(data)
                # Convert DataFrame to JSON and add it to the dictionary
                sheets_data[f'Sheet_{sheet_index + 1}'] = json.loads(df.to_json(orient='split'))
            # Convert the dictionary to a JSON string, preserving the doc's structure
            json_string = json.dumps(sheets_data)
            return json_string, 1
        except Exception as e:
            print(f"An error occurred when trying to extract the ODS doc data: {e}")
            return None, 0

    # Extracts contents from an HTML attachment blob
    # Returns a beautiful soup html object as a string, preserving the html's structure
    # Scraped = 1 if successful, 0 otherwise. raw text = None if unsuccessful
    def html_extract(self, blob):
        blob = self.blob_validate(blob)
        try:
            # Convert hexadecimal blob to bytes
            blob_bytes = bytes.fromhex(blob)
            # Create a BytesIO object from the bytes
            bytes_mem_obj = BytesIO(blob_bytes)
            # Parse the HTML using BeautifulSoup
            soup = BeautifulSoup(bytes_mem_obj, 'html.parser')
            return str(soup), 1
        except Exception as e:
            print(f"An error occurred when attempting to read the HTML data: {e}")
            return None, 0

    # Util function that performs an OCR (Optical Character Recognition) extraction of a image's text
    # Returns any text that was extracted from am image
    def ocr_scrape(self, img_bytes):
        try:
            # Create an OCR reader
            reader = easyocr.Reader(['en'])
            # Open an image file
            result = reader.readtext(img_bytes)
            # Extract text from the result
            text = []
            for entry in result:
                text.append(entry[1])
            textString = ''.join(text)
            return textString, 1
        except Exception as e:
            print(f"Error occurred when attempting to extract text from image: {e}")
            return None, 0
    
    # Takes a hexadecimal blob of a png image and converts it to bytes
    # Calls the OCR_scrape function which performs an OCR text extraction on the image
    # Returns any text that was successfully extracted
    # Has commented optional code that would allow you to save the image and manually review
    def png_extract(self, blob):
        blob = self.blob_validate(blob)
        try:
            # Convert hexadecimal blob to bytes
            img_bytes = bytes.fromhex(blob)
            # OPTIONAL CODE: Save the image to a file for manual review
            # ---------------------
                # Create a BytesIO object from the bytes
                #img_mem_obj = BytesIO(img_bytes)
                # Open the image using Pillow
                #img = Image.open(img_mem_obj)
                #img.save(output_file_path)
        except Exception as e:
            print(f"An error occurred when attempting to read png blob as bytes: {e}")
            return None, 0
        scraped_text, scraped = self.ocr_scrape(img_bytes)
        return scraped_text, scraped

    # Takes a hexadecimal blob of a jpg image and converts it to bytes
    # Calls the OCR_scrape function which performs an OCR text extraction on the image
    # Returns any text that was successfully extracted
    # Has commented optional code that would allow you to save the image and manually review
    def jpg_extract(self, blob):
        blob = self.blob_validate(blob)
        try:
            # Convert hexadecimal blob to bytes
            img_bytes = bytes.fromhex(blob)
            # OPTIONAL CODE: Save the image to a file for manual review
            # ---------------------
                # Create a BytesIO object from the bytes
                #img_mem_obj = BytesIO(img_bytes)
                # Open the image using Pillow
                #img = Image.open(img_mem_obj)
                #img.save(output_file_path)
        except Exception as e:
            print(f"An error occurred when attempting to read jpg blob as bytes: {e}")
            return None, 0
        scraped_text, scraped = self.ocr_scrape(img_bytes)
        return scraped_text, scraped

    # Extracts contents from a .xls (Excel 97-2003) file hexadecimal blob
    # Returns extracted contents as a JSON object, preserving spreadsheet structure.
    def xls_extract(self, blob):
        blob = self.blob_validate(blob)
        try:
            # Convert hexadecimal blob into bytes
            blob_bytes = bytes.fromhex(blob)
            # Create a BytesIO object from the bytes
            bytes_mem_obj = BytesIO(blob_bytes)
            # Define engine pandas will use to read xls doc
            engine = "xlrd"
            # Use pandas to read the xls doc with xlrd
            doc_xls = pd.ExcelFile(bytes_mem_obj, engine=engine)
        except Exception as e:
            print(f"An error occurred when attempting to read the blob and load as an xls doc: {e} ")
            return None, 0
        try:
            # Create empty df for sheet data
            sheets_df = pd.DataFrame()
            # Extract the contents of the xls doc, append to the sheets_df
            for sheet in doc_xls.sheet_names:
                df_sheet = doc_xls.parse(sheet, header=None)
                df_sheet["sheet"] = sheet
                sheets_df = sheets_df.append(df_sheet, ignore_index=True)
            # Convert the sheets df to JSON to preserve the xls doc's structure
            json_string = sheets_df.reset_index(drop=True).to_json().replace("}", "}\n")
            return json_string, 1
        except Exception as e:
            print(f"An error occurred when attempting to extract data from xls doc: {e}")
            return None, 0
    
    # Extracts contents from a .xlsx (Excel Workbook) file hexadecimal blob
    # Returns extracted contents as a JSON object, preserving spreadsheet structure.
    def xlsx_extract(self, blob):
        blob = self.blob_validate(blob)
        try:
            # Convert hexadecimal blob into bytes
            blob_bytes = bytes.fromhex(blob)
            # Create a BytesIO object from the bytes
            bytes_mem_obj = BytesIO(blob_bytes)
            # Define engine pandas will use to read xlsx doc
            engine = "openpyxl"
            # Use pandas to read the xls doc with openpyxl
            doc_xlsx = pd.ExcelFile(bytes_mem_obj, engine=engine)
        except Exception as e:
            print(f"An error occurred when attempting to read blob and load as an xlsx doc: {e}")
            return None, 0
        try:
            # Create empty df for sheet data
            sheets_df = pd.DataFrame()
            # Extract the contents of the xlsx doc, append to the sheets_df
            for sheet in doc_xlsx.sheet_names:
                df_sheet = doc_xlsx.parse(sheet, header=None)
                df_sheet["sheet"] = sheet
                sheets_df = sheets_df.append(df_sheet)
            # Convert the sheets df to JSON to preserve the xlsx doc's structure
            json_string = sheets_df.reset_index(drop=True).to_json().replace("}", "}\n")
            return json_string, 1
        except Exception as e:
            print(f"An error occurred when attempting to extract data from xlsx doc: {e}")
            return None, 0

    # Extracts text from a PDF hexadecimal blob
    # Returns extracted raw text
    def pdf_extract(self, blob):
        blob = self.blob_validate(blob)
        try:
            # Convert hexadecimal blob into bytes
            blob = bytes.fromhex(blob)
            # Create a BytesIO object from the bytes
            bytes_mem_obj = BytesIO(blob)
            # Open the bytes object as a PDF file using PyPDF2
            pdf_reader = PyPDF2.PdfFileReader(bytes_mem_obj)
        except Exception as e:
            print(f"An error occurred when attempting to read blob and load as PDF doc: {e}")
            return None, 0
        try:
            # Retrieve number of pdf pages
            num_pages = pdf_reader.numPages
            # Init empty text string
            text = ''
            # Extract all the text in the doc from all pages
            for page_num in range(num_pages):
                page = pdf_reader.getPage(page_num)
                text += page.extractText()
            return text, 1
        except Exception as e:
            print(f"An error occurred when attempting to extract the text from the PDF doc: {e}")
            return None, 0

    # Extracts text from a .docx hexadecimal blob
    # Returns raw text from the .docx file
    def docx_extract(self, blob):
        blob = self.blob_validate(blob)
        try:
            # Convert hexadecimal blob into bytes
            blob = bytes.fromhex(blob)
            # Create a BytesIO object from the bytes
            bytes_mem_obj = BytesIO(blob)
            # Use docx to load the blob bytes as a file
            docx_doc = docx.Document(bytes_mem_obj)
        except Exception as e:
            print(f"An error occurred when attempting to read the blob and load as a docx file: {e}")
            return None, 0
        try:
            # Init empty text list
            fullText = []
            # Extract the text paragraph by paragraph, append to text list
            for para in docx_doc.paragraphs:
                fullText.append(para.text)
            return "\n".join(fullText), 1
        except Exception as e:
            print(f"An error occurred when attempting to extract text from the docx doc: {e}")
            return None, 0

    # Extracts text from a .doc (Word 97-2003) file hexadecimal blob - Works for both application/msword and application/octet-stream .doc files
    # Returns raw text from the .doc file
    def doc_extract(self, blob):
        blob = self.blob_validate(blob)
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Update the directory path for new tempfile
            temp_path = os.path.join(temp_dir, 'temp.doc')
            # Create a temporary .doc file within the temp directory
            with tempfile.NamedTemporaryFile(delete=False, suffix='.doc') as temp_file:
                try:
                    # Turn the raw hex blob into bytes
                    blob = bytes.fromhex(blob)
                    # Write the bytes to the temp file
                    temp_file.write(blob)
                    # Update the temp path to include the new temp file's name
                    temp_path = temp_file.name
                except Exception as e:
                    print(f"An error occurred when attempting to write bytes from .doc blob to the temp file: {e}")
                    return None, 0
            try:
                # Use textract to extract text from the Word document - requires antiword dependency!
                text = textract.process(temp_path, method='antiword', path=r'C:\antiword\antiword.exe')
                return text.decode("utf-8"), 1
            except Exception as e:
                print(f"Error extracting text: {e}")
                return None, 0

