#!/usr/bin/env python3
"""
Consolidated PDF Content Extractor
This creates ONE file with all lecture content for easy reading
"""
import PyPDF2
import os
import json

def extract_pdf_content(pdf_path):
    """Extract all text from a PDF file"""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            content = {
                'num_pages': len(reader.pages),
                'pages': []
            }
            
            for i, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                content['pages'].append({
                    'page_num': i,
                    'text': text
                })
            
            return content
    except Exception as e:
        return {'error': str(e), 'num_pages': 0, 'pages': []}

# Configuration
BASE_DIR = r"G:\School\ISIT312\Exam_prep"
OUTPUT_FILE = os.path.join(BASE_DIR, "extracted_texts", "ALL_CONTENT.txt")

# List of all files to process in order
FILES_TO_PROCESS = [
    ("Lectures", "L0 Subject Overview.pdf", "00_OVERVIEW"),
    ("Lectures", "01clustercomputing.pdf", "01_CLUSTER_COMPUTING"),
    ("Lectures", "02mapreduceframework.pdf", "02_MAPREDUCE_FRAMEWORK"),
    ("Lectures", "03hadooparchitecture.pdf", "03_HADOOP_ARCHITECTURE"),
    ("Lectures", "04hdfsinterfaces.pdf", "04_HDFS_INTERFACES"),
    ("Lectures", "05mapreducemodel.pdf", "05_MAPREDUCE_MODEL"),
    ("Lectures", "06javamapreduceapplication.pdf", "06_JAVA_MAPREDUCE"),
    ("Lectures", "07hive.pdf", "07_HIVE_INTRO"),
    ("Lectures", "08hivedatastructures.pdf", "08_HIVE_DATA_STRUCTURES"),
    ("Lectures", "09dwconcepts.pdf", "09_DW_CONCEPTS"),
    ("Lectures", "10conceptdwdesign.pdf", "10_DW_DESIGN_CONCEPTS"),
    ("Lectures", "11logicaldwdesign.pdf", "11_LOGICAL_DW_DESIGN"),
    ("Lectures", "12sqlfordw.pdf", "12_SQL_FOR_DW"),
    ("Lectures", "13hiveprogramming.pdf", "13_HIVE_PROGRAMMING"),
    ("Lectures", "14physicaldwdesign.pdf", "14_PHYSICAL_DW_DESIGN"),
    ("Lectures", "15hbasedatamodel.pdf", "15_HBASE_DATA_MODEL"),
    ("Lectures", "16hbaseoperations.pdf", "16_HBASE_OPERATIONS"),
    ("Lectures", "17sparkintroduction.pdf", "17_SPARK_INTRO"),
    ("Lectures", "18sparkdatamodel.pdf", "18_SPARK_DATA_MODEL"),
    ("Lectures", "19sparkoperations.pdf", "19_SPARK_OPERATIONS"),
    ("Lectures", "20sparkstream.pdf", "20_SPARK_STREAMING"),
    ("Lectures", "21 Subject Review.pdf", "21_SUBJECT_REVIEW"),
    ("Sample Exam", "exams-s2-2017-isit312(4).pdf", "SAMPLE_EXAM"),
]

# Create output directory
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

print("="*80)
print("CONSOLIDATED PDF EXTRACTOR - ISIT312 Exam Prep")
print("="*80)
print(f"\nExtracting {len(FILES_TO_PROCESS)} files...")
print(f"Output: {OUTPUT_FILE}\n")

# Open output file
with open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
    outfile.write("="*80 + "\n")
    outfile.write("ISIT312 - COMPLETE LECTURE CONTENT\n")
    outfile.write("="*80 + "\n")
    outfile.write(f"Total Files: {len(FILES_TO_PROCESS)}\n")
    outfile.write("="*80 + "\n\n")
    
    # Process each file
    for folder, filename, label in FILES_TO_PROCESS:
        pdf_path = os.path.join(BASE_DIR, folder, filename)
        
        print(f"Processing: {filename}...")
        
        # Write section header
        outfile.write("\n\n")
        outfile.write("#" * 80 + "\n")
        outfile.write(f"### {label}\n")
        outfile.write(f"### File: {filename}\n")
        outfile.write("#" * 80 + "\n\n")
        
        # Extract content
        content = extract_pdf_content(pdf_path)
        
        if 'error' in content:
            outfile.write(f"ERROR extracting {filename}: {content['error']}\n")
            print(f"  ✗ Error: {content['error']}")
        else:
            outfile.write(f"Total Pages: {content['num_pages']}\n")
            outfile.write("-" * 80 + "\n\n")
            
            # Write all pages
            for page_data in content['pages']:
                outfile.write(f"\n--- PAGE {page_data['page_num']} ---\n\n")
                outfile.write(page_data['text'])
                outfile.write("\n")
            
            print(f"  ✓ Extracted {content['num_pages']} pages")
        
        outfile.write("\n" + "="*80 + "\n")

print("\n" + "="*80)
print("EXTRACTION COMPLETE!")
print(f"All content saved to: {OUTPUT_FILE}")
print("="*80)
print("\nYou can now provide this file to Claude for analysis.")
print("File size:", end=" ")

# Show file size
try:
    size = os.path.getsize(OUTPUT_FILE)
    if size < 1024:
        print(f"{size} bytes")
    elif size < 1024*1024:
        print(f"{size/1024:.2f} KB")
    else:
        print(f"{size/(1024*1024):.2f} MB")
except:
    print("Unknown")

# Also create individual files
print("\nCreating individual topic files...")
for folder, filename, label in FILES_TO_PROCESS:
    pdf_path = os.path.join(BASE_DIR, folder, filename)
    individual_output = os.path.join(BASE_DIR, "extracted_texts", filename.replace(".pdf", ".txt"))
    
    content = extract_pdf_content(pdf_path)
    if 'error' not in content:
        with open(individual_output, 'w', encoding='utf-8') as f:
            f.write(f"{label}\n")
            f.write("="*80 + "\n\n")
            for page_data in content['pages']:
                f.write(f"\n--- PAGE {page_data['page_num']} ---\n\n")
                f.write(page_data['text'])
                f.write("\n")

print("✓ Individual files also created")
print("\nReady for analysis!")
