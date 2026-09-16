# OMR Processing System

A computer vision-based Optical Mark Recognition (OMR) processing system designed to automatically extract answers and candidate information from scanned OMR answer sheets and generate structured results.

## Overview

This project uses Python and OpenCV to process scanned OMR sheets, correct alignment issues, detect marked bubbles, extract candidate information, and generate automated result reports.

The system was developed during my AI/ML internship at M PRO9 Pvt. Ltd. and focuses on automating the evaluation workflow for scanned OMR answer sheets.

## Key Features

- Automated processing of scanned OMR answer sheets
- PDF/image processing and conversion
- Automatic detection of reference/alignment markers
- Image alignment and deskewing for skewed or misaligned scans
- Region of Interest (ROI) based answer extraction
- Bubble detection using computer vision and image masks
- Roll number and form/version extraction
- Detection of blank and multiple-marked responses
- Support for KCET and NEET-style OMR formats
- Automated result generation in Excel format
- Image-processing parameters and thresholds designed to improve robustness across different scan conditions

## Technology Stack

- **Python**
- **OpenCV**
- **Pandas**
- **NumPy**
- **PDF/Image Processing**
- **Excel Report Generation**

## Processing Workflow

```text
Scanned OMR PDF/Image
        ↓
PDF/Image Conversion
        ↓
Reference & Alignment Detection
        ↓
Perspective Correction / Deskewing
        ↓
Region of Interest Extraction
        ↓
Bubble Detection
        ↓
Answer & Candidate Information Extraction
        ↓
Result Processing
        ↓
Excel Report Generation
