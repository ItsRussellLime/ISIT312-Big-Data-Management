import PyPDF2
import sys
import json
import os

def read_pdf(path):
    """Read a PDF and return its content"""
    try:
        with open(path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text_content = []
            
            for i, page in enumerate(reader.pages):
                text_content.append(f"\n{'='*80}\n")
                text_content.append(f"PAGE {i + 1} of {len(reader.pages)}\n")
                text_content.append(f"{'='*80}\n\n")
                text_content.append(page.extract_text())
            
            return ''.join(text_content)
    except Exception as e:
        return f"ERROR: {str(e)}"

def read_all_lectures():
    """Read all lecture PDFs and save to one consolidated file"""
    base_dir = r"G:\School\ISIT312\Exam_prep"
    
    files = [
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
    
    output_file = os.path.join(base_dir, "extracted_texts", "ALL_CONTENT.txt")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as out:
        out.write("="*80 + "\n")
        out.write("ISIT312 - ALL LECTURE CONTENT\n")
        out.write("="*80 + "\n\n")
        
        for folder, filename in files:
            filepath = os.path.join(base_dir, folder, filename)
            print(f"Processing: {filename}")
            
            out.write("\n\n" + "#"*80 + "\n")
            out.write(f"FILE: {filename}\n")
            out.write("#"*80 + "\n")
            
            content = read_pdf(filepath)
            out.write(content)
            out.write("\n" + "="*80 + "\n")
            
            # Also create individual file
            indiv_file = os.path.join(base_dir, "extracted_texts", filename.replace(".pdf", ".txt"))
            with open(indiv_file, 'w', encoding='utf-8') as f:
                f.write(content)
    
    print(f"\nDone! Output: {output_file}")
    return output_file

if __name__ == "__main__":
    output = read_all_lectures()
    print(f"All content extracted to: {output}")
