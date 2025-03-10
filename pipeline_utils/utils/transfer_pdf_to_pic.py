### using PuMuPDF to transfer the pdf data to jpeg

import fitz  # PyMuPDF
import os
import io
from PIL import Image
from machine_label.utils import DEFAULT_CFG, get_cfg
from machine_label.utils.s3_load import (upload_img_to_s3,
                                         upload_pdf_to_s3,
                                         check_link,
                                         pdf_from_s3)


# class for transfer the pdf file
class TransferPDF:
    def __init__(self, confg=DEFAULT_CFG, overrides=None):
        self.args = get_cfg(confg, overrides)
        self._pdf_path = self.args.pdf_path
        self.bucket_name = self.args.bucket_name

    @property
    def pdf_path(self):
        return self._pdf_path

    def piece_pdf_to_pages(self):
        pdf_stream = pdf_from_s3(self.pdf_path)
        # Open the PDF with fitz
        pdf = fitz.open(stream=pdf_stream, filetype="pdf")
        bucket, pdf_s3 = check_link(self.pdf_path)

        pdf_folder_s3 = os.path.dirname(pdf_s3)
        # filename_only, _ = os.path.splitext(pdf_folder_s3)
        output_directory = f"{pdf_folder_s3}"
        # Split the PDF into individual pages
        for page_num in range(len(pdf)):
            # page = pdf.load_page(page_num)  # Load the current page
            output_pdf = fitz.open()  # Create a new PDF in memory
            output_pdf.insert_pdf(pdf, from_page=page_num, to_page=page_num)  # Insert the current page into the new PDF

            output_filename = f"sheet_{page_num}.pdf"
            # output_pdf.save(output_filename)  
            upload_pdf_to_s3(output_directory, output_pdf, output_filename, bucket=bucket)

            output_pdf.close()

        return output_directory, len(pdf)

    def transfer_pdf_to_png(self, from_s3=True):
        if from_s3:
            # process single pdf
            pdf_stream = pdf_from_s3(self.pdf_path)
            # Open the PDF with fitz
            doc = fitz.open(stream=pdf_stream, filetype="pdf")
        else:
            doc = fitz.open(self.pdf_path)
        _, pdf_s3 = check_link(self.pdf_path)
        pdf_folder_s3 = os.path.dirname(pdf_s3)
        output_directory = f"{pdf_folder_s3}"

        # Loop through each page
        for page_num in range(len(doc)):
            # Get the page
            page = doc[page_num]
            # for general prediction and label studio use default dpi=72
            pix = page.get_pixmap()
            # Convert the pixmap to a PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            upload_img_to_s3(output_directory, img, f"sheet_{page_num}.png", bucket=self.bucket_name)
        doc.close()

    @staticmethod
    def pdf_to_highresolution(pdf_path, box, page_number=0, from_s3=True):
        # Specify the DPI for high resolution
        if from_s3:
            pdf_stream = pdf_from_s3(pdf_path)
            # Open the PDF with fitz
            doc = fitz.open(stream=pdf_stream, filetype="pdf")
        else:
            doc = fitz.open(pdf_path)
        page = doc.load_page(page_number)
        dpi = 300
        zoom = dpi / 72  # default DPI in PDF is 72
        mat = fitz.Matrix(zoom, zoom)
        # Crop and save the image
        cropped_img = page.get_pixmap(matrix=mat, clip=box)
        img_bytes = cropped_img.tobytes("png")  # Convert pixmap to PNG bytes
        img = Image.open(io.BytesIO(img_bytes))  # Open the PNG bytes with PIL
        doc.close()
        return img


# Get the path from the user
if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Process a PDF file.")
    # parser.add_argument("pdf_num", type=int, help="The PDF number to process")
    parser.add_argument("overrides", type=str, help="JSON string for overrides dictionary")

    args = parser.parse_args()

    # Convert the JSON string back to a dictionary
    overrides = json.loads(args.overrides)
    process_pdf = TransferPDF(overrides)
    process_pdf.piece_pdf_to_pages()
    process_pdf.transfer_pdf_to_png()
