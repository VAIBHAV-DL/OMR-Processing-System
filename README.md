# OMR Processing System

A computer vision-based Optical Mark Recognition (OMR) processing system for automatically extracting candidate information and marked responses from scanned OMR answer sheets and generating structured result reports.

## Overview

This project was developed during my AI/ML internship at **M PRO9 Pvt. Ltd.** as part of an automation workflow for processing scanned OMR answer sheets.

The system uses image-processing and computer-vision techniques to handle scanned OMR documents, correct alignment issues, detect marked bubbles, extract candidate information and answers, identify blank or multiple-marked responses, and generate structured Excel reports.

The implementation includes processing workflows for **KCET and NEET-style OMR formats**.

## Key Features

- Automated processing of scanned OMR answer sheets
- PDF-to-image conversion for scanned documents
- Reference marker detection for alignment
- Perspective correction and deskewing
- Region of Interest (ROI) based extraction
- Computer vision-based bubble detection
- Roll number and form/version extraction
- Detection of blank responses
- Detection of multiple-marked responses
- KCET and NEET-specific processing workflows
- Automated Excel result generation
- Image-processing thresholds and parameters for handling variations in scanned documents

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
Candidate Information & Answer Extraction
        ↓
Response Validation
        ↓
Result Processing
        ↓
Excel Report Generation
