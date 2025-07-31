# AcadCheck - Academic Integrity Platform

## Overview
AcadCheck is a Flask-based web application designed to uphold academic integrity. It offers comprehensive analysis of uploaded documents (PDF, DOCX, TXT) for both plagiarism and AI-generated content. The platform's core purpose is to provide detailed reports, enabling users to identify and address potential academic integrity issues. It aims to offer a robust, multi-faceted detection system, combining external API strengths with sophisticated local algorithms to ensure high accuracy and reliability.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask with SQLAlchemy ORM (declarative base)
- **Database**: SQLAlchemy supporting SQLite (local) and PostgreSQL (production)
- **Authentication**: Dual system: OAuth (Flask-Dance) for production, simplified local for development
- **File Processing**: Multi-format document parsing with text extraction
- **API Integration**: Multi-provider plagiarism detection with intelligent fallback and demo modes
- **Detection System**:
    - **Plagiarism**: Three-tier system (Copyleaks → PlagiarismCheck → Local Turnitin-style algorithm) utilizing n-grams, fingerprints, pattern analysis, structural metrics, Sentence-BERT, TF-IDF, Jaccard similarity, and character-level matching. Includes a local plagiarism database for cross-document similarity detection and academic content calibration.
    - **AI Content**: Eight-layer detection system (ML model, academic/business/tech keywords, syntax patterns, formal transitions, sentence length, sophisticated vocabulary, perplexity/burstiness analysis). Includes an intelligent scoring system and a highly accurate SimpleAIDetector for local/offline operation.

### Frontend Architecture
- **Template Engine**: Jinja2 with Bootstrap 5
- **Styling**: Custom CSS for academic-themed, responsive design
- **JavaScript**: Vanilla JS for UI enhancements (drag-and-drop, file upload)
- **Icons**: Font Awesome

### Data Storage
- **Primary Database**: SQLAlchemy (SQLite/PostgreSQL) for user, document, and analysis results
- **File Storage**: Local filesystem for uploaded documents
- **Reports**: PDF generation using WeasyPrint

### Key Features
- **Role-Based Access**: User roles (Student, Professor, Admin)
- **Multi-API Support**: Configurable primary/secondary API, with intelligent fallback to local algorithms or demo mode
- **File Processing Pipeline**: Secure upload, text extraction, analysis queuing, and report generation
- **Sentence Highlighting**: Comprehensive sentence-level highlighting in reports with intelligent phrase detection and realistic source attribution.
- **Dynamic Filenaming**: Customizable download filenames for analysis reports.
- **Original Document Layout**: System to display documents exactly as they appear on user's computer with preserved formatting, title pages, and academic structure.

## External Dependencies

### Required APIs
- **Copyleaks API**: Primary plagiarism and AI detection service
- **PlagiarismCheck API**: Alternative plagiarism detection service

### Python Packages
- **Flask**: Web framework and extensions (SQLAlchemy, Login, Dance)
- **Document Processing**: PyPDF2, python-docx
- **PDF Generation**: WeasyPrint
- **Database**: psycopg2-binary (PostgreSQL)
- **Security**: JWT, python-dotenv
- **Machine Learning**: scikit-learn, numpy (for local detection algorithms)

### Frontend Dependencies
- **Bootstrap 5**: UI framework (CDN)
- **Font Awesome**: Icon library (CDN)