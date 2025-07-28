# AcadCheck - Academic Integrity Platform

## Overview

AcadCheck is a Flask-based web application that provides academic integrity services by combining plagiarism detection with AI-generated content analysis. The platform allows users to upload documents (PDF, DOCX, TXT) for comprehensive analysis and generates detailed reports highlighting potential issues.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask with SQLAlchemy ORM using declarative base pattern
- **Database**: SQLAlchemy with configurable database support (SQLite for local, PostgreSQL for production)
- **Authentication**: Dual authentication system - OAuth-based for production (Flask-Dance) and simplified local authentication for development
- **File Processing**: Multi-format document processing with text extraction utilities
- **API Integration**: Multi-provider plagiarism detection with smart fallback system

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 UI framework
- **Styling**: Custom CSS with academic-themed design and responsive layout
- **JavaScript**: Vanilla JavaScript for enhanced file upload, drag-and-drop, and UI interactions
- **Icons**: Font Awesome for consistent iconography

### Data Storage
- **Primary Database**: SQLAlchemy with support for SQLite (local) and PostgreSQL (production)
- **File Storage**: Local filesystem storage in uploads directory
- **Reports**: PDF generation using WeasyPrint for analysis reports

## Key Components

### Models (models.py)
- **User**: User management with role-based permissions (Student, Professor, Admin)
- **Document**: Document metadata, file paths, and analysis status tracking
- **AnalysisResult**: Stores plagiarism and AI detection scores
- **HighlightedSentence**: Stores sentence-level analysis for highlighting in reports
- **OAuth**: OAuth token storage for authenticated sessions

### Authentication System
The application supports two authentication modes:
- **Production Mode**: OAuth-based authentication using Flask-Dance with session management
- **Local Mode**: Simplified authentication with fake user for local development

### API Integration Layer
- **Multi-Provider Support**: Configurable switching between Copyleaks and PlagiarismCheck APIs
- **Smart Fallback**: Automatic failover between APIs when primary service is unavailable
- **Demo Mode**: Realistic analysis simulation when APIs are unavailable

### File Processing Pipeline
1. **Upload Handler**: Secure file upload with validation and virus scanning considerations
2. **Text Extraction**: Support for PDF, DOCX, and TXT formats
3. **Analysis Queue**: Document processing with status tracking
4. **Report Generation**: HTML and PDF report creation with highlighted content

## Data Flow

1. **Document Upload**: User uploads document through drag-and-drop interface
2. **Text Extraction**: System extracts plain text from uploaded file
3. **API Analysis**: Document is submitted to configured plagiarism detection API
4. **Results Processing**: API response is parsed and stored in database
5. **Report Generation**: Detailed analysis report is generated with highlighted issues
6. **User Access**: User can view online report or download PDF version

## External Dependencies

### Required APIs
- **Copyleaks API**: Primary plagiarism and AI detection service
- **PlagiarismCheck API**: Alternative plagiarism detection service (fallback)

### Python Packages
- **Flask**: Web framework and extensions (SQLAlchemy, Login, Dance)
- **Document Processing**: PyPDF2, python-docx for file parsing
- **PDF Generation**: WeasyPrint for report creation
- **Database**: psycopg2-binary for PostgreSQL, SQLite for local development
- **Security**: JWT, python-dotenv for configuration management

### Frontend Dependencies
- **Bootstrap 5**: UI framework loaded via CDN
- **Font Awesome**: Icon library loaded via CDN
- **Custom CSS/JS**: Local assets for enhanced functionality

## Deployment Strategy

### Local Development
- **Database**: SQLite for simplicity and no external dependencies
- **Configuration**: `.env` file-based configuration with sensible defaults
- **Launch Scripts**: Multiple entry points (main.py, run_local.py, quick_start.py)
- **Authentication**: Bypass mode with fake user for testing

### Production Deployment
- **Database**: PostgreSQL with connection pooling and health checks
- **Authentication**: Full OAuth integration with user management
- **API Integration**: Real API keys with fallback mechanisms
- **File Security**: Proper upload directory permissions and size limits

### Configuration Management
- **Environment Variables**: All sensitive data stored in environment variables
- **API Switching**: Runtime switching between plagiarism detection providers
- **Fallback Logic**: Automatic degradation to demo mode when APIs unavailable

### Multi-API Support
The application includes a dual-API switching system:
- **Primary Provider**: Configurable via `PLAGIARISM_API_PROVIDER` environment variable (copyleaks/plagiarismcheck)
- **Automatic Fallback**: When primary API fails, system automatically tries secondary API
- **Demo Mode**: When all APIs fail, system provides realistic simulated analysis
- **Status Tracking**: Real-time monitoring of API availability and performance

### Recent Changes (July 28, 2025)
- **AI Detection Service Removed**: GPTZero integration removed due to authentication issues
- **Simplified Architecture**: Now supports only Copyleaks and PlagiarismCheck APIs
- **Database Schema Updated**: Added support for sources_count, analysis_provider, and raw_response fields
- **Admin Dashboard Cleaned**: Removed references to AI Detection Service
- **Improved Stability**: Dual-provider system with robust fallback mechanism