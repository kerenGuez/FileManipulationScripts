import os
import sys
from PyPDF2 import PdfMerger


def merge_pdfs_in_folder(folder_path, output_filename="merged_output.pdf"):
    # Create a PdfMerger object
    merger = PdfMerger()

    # List all PDF files in the specified folder
    pdf_files = [file for file in os.listdir(folder_path) if file.endswith('.pdf')]

    # Sort the PDF files to ensure proper order
    pdf_files.sort()

    # Loop through and append each PDF to the merger
    for pdf_file in pdf_files:
        file_path = os.path.join(folder_path, pdf_file)
        print(f"Adding {pdf_file}")
        merger.append(file_path)

    # Write the merged PDF to the output file
    output_path = os.path.join(folder_path, output_filename)
    merger.write(output_path)
    merger.close()
    print(f"Merged PDF saved as {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python merge_files.py <folder_path>")
        sys.exit(1)

    the_folder_path = sys.argv[1]
    merge_pdfs_in_folder(the_folder_path)