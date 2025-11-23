# ISIT312 Exam Preparation - Extraction & Analysis Tools

## What This Folder Contains

This folder contains tools to extract and analyze your ISIT312 lecture materials for efficient exam preparation.

## Files Created

### Extraction Scripts
- **extract_consolidated.py** - ⭐ RECOMMENDED - Creates one master file with all content
- **extract_all_pdfs.py** - Creates individual text files for each lecture
- **run_extraction.bat** - Windows batch file to run extraction easily

### Output Directories
- **extracted_texts/** - Contains extracted text from all PDFs
  - `ALL_CONTENT.txt` - Master file with all lectures (created by extract_consolidated.py)
  - Individual .txt files for each lecture
- **Notes/** - Will contain organized topic-wise study notes
- **analysis/** - Will contain analysis and cramming plan

## How to Use

### Step 1: Extract PDF Content

**Option A - Recommended (Creates master file):**
```cmd
cd G:\School\ISIT312\Exam_prep
python extract_consolidated.py
```

**Option B - Alternative:**
```cmd
cd G:\School\ISIT312\Exam_prep
python extract_all_pdfs.py
```

**Option C - Double-click:**
- Just double-click `run_extraction.bat`

### Step 2: Provide Content to Claude

After extraction completes, tell Claude:
"The extraction is complete. Please read the extracted content and create my study materials."

### Step 3: Review Generated Materials

Claude will create:
1. **Topic Summaries** (`analysis/syllabus_and_topics_summary.md`)
   - 3-5 sentence summaries per topic
   - Key concepts, models, techniques
   - Important definitions and equations

2. **Cramming Plan** (`analysis/cramming_plan.md`)
   - Topic prioritization based on exam weightage
   - Study time allocation
   - Prerequisites and dependencies

3. **Detailed Notes** (`Notes/` folder)
   - One file per topic
   - Comprehensive coverage with examples
   - Exam-focused content
   - Easy to read and structured

## Requirements

- Python 3.6 or higher
- PyPDF2 library (will be installed automatically)

## Troubleshooting

### "Python is not recognized"
1. Install Python from https://www.python.org/downloads/
2. During installation, check "Add Python to PATH"

### "No module named 'PyPDF2'"
Run: `pip install PyPDF2`

### Extraction errors
Try alternative extraction method:
```cmd
pip install pdfplumber
```
Then use the pdfplumber-based extraction (see manual_extract.py comments)

## Course Coverage

This preparation material covers all ISIT312 topics:

### Part 1: Big Data Processing (Lectures 1-8)
- Cluster Computing
- MapReduce Framework & Model
- Hadoop Architecture
- HDFS Interfaces
- Java MapReduce Applications
- Hive Introduction & Data Structures

### Part 2: Data Warehousing (Lectures 9-14)
- DW Concepts & Design
- Logical & Physical DW Design
- SQL for Data Warehousing
- Hive Programming

### Part 3: NoSQL & Streaming (Lectures 15-20)
- HBase Data Model & Operations
- Spark Introduction & Data Model
- Spark Operations & Streaming

### Review Material
- Lecture 21: Subject Review
- Sample Exam Paper

## Next Steps

After extraction:
1. Read through the topic summaries
2. Follow the cramming plan
3. Study the detailed notes topic by topic
4. Practice with the sample exam
5. Focus on high-weightage topics

## Questions?

If you encounter any issues or need clarification on any topic, just ask Claude!

---
Created for ISIT312 Exam Preparation
Last Updated: November 2025
