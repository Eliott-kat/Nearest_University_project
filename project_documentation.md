# AcadCheck - Academic Integrity Platform

## Overview

AcadCheck is a Flask-based web application that provides academic integrity services by combining plagiarism detection with AI-generated content analysis. The platform allows users to upload documents (PDF, DOCX, TXT) and receive comprehensive analysis reports highlighting potential plagiarism and AI-generated content sections.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

**July 26, 2025:**
- Fixed critical "Not Found" issue in local installation by ensuring routes.py import in run_local.py
- Successfully deployed SQLite-based local version with real Copyleaks API integration
- Application now fully functional with dashboard, upload, analysis, and PDF report generation
- Real-time Copyleaks API authentication configured (currently server experiencing 500 errors, falls back to demo mode)
- Created comprehensive local installation scripts (run_local.py, quick_start.py) for easy deployment
- **NEW: Multi-API Support** - Added infrastructure to switch between Copyleaks and PlagiarismCheck APIs
- Created migration scripts and documentation for easy API switching  
- Enhanced .env configuration with PLAGIARISM_API_PROVIDER option
- **NEW: Smart Fallback System** - Fixed automatic fallback between APIs when one fails
- Created comprehensive token acquisition guide for PlagiarismCheck API
- **NEW: Dual API Fallback** - Simplified to Copyleaks → GPTZero → Demo mode
- GPTZero provides both AI detection (99%+) and plagiarism checking as reliable fallback

## System Architecture

### Backend Architecture
- **Framework**: Flask with SQLAlchemy ORM
- **Database**: SQLAlchemy with declarative base (configured for external database via DATABASE_URL)
- **Authentication**: OAuth-based authentication system using Flask-Dance with secure integration
- **File Processing**: Multi-format document processing (PDF, DOCX, TXT) with text extraction
- **External API Integration**: Copyleaks API for plagiarism and AI detection services

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 UI framework
- **Styling**: Custom CSS with academic-themed color scheme and responsive design
- **JavaScript**: Vanilla JavaScript for file upload enhancements, drag-and-drop functionality, and UI interactions
- **Icons**: Font Awesome for consistent iconography

### Authentication System
- **OAuth Provider**: Custom authentication system with Flask-Dance
- **Session Management**: Flask-Login with persistent sessions
- **User Roles**: Role-based access control (Student, Professor, Admin)
- **Security**: ProxyFix middleware for proper header handling in deployment

## Key Components

### Models (models.py)
- **User**: User management with role-based permissions and OAuth integration
- **Document**: Document metadata, file paths, and analysis status tracking
- **AnalysisResult**: Stores plagiarism scores, AI detection results, and analysis metadata
- **HighlightedSentence**: Individual flagged sentences with confidence scores
- **OAuth**: OAuth token storage with browser session tracking

### Services
- **CopyleaksService**: Handles API authentication, document submission, and result processing
- **ReportGenerator**: Creates HTML and PDF reports with highlighted text sections
- **FileUtils**: Document processing and text extraction from multiple formats

### Core Routes
- **Landing/Dashboard**: Role-based interface (public landing vs authenticated dashboard)
- **Document Upload**: Multi-format file upload with progress tracking
- **Analysis Display**: Detailed results with highlighted problematic sections
- **Report Generation**: Downloadable PDF reports with comprehensive analysis
- **Admin Panel**: System-wide statistics and user management (admin-only)

## Data Flow

1. **Document Upload**: User uploads document → File validation → Text extraction → Database storage
2. **Analysis Submission**: Document sent to Copyleaks API → Status tracking → Webhook processing
3. **Result Processing**: API response parsed → Highlighted sentences identified → Analysis results stored
4. **Report Generation**: Results compiled → HTML template rendered → Optional PDF export
5. **User Access**: Dashboard displays analysis status → Detailed report viewing → Download options

## External Dependencies

### Core Dependencies
- **Flask**: Web framework with SQLAlchemy ORM integration
- **Copyleaks API**: Primary plagiarism and AI detection service
- **Flask-Dance**: OAuth authentication handling
- **PyPDF2**: PDF text extraction
- **python-docx**: Word document processing
- **WeasyPrint**: PDF report generation from HTML

### UI Dependencies
- **Bootstrap 5**: Responsive UI framework
- **Font Awesome**: Icon library
- **Custom CSS**: Academic-themed styling with highlight functionality

### Configuration Requirements
- `DATABASE_URL`: Database connection string
- `SESSION_SECRET`: Flask session encryption key
- `COPYLEAKS_EMAIL`: Copyleaks API account email
- `COPYLEAKS_API_KEY`: Copyleaks API authentication key

## Deployment Strategy

### Environment Configuration
- **Upload Directory**: Configurable file storage location (default: 'uploads')
- **File Size Limits**: 16MB maximum upload size
- **Database**: External database via environment variable
- **Proxy Configuration**: ProxyFix for deployment behind reverse proxy

### File Management
- **Upload Storage**: Local filesystem with unique filename generation
- **Report Storage**: Generated reports stored in uploads/reports subdirectory
- **Text Processing**: In-memory processing with extracted content cached in database

### Security Considerations
- **File Validation**: Strict file type checking and secure filename handling
- **Role-based Access**: Granular permissions for different user types
- **Session Security**: Secure session management with browser session tracking
- **API Security**: Secure token handling for external service integration

The application follows a traditional MVC pattern with clear separation between data models, business logic services, and presentation layers. The architecture supports scalability through external database integration and modular service design.