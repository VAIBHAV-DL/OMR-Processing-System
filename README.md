# OMR Processing System

A computer vision-based Optical Mark Recognition (OMR) processing system for automatically extracting candidate information and marked responses from scanned OMR answer sheets and generating structured Excel result reports.

The system is designed to process KCET and NEET-style OMR answer sheets using image processing, geometric correction, region-based extraction, and bubble detection techniques.

---

## Overview

This project was developed during my AI/ML internship at **M PRO9 Pvt. Ltd.** as part of an automation workflow for processing scanned OMR answer sheets.

The system takes scanned OMR documents in PDF format, processes each page, detects the relevant regions and marked bubbles, extracts candidate information and responses, validates the detected markings, and generates structured Excel reports.

The implementation contains separate processing workflows for **KCET** and **NEET-style OMR formats**.

---

## Key Features

- Automated processing of scanned OMR answer sheets
- PDF-to-image conversion for scanned documents
- Reference marker detection for page alignment
- Perspective correction and deskewing
- Region of Interest (ROI) based extraction
- Computer vision-based bubble detection
- Candidate information extraction
- Roll number extraction
- Booklet/version code extraction
- Detection of blank responses
- Detection of multiple-marked responses
- KCET-specific OMR processing
- NEET-specific OMR processing
- Automated Excel result generation
- Configurable image-processing thresholds and coordinates

---

## Processing Workflow

```text
Scanned OMR PDF / Image
          ↓
PDF / Image Conversion
          ↓
Reference Marker Detection
          ↓
Perspective Correction / Deskewing
          ↓
Region of Interest Extraction
          ↓
Bubble Detection
          ↓
Candidate Information & Answer Extraction
          ↓
Response Validation
          ↓
Result Processing
          ↓
Excel Report Generation
```

---

## Supported OMR Formats

### KCET

The KCET processing workflow handles the structure and layout of the KCET-style OMR sheets, including:

- Candidate information
- Roll number
- Version code
- Answer bubbles
- Blank responses
- Multiple-marked responses
- Structured result generation

### NEET

The NEET processing workflow handles NEET-style OMR sheets, including:

- Roll number
- Test booklet information
- Booklet code
- Answer bubbles
- Blank responses
- Multiple-marked responses
- Structured Excel output

---

## Project Structure

```text
OMR-Processing-System/
├── NEET.py
├── kcet_omr_engine.py
├── requirements.txt
├── README.md
└── .gitignore
```

### File Description

| File | Description |
|------|-------------|
| `NEET.py` | Processing engine for NEET-style OMR sheets |
| `kcet_omr_engine.py` | Processing engine for KCET-style OMR sheets |
| `requirements.txt` | Python dependencies required by the project |
| `README.md` | Project documentation |
| `.gitignore` | Prevents generated files, local environments, and unnecessary files from being committed |

---

## Technologies Used

- **Python**
- **OpenCV**
- **NumPy**
- **Pandas**
- **PyMuPDF**
- **openpyxl**
- **Computer Vision**
- **Image Processing**
- **Excel Report Generation**

---

## Core Computer Vision Techniques

### 1. PDF to Image Conversion

Scanned OMR PDF pages are converted into images so that computer vision operations can be performed on individual pages.

### 2. Reference Marker Detection

Reference markers present on the OMR sheet are used to determine the page geometry and establish consistent coordinates for further processing.

### 3. Perspective Correction

Perspective transformation is applied to compensate for alignment and scanning variations and to bring the OMR sheet into a standardized orientation.

### 4. Region of Interest Extraction

Specific regions of the processed image are isolated for:

- Candidate information
- Roll number
- Booklet/version information
- Answer sections

This reduces unnecessary image processing outside the relevant areas.

### 5. Bubble Detection

The system analyzes the OMR response regions to determine whether bubbles are:

- Unmarked
- Validly marked
- Multiple marked

Detected responses are converted into structured answer values.

### 6. Response Validation

The extracted responses are classified so that blank and multiple-marked responses are not incorrectly treated as valid answers.

### 7. Excel Report Generation

The extracted candidate information and responses are written into structured Excel files for further use and analysis.

---

## Output

The system generates Excel reports containing information such as:

```text
Page
Roll Number
Booklet / Version Code
Q1
Q2
Q3
...
Q200
```

Depending on the OMR format, the number of questions and candidate-information fields can vary.

Example response values:

```text
A
B
C
D
-
*
```

Where:

```text
A / B / C / D → Detected answer
-             → Blank / unmarked response
*             → Multiple-marked / invalid response
```

---

## Running the Project

### 1. Clone the repository

```bash
git clone https://github.com/VAIBHAV-DL/OMR-Processing-System.git
cd OMR-Processing-System
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

#### Windows

```bash
venv\Scripts\activate
```

#### Linux / macOS

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the NEET processor

```bash
python NEET.py
```

### 6. Run the KCET processor

```bash
python kcet_omr_engine.py
```

---

## Input and Output

The processing scripts use the project's configured input and output directories.

Example:

```text
OMR-Processing-System/
├── input/
│   ├── NEET/
│   └── kcet/
│
└── output/
    ├── NEET_Results.xlsx
    └── OMR_Results.xlsx
```

**Input files and generated result files are intentionally excluded from version control where appropriate through `.gitignore`.**

---

## Validation

The processing pipeline has been tested using sample KCET and NEET-style OMR documents.

The generated responses were manually compared against the source OMR sheets to verify the extracted:

- Candidate information
- Roll numbers
- Booklet/version information
- Marked responses
- Blank responses
- Multiple-marked responses

The current implementation successfully generates structured Excel results from the tested OMR inputs.

---

## Design Considerations

OMR documents can contain variations caused by:

- Scanning alignment
- Page rotation
- Perspective distortion
- Image quality
- Printing variations
- Bubble marking differences

The processing pipeline therefore uses geometric correction, region-specific extraction, and configurable image-processing parameters rather than relying only on fixed image dimensions.

---

## Limitations

- The processing coordinates and thresholds are configured for the supported OMR layouts.
- Different OMR designs may require new coordinates or processing parameters.
- Detection accuracy can depend on scan quality and document condition.
- The system is currently focused on the supported KCET and NEET-style layouts.

---

## Future Improvements

Potential extensions include:

- Support for additional OMR formats
- Automatic OMR template configuration
- Improved robustness across different scan resolutions
- Confidence scoring for detected responses
- Batch-processing interface
- Graphical user interface
- Automated result analytics
- Database integration
- Deployment as a web-based OMR processing service

---

## Internship Context

This project was developed as part of my **AI/ML internship at M PRO9 Pvt. Ltd.**

The work involved applying computer vision and image-processing techniques to automate the extraction of information from scanned OMR answer sheets and convert the extracted data into structured reports.

---

## Author

**Vaibhav Balekundri**

Bachelor of Engineering — Artificial Intelligence and Data Science

---

## License

This project is intended primarily for educational, portfolio, and demonstration purposes.
