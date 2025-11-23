#!/usr/bin/env python3
"""Extract text from all PDF lecture files"""
import PyPDF2
import os

def extract_pdf(pdf_path, output_path):
    """Extract text from PDF and save to text file"""
    try:
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text_content = []
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text_content.append(f"\n{'='*70}\nPAGE {page_num + 1}\n{'='*70}\n")
                text_content.append(page.extract_text())
            
            full_text = ''.join(text_content)
            
            with open(output_path, 'w', encoding='utf-8') as out_file:
                out_file.write(full_text)
            
            return True, len(pdf_reader.pages)
    except Exception as e:
        return False, str(e)

# Paths
base_dir = r"G:\School\ISIT312\Exam_prep"
lectures_dir = os.path.join(base_dir, "Lectures")
output_dir = os.path.join(base_dir, "extracted_texts")

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# List of all lecture files
files_to_process = [
    ("Lectures", "L0 Subject Overview.pdf"),
    ("Lectures", "01clustercomputing.pdf"),
    ("Lectures", "02mapreduceframework.pdf"),
    ("Lectures", "03hadooparchitecture.pdf"),
    ("Lectures", "04hdfsinterfaces.pdf"),
    ("Lectures", "05mapreducemodel.pdf"),
    ("Lectures", "06javamapreduceapplication.pdf"),
    ("Lectures", "07hive.pdf"),
    ("Lectures", "08hivedatastructures.pdf"),
    ("Lectures", "09dwconcepts.pdf"),
    ("Lectures", "10conceptdwdesign.pdf"),
    ("Lectures", "11logicaldwdesign.pdf"),
    ("Lectures", "12sqlfordw.pdf"),
    ("Lectures", "13hiveprogramming.pdf"),
    ("Lectures", "14physicaldwdesign.pdf"),
    ("Lectures", "15hbasedatamodel.pdf"),
    ("Lectures", "16hbaseoperations.pdf"),
    ("Lectures", "17sparkintroduction.pdf"),
    ("Lectures", "18sparkdatamodel.pdf"),
    ("Lectures", "19sparkoperations.pdf"),
    ("Lectures", "20sparkstream.pdf"),
    ("Lectures", "21 Subject Review.pdf"),
    ("Sample Exam", "exams-s2-2017-isit312(4).pdf"),
]

print("Starting PDF extraction...")
print("="*70)

success_count = 0
fail_count = 0

for folder, filename in files_to_process:
    pdf_path = os.path.join(base_dir, folder, filename)
    output_filename = filename.replace(".pdf", ".txt")
    output_path = os.path.join(output_dir, output_filename)
    
    print(f"\nProcessing: {filename}")
    success, result = extract_pdf(pdf_path, output_path)
    
    if success:
        print(f"  ✓ Extracted {result} pages -> {output_filename}")
        success_count += 1
    else:
        print(f"  ✗ Failed: {result}")
        fail_count += 1

print("\n" + "="*70)
print(f"Extraction complete: {success_count} successful, {fail_count} failed")
print(f"Output directory: {output_dir}")
