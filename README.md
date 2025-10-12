# Rishab Dixit's Portfolio Website

A modern, interactive portfolio website showcasing full-stack development skills, AI/ML projects, and professional experience. Built with Flask, featuring dynamic demos, responsive design, and advanced web technologies.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Interactive Demos](#interactive-demos)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Features

### Core Features
- **Responsive Portfolio Website** - Modern, mobile-first design
- **Interactive Contact System** - AJAX-powered contact form with JSON storage
- **Resume Downloads** - Multiple resume formats (Web Dev & Software Dev)
- **Certificates Section** - Downloadable certificates with verification
- **Dark/Light Theme** - Dynamic theme switching
- **Project Showcase** - Dynamic project cards with modals
- **Skill Analysis** - Interactive skill visualization with progress indicators

### AI/ML Demos
- **Mood Detector** - Real-time sentiment analysis using NLTK and scikit-learn
- **Student Pass Predictor** - ML model for predicting student performance
- **Code Execution Engine** - Multi-language code execution (Python, C++, Java, JS)

### Design Features
- **Glassmorphism UI** - Modern glass-effect design with backdrop blur
- **Smooth Animations** - CSS animations and JavaScript interactions
- **Professional Typography** - Inter font with optimized readability
- **Mobile Optimized** - Responsive design across all devices
- **Loading States** - Skeleton loaders and smooth transitions

## Tech Stack

### Backend
- **Flask** - Web framework for Python
- **SQLAlchemy** - Database ORM (for future enhancements)
- **Flask-Caching** - In-memory caching system
- **Flask-Mail** - Email functionality
- **Flask-WTF** - Form handling and validation

### Frontend
- **HTML5** - Semantic markup with modern standards
- **CSS3** - Advanced styling with Grid, Flexbox, and animations
- **JavaScript (ES6+)** - Modern JavaScript with async/await
- **Font Awesome** - Icon library
- **Google Fonts** - Inter typography

### AI/ML Libraries
- **scikit-learn** - Machine learning algorithms
- **NLTK** - Natural language processing
- **pandas** - Data manipulation
- **numpy** - Numerical computing
- **TensorFlow** - Deep learning framework

### Development Tools
- **pytest** - Testing framework
- **pre-commit** - Code quality hooks
- **Flask-Migrate** - Database migrations
- **Gunicorn** - WSGI server for production

## Installation

### Prerequisites
- Python 3.10+
- pip (Python package manager)
- Git (for version control)

### Step-by-Step Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/being-souL1230/My__portfolio.git
   cd My__portfolio
   ```

2. **Create Virtual Environment** (Recommended)
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Environment Variables** (Optional)
   Create a `.env` file:
   ```env
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here
   CACHE_TYPE=SimpleCache
   ```

5. **Run the Application**
   ```bash
   # Development mode
   python app.py

   # Or with specific host/port
   python app.py --host=0.0.0.0 --port=5000
   ```

6. **Access the Application**
   Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Project Structure

```
portfolio_website/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── runtime.txt                     # Python version specification
├── contact_submissions.json        # Contact form submissions
├── sentiment_model.pkl             # ML model for mood detection
├── .gitignore                     # Git ignore rules
├── .pre-commit-config.yaml        # Pre-commit hooks
├── pytest.ini                    # Pytest configuration
├── tests/                         # Test files
│   ├── test_app.py               # Application tests
│   ├── test_routes.py            # Route tests
│   └── test_ml.py                # ML model tests
├── static/                       # Static assets
│   ├── css/                      # Stylesheets
│   │   ├── main.css             # Main stylesheet (72KB)
│   │   ├── components.css       # Component styles
│   │   ├── sections.css         # Section-specific styles
│   │   ├── project-card.css     # Project card styles
│   │   ├── portfolio.css        # Portfolio-specific styles
│   │   ├── global.css           # Global styles
│   │   ├── dark-mode.css        # Dark theme styles
│   │   └── theme.css            # Theme management
│   ├── js/                      # JavaScript files
│   │   ├── main.js             # Main JavaScript (47KB)
│   │   ├── theme-switcher.js   # Theme switching logic
│   │   └── portfolio.js        # Portfolio functionality
│   ├── data/                    # Static data files
│   │   ├── AI for Beginners.pdf
│   │   ├── Introduction to Cybersecurity.pdf
│   │   └── Resume files
│   └── Rishab_image.jpeg       # Profile image
└── templates/                   # HTML templates
    ├── home.html               # Homepage
    ├── resume.html            # Resume page
    ├── certificates.html      # Certificates page
    ├── demos/                 # Interactive demos
    │   ├── mood_detector.html
    │   └── pass_predictor.html
    └── errors/               # Error pages
        ├── 404.html
        └── 500.html
```

## API Endpoints

### Contact System
- `POST /api/contact` - Submit contact form
- `GET /admin/contacts` - View contact submissions (Admin)

### AI/ML Features
- `POST /api/mood-analysis` - Analyze text sentiment
- `POST /api/pass-predict` - Predict student performance
- `POST /api/execute-code` - Execute code in multiple languages

### Static Files
- `GET /download/resume/web-developer` - Download web dev resume
- `GET /download/resume/software-developer` - Download software dev resume
- `GET /download/certificate/<id>` - Download certificates

## Interactive Demos

### 1. Mood Detector
**Location**: `/demo/mood-detector`
- **Technology**: NLTK, scikit-learn, Random Forest
- **Features**:
  - Real-time sentiment analysis
  - Text preprocessing with lemmatization
  - Confidence scoring with emotional intensity
  - ML-based classification with caching

### 2. Student Pass Predictor
**Location**: `/demo/pass-predictor`
- **Technology**: scikit-learn, Logistic Regression
- **Features**:
  - ML model for predicting student performance
  - 8 input factors (study hours, sleep, attendance, etc.)
  - Real-time prediction with confidence scores
  - Interactive cards with glassmorphism design

### 3. Code Execution Engine
**Supported Languages**:
- Python (interpreted)
- JavaScript (Node.js)
- C/C++ (compiled with GCC)
- Java (compiled with javac)

## Usage Guide

### For Visitors
1. **Homepage** - Browse skills, expertise, and projects
2. **Interactive Demos** - Try AI/ML features
3. **Resume Download** - Get professional resumes
4. **Contact Form** - Send messages via AJAX
5. **Certificates** - View and download certifications

### For Developers
1. **Local Development**:
   ```bash
   git clone <repository-url>
   cd portfolio_website
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   python app.py
   ```

2. **Testing**:
   ```bash
   pytest
   ```

3. **Code Quality**:
   ```bash
   pre-commit install
   pre-commit run --all-files
   ```

## Key Highlights

### Performance Optimizations
- **Caching System** - In-memory caching for ML predictions
- **Lazy Loading** - Optimized asset loading
- **Minified CSS/JS** - Reduced bundle sizes
- **Database Optimization** - Efficient JSON storage

### Security Features
- **Input Validation** - Form validation with Flask-WTF
- **XSS Protection** - Secure template rendering
- **CSRF Protection** - Cross-site request forgery prevention
- **File Upload Security** - Safe file handling

### Accessibility
- **WCAG Compliant** - Web accessibility standards
- **Keyboard Navigation** - Full keyboard support
- **Screen Reader Friendly** - Semantic HTML structure
- **High Contrast** - Dark/light theme support

## Deployment

### Local Deployment
```bash
# Development
python app.py

# Production with Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Production Deployment (Heroku/Vercel)
```bash
# Create requirements.txt with production dependencies
pip freeze > requirements.txt

# Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret-key
```

### Docker Deployment
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

## Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `pytest`
5. Commit changes: `git commit -m 'Add feature'`
6. Push to branch: `git push origin feature-name`
7. Submit a Pull Request

### Code Style
- Follow PEP 8 for Python code
- Use semantic HTML5 elements
- Follow BEM methodology for CSS
- Use ES6+ JavaScript features
- Add comments for complex logic

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_app.py

# Run with coverage
pytest --cov=app tests/
```

## Project Statistics

- **Total Files**: 50+ files
- **Lines of Code**: 20,000+ lines
- **CSS Size**: 72KB (main.css)
- **JavaScript Size**: 47KB (main.js)
- **Python Dependencies**: 200+ packages
- **Interactive Demos**: 2 AI/ML applications
- **Responsive Breakpoints**: 4 (desktop, tablet, mobile, small mobile)

## Recent Updates

### Version 2.0 Features
- Enhanced mood detection with advanced NLP
- Student pass predictor with ML model
- Interactive code execution engine
- Improved responsive design
- Advanced caching system
- Contact form with JSON storage

### Performance Improvements
- **Loading Speed**: Optimized with lazy loading
- **Memory Usage**: Efficient caching strategies
- **Bundle Size**: Minified and compressed assets
- **Database**: JSON-based storage for contacts

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

**Rishab Dixit**
- Full Stack Developer
- AI/ML Enthusiast
- GitHub: [being-souL1230](https://github.com/being-souL1230)
- LinkedIn: [Rishab Dixit](https://www.linkedin.com/in/rishab-dixit-6497aa357)
- Email: rishabdixit402@gmail.com

---

<div align="center">
  <p><strong>Built with love using Flask, HTML/CSS/JS, and AI/ML</strong></p>
  <p><em>Showcasing modern web development and machine learning skills</em></p>
</div>
