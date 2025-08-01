# AcadCheck - Academic Integrity Platform

## Overview
AcadCheck is a Flask-based web application designed to uphold academic integrity. It offers comprehensive analysis of uploaded documents (PDF, DOCX, TXT) for both plagiarism and AI-generated content. The platform's core purpose is to provide detailed reports, enabling users to identify and address potential academic integrity issues. It aims to offer a robust, multi-faceted detection system, combining external API strengths with sophisticated local algorithms to ensure high accuracy and reliability.

## User Preferences
Preferred communication style: Simple, everyday language.
Interface preference: Professional, corporate-style design with clean aesthetics.
Navigation preference: Simple arrow-based navigation between pages instead of complex floating buttons.
Button preference: Enhanced view buttons with eye icon and text labels for better visibility.

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
- **Complete Authentication System**: User registration, login/logout, role-based access (Student/Professor), demo mode
- **Security Hardening**: Input validation, malicious content detection, rate limiting, secure headers, CSRF protection
- **Real-time Monitoring**: System performance monitoring, error tracking, resource usage alerts, automated optimization
- **Robust File Processing**: Secure upload validation, multi-format support (PDF/DOCX/TXT), character encoding handling
- **3-Tier Detection System**: Improved local algorithm as primary, intelligent fallback, realistic academic scores (3-8%)
- **Performance Optimization**: Intelligent caching, memory management, database optimization, automatic cleanup
- **Professional UI**: Glassmorphism design, responsive interface, drag-and-drop uploads, real-time feedback
- **Comprehensive Testing**: Automated robustness tests, security validation, performance benchmarks

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