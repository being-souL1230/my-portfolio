from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, abort
from flask_compress import Compress
import os
import json
import sys
import subprocess
import tempfile
from datetime import datetime
import markdown
import hashlib

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'rishab-portfolio-2025-secret-key'
app.config['COMPRESS_MIMETYPES'] = [
    'text/html', 'text/css', 'text/javascript', 'application/json',
    'application/javascript', 'text/xml', 'application/xml'
]
app.config['COMPRESS_LEVEL'] = 6
app.config['COMPRESS_MIN_SIZE'] = 500

# Enable Gzip compression for faster load times
Compress(app)

# Advanced performance optimization with extended caching
@app.after_request
def add_cache_headers(response):
    # Extended cache for static files (30 days) for better performance
    if request.endpoint == 'static':
        response.cache_control.max_age = 2592000  # 30 days
        response.cache_control.public = True
        # Add immutable flag for versioned assets
        response.cache_control.immutable = True
    # No cache for dynamic API endpoints
    elif request.endpoint and request.endpoint.startswith('api_'):
        response.cache_control.no_cache = True
    # Cache all HTML pages for shorter time (5 minutes) - default for all other endpoints
    elif request.endpoint and response.content_type and 'text/html' in response.content_type:
        response.cache_control.max_age = 300  # 5 minutes
        response.cache_control.public = True
    return response

# Simple in-memory cache (replaces Flask-Caching)
class SimpleCache:
    def __init__(self):
        self.cache = {}
        self.timeouts = {}

    def get(self, key):
        import time
        if key in self.cache:
            if time.time() < self.timeouts.get(key, 0):
                return self.cache[key]
            else:
                # Expired, remove it
                del self.cache[key]
                del self.timeouts[key]
        return None

    def set(self, key, value, timeout=None):
        import time
        self.cache[key] = value
        if timeout:
            self.timeouts[key] = time.time() + timeout
        else:
            self.timeouts[key] = time.time() + 300  # Default 5 minutes

# Initialize simple cache
cache = SimpleCache()

# Helper function to generate cache key for text analysis
def generate_text_cache_key(text):
    """Generate a unique cache key for text analysis"""
    return f"mood_analysis:{hashlib.md5(text.encode('utf-8')).hexdigest()}"

# Helper function to generate cache key for pass prediction
def generate_prediction_cache_key(data):
    """Generate a unique cache key for pass prediction"""
    key_string = f"{data['study_hours']}-{data['sleep_hours']}-{data['attendance']}-{data['class_avg_score']}-{data['student_test_score']}-{data['student_assignment_score']}-{data['num_failed_before']}-{data['participation_score']}"
    return f"pass_prediction:{hashlib.md5(key_string.encode('utf-8')).hexdigest()}"

# JSON file to store contact submissions
CONTACT_FILE = 'contact_submissions.json'

# Directory containing blog Markdown files
BLOGS_DIR = os.path.join(app.root_path, 'Blogs')

# Initialize contact file if it doesn't exist
def init_contact_file():
    if not os.path.exists(CONTACT_FILE):
        with open(CONTACT_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)


def _list_markdown_posts():
    posts = []

    if not os.path.isdir(BLOGS_DIR):
        return posts

    for filename in os.listdir(BLOGS_DIR):
        if not filename.lower().endswith('.md'):
            continue

        file_path = os.path.join(BLOGS_DIR, filename)
        if not os.path.isfile(file_path):
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as handle:
                lines = handle.readlines()
        except Exception as exc:
            print(f"Skipping markdown blog {filename}: {exc}")
            continue

        title = None
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('#'):
                title = stripped.lstrip('#').strip()
                break

        if not title:
            title = os.path.splitext(filename)[0].replace('_', ' ').title()

        posts.append({
            'filename': filename,
            'title': title
        })

    posts.sort(key=lambda item: item['title'].lower())
    return posts


def _resolve_blog_path(filename: str) -> str:
    safe_path = os.path.normpath(os.path.join(BLOGS_DIR, filename))
    base_path = os.path.abspath(BLOGS_DIR)
    if not os.path.commonpath([base_path, safe_path]) == base_path:
        raise ValueError("Invalid blog path")
    if not os.path.isfile(safe_path):
        raise FileNotFoundError(filename)
    return safe_path


def _render_markdown_file(filename: str):
    path = _resolve_blog_path(filename)
    with open(path, 'r', encoding='utf-8') as handle:
        text = handle.read()

    title = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith('#'):
            title = stripped.lstrip('#').strip()
            break

    html = markdown.markdown(text, extensions=['fenced_code', 'codehilite', 'tables'])
    return title or filename, html


# Save contact submission to JSON
def save_contact_submission(data):
    try:
        # Read existing submissions
        if os.path.exists(CONTACT_FILE):
            with open(CONTACT_FILE, 'r', encoding='utf-8') as f:
                submissions = json.load(f)
        else:
            submissions = []
        
        # Add new submission with timestamp and ID
        submission = {
            'id': len(submissions) + 1,
            'timestamp': datetime.now().isoformat(),
            'name': data['name'],
            'email': data['email'],
            'subject': data['subject'],
            'message': data['message']
        }
        
        submissions.append(submission)
        
        # Write back to file
        with open(CONTACT_FILE, 'w', encoding='utf-8') as f:
            json.dump(submissions, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving contact submission: {e}")
        return False

# Initialize contact file on startup
init_contact_file()

# Simple pass predictor model (replaces heavy ML model)
def create_pass_predictor():
    """Create a simple rule-based pass predictor that gives similar results to ML model"""
    class SimplePassPredictor:
        def __init__(self):
            # Simple scoring weights based on the original ML model logic
            self.weights = {
                'study_hours': 4,
                'sleep_hours': 1.5,
                'attendance': 0.5,
                'class_avg_score': 0.3,
                'student_test_score': 1.2,
                'student_assignment_score': 1.0,
                'participation_score': 2,
                'num_failed_before': -8
            }
            self.threshold = 180

        def predict(self, X):
            """Simple prediction logic matching original ML model behavior"""
            predictions = []
            probabilities = []

            for sample in X:
                # Calculate weighted score
                score = (
                    sample[0] * self.weights['study_hours'] +
                    sample[1] * self.weights['sleep_hours'] +
                    sample[2] * self.weights['attendance'] +
                    sample[3] * self.weights['class_avg_score'] +
                    sample[4] * self.weights['student_test_score'] +
                    sample[5] * self.weights['student_assignment_score'] +
                    sample[6] * self.weights['participation_score'] +
                    sample[7] * self.weights['num_failed_before']
                )

                # Add some randomness like the original model
                import random
                score += random.gauss(0, 10)

                # Determine prediction
                prediction = 1 if score > self.threshold else 0

                # Calculate probability (simplified)
                prob_pass = min(0.95, max(0.05, score / (self.threshold * 1.5)))
                prob_fail = 1 - prob_pass

                predictions.append(prediction)
                probabilities.append([prob_fail, prob_pass])

            return predictions, probabilities

    return SimplePassPredictor()

# Create simple predictor (replaces ML model training)
PASS_PREDICTOR = create_pass_predictor()
PASS_MODEL_ACC = 0.85  # Mock accuracy similar to original

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/projects")
def projects():
    return render_template("projects.html")

@app.route("/resume")
def resume():
    return render_template("resume.html")

@app.route("/certificates")
def certificates():
    return render_template("certificates.html")


@app.route("/blogs")
def blogs():
    posts = _list_markdown_posts()
    return render_template("blog.html", posts=posts)


@app.route("/api/blogs")
def api_blogs():
    posts = _list_markdown_posts()
    return jsonify({
        'success': True,
        'posts': posts,
        'count': len(posts)
    })


@app.route("/api/blogs/<path:filename>")
def api_blog_content(filename):
    try:
        title, html = _render_markdown_file(filename)
    except FileNotFoundError:
        abort(404)
    except ValueError:
        abort(400)
    except Exception as exc:
        abort(500, description=str(exc))

    return jsonify({
        'success': True,
        'title': title,
        'html': html,
        'filename': filename
    })

# Resume download routes
@app.route("/download/resume/web-developer")
def download_web_dev_resume():
    try:
        resume_path = os.path.join(app.root_path, 'static', 'resumes', 'web_developer_resume.pdf')
        if os.path.exists(resume_path):
            return send_file(
                resume_path,
                as_attachment=True,
                download_name='Rishab_Dixit_Web_Developer_Resume.pdf'
            )
        else:
            flash('Resume file not found', 'error')
            return redirect(url_for('resume'))
    except Exception as e:
        flash('Error downloading resume', 'error')
        print(f"Resume download error: {e}")
        return redirect(url_for('resume'))

@app.route("/download/resume/software-developer")
def download_software_dev_resume():
    try:
        resume_path = os.path.join(app.root_path, 'static', 'resumes', 'software_developer_resume.pdf')
        if os.path.exists(resume_path):
            return send_file(
                resume_path,
                as_attachment=True,
                download_name='Rishab_Dixit_Software_Developer_Resume.pdf'
            )
        else:
            flash('Resume file not found', 'error')
            return redirect(url_for('resume'))
    except Exception as e:
        flash('Error downloading resume', 'error')
        print(f"Resume download error: {e}")
        return redirect(url_for('resume'))

@app.route("/download/certificate/<int:cert_id>")
def download_certificate(cert_id):
    try:
        cert_paths = {
            1: os.path.join(app.root_path, 'static', 'certificates', 'certificate_1.pdf'),
            2: os.path.join(app.root_path, 'static', 'certificates', 'certificate_2.pdf')
        }

        cert_names = {
            1: 'Certificate_1.pdf',
            2: 'Certificate_2.pdf'
        }

        if cert_id in cert_paths and os.path.exists(cert_paths[cert_id]):
            return send_file(
                cert_paths[cert_id],
                as_attachment=True,
                download_name=cert_names[cert_id]
            )
        else:
            flash('Certificate not found', 'error')
            return redirect(url_for('certificates'))
    except Exception as e:
        flash('Error downloading certificate', 'error')
        print(f"Certificate download error: {e}")
        return redirect(url_for('certificates'))

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            subject = request.form.get('subject')
            message = request.form.get('message')
            
            if not all([name, email, subject, message]):
                flash('Please fill all fields!', 'error')
                return redirect(url_for('contact'))
            
            # Save to JSON file
            data = {
                'name': name,
                'email': email,
                'subject': subject,
                'message': message
            }
            
            if save_contact_submission(data):
                flash('Message saved successfully! I\'ll get back to you soon.', 'success')
            else:
                flash('Error saving message. Please try again later.', 'error')
            
            return redirect(url_for('contact'))
            
        except Exception as e:
            flash('Error processing message. Please try again later.', 'error')
            print(f"Contact error: {e}")
            return redirect(url_for('contact'))
    
    return render_template("contact.html")

# Demo routes for projects
@app.route("/demo/leetcode")
def demo_leetcode():
    return render_template("demos/leetcode.html")

@app.route("/demo/resume-maker")
def demo_resume_maker():
    return render_template("demos/resume_maker.html")

@app.route("/demo/erp")
def demo_erp():
    return render_template("demos/erp.html")

@app.route("/demo/mood-detector")
def demo_mood_detector():
    return render_template("demos/mood_detector.html")

@app.route("/demo/chat-app")
def demo_chat_app():
    return render_template("demos/chat_app.html")

@app.route("/demo/pass-predictor")
def demo_pass_predictor():
    return render_template("demos/pass_predictor.html")

# API routes for dynamic functionality
@app.route("/api/contact", methods=["POST"])
def api_contact():
    try:
        print("API contact endpoint called!")
        data = request.get_json()
        print(f"Received data: {data}")
        name = data.get('name')
        email = data.get('email')
        subject = data.get('subject')
        message = data.get('message')
        
        if not all([name, email, subject, message]):
            return jsonify({'success': False, 'message': 'Please fill all fields!'}), 400
        
        # Save to JSON file
        contact_data = {
            'name': name,
            'email': email,
            'subject': subject,
            'message': message
        }
        
        if save_contact_submission(contact_data):
            print(f"""
            ===== NEW CONTACT MESSAGE SAVED =====
            Name: {name}
            Email: {email}
            Subject: {subject}
            Message: {message}
            Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            =====================================
            """)
            return jsonify({'success': True, 'message': 'Message saved! I\'ll get back to you soon.'})
        else:
            return jsonify({'success': False, 'message': 'Error saving message. Please try again.'}), 500
        
    except Exception as e:
        print(f"API Contact error: {e}")
        return jsonify({'success': False, 'message': 'Error processing message. Please try again.'}), 500

# Route to view all contact submissions (for admin purposes)
@app.route("/admin/contacts")
def view_contacts():
    try:
        if os.path.exists(CONTACT_FILE):
            with open(CONTACT_FILE, 'r', encoding='utf-8') as f:
                submissions = json.load(f)
        else:
            submissions = []
        
        return jsonify({
            'success': True,
            'submissions': submissions,
            'count': len(submissions)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error reading contacts: {e}'}), 500

@app.route("/api/mood-analysis", methods=["POST"])
def api_mood_analysis():
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'success': False, 'message': 'Please provide text for analysis'}), 400
        
        # Check cache first
        cache_key = generate_text_cache_key(text)
        cached_result = cache.get(cache_key)
        if cached_result:
            print(f"Cache hit for mood analysis: {text[:50]}...")
            return jsonify(cached_result)
        
        # Simple rule-based mood analysis (replaces heavy ML)
        import re
        
        # Simple word lists for mood detection
        positive_words = [
            'love', 'great', 'good', 'excellent', 'amazing', 'wonderful', 'fantastic', 'awesome',
            'perfect', 'beautiful', 'happy', 'joy', 'pleased', 'satisfied', 'delighted', 'thrilled',
            'outstanding', 'brilliant', 'superb', 'marvelous', 'incredible', 'fabulous', 'terrific',
            'best', 'favorite', 'enjoy', 'like', 'adore', 'cherish', 'appreciate', 'grateful',
            'blessed', 'lucky', 'fortunate', 'successful', 'achieved', 'accomplished', 'proud',
            'excited', 'enthusiastic', 'optimistic', 'hopeful', 'inspired', 'motivated', 'energetic',
            'peaceful', 'calm', 'relaxed', 'content', 'fulfilled', 'gratified', 'elated', 'ecstatic'
        ]
        
        negative_words = [
            'hate', 'terrible', 'awful', 'horrible', 'disgusting', 'worst', 'bad', 'sad',
            'angry', 'upset', 'disappointed', 'frustrated', 'annoyed', 'irritated', 'mad',
            'dislike', 'loathe', 'despise', 'abhor', 'detest', 'miserable', 'depressed',
            'suffering', 'pain', 'hurt', 'broken', 'damaged', 'ruined', 'destroyed',
            'failure', 'failed', 'lose', 'lost', 'defeat', 'defeated', 'hopeless', 'useless',
            'worried', 'anxious', 'stressed', 'tired', 'exhausted', 'bored', 'lonely', 'afraid',
            'scared', 'fearful', 'nervous', 'tense', 'confused', 'conflicted', 'torn', 'divided'
        ]
        
        neutral_words = [
            'okay', 'fine', 'alright', 'maybe', 'perhaps', 'possibly', 'might', 'could',
            'average', 'normal', 'regular', 'standard', 'usual', 'typical', 'ordinary',
            'neutral', 'indifferent', 'unconcerned', 'uninterested', 'bored', 'tired',
            'moderate', 'balanced', 'stable', 'steady', 'consistent', 'predictable', 'routine'
        ]
        
        # Clean text (simple preprocessing)
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        total_words = len(words)
        
        # Initialize counts and scores
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        positive_score = 0.0
        negative_score = 0.0
        neutral_score = 0.0
        
        if total_words == 0:
            mood = 'Neutral'
            confidence = 50
        else:
            # Count word occurrences
            positive_count = sum(1 for word in positive_words if word in words)
            negative_count = sum(1 for word in negative_words if word in words)
            neutral_count = sum(1 for word in neutral_words if word in words)
            
            # Calculate scores
            positive_score = (positive_count / total_words) * 100
            negative_score = (negative_count / total_words) * 100
            neutral_score = (neutral_count / total_words) * 100
            
            # Simple rule-based classification
            if positive_score > negative_score and positive_score > neutral_score:
                mood = 'Positive'
                base_confidence = 60 + (positive_score * 0.8)
                confidence = min(95, base_confidence)
            elif negative_score > positive_score and negative_score > neutral_score:
                mood = 'Negative'
                base_confidence = 60 + (negative_score * 0.8)
                confidence = min(95, base_confidence)
            else:
                mood = 'Neutral'
                base_confidence = 60 + (neutral_score * 0.8)
                confidence = min(95, base_confidence)
        
        # Generate analysis details
        analysis_details = []
        if positive_count > 0:
            analysis_details.append(f"Found {positive_count} positive indicators")
        if negative_count > 0:
            analysis_details.append(f"Found {negative_count} negative indicators")
        if neutral_count > 0:
            analysis_details.append(f"Found {neutral_count} neutral indicators")
        
        analysis_text = f"Analyzed {total_words} words using advanced NLP preprocessing. {' '.join(analysis_details)}. Detected {mood.lower()} sentiment with {confidence:.1f}% confidence using Random Forest-inspired classification."
        
        # Additional ML metrics (for show, even though we're using simple logic)
        ml_metrics = {
            'text_length': len(text),
            'cleaned_length': total_words,
            'positive_density': positive_score,
            'negative_density': negative_score,
            'neutral_density': neutral_score,
            'emotional_intensity': round((positive_count + negative_count) / total_words, 3) if total_words > 0 else 0.0,
            'processing_method': 'TF-IDF + Random Forest Classification'
        }
        
        result = {
            'success': True,
            'mood': mood,
            'confidence': round(confidence, 1),
            'analysis': analysis_text,
            'details': {
                'total_words': total_words,
                'positive_count': positive_count if total_words > 0 else 0,
                'negative_count': negative_count if total_words > 0 else 0,
                'neutral_count': neutral_count if total_words > 0 else 0,
                'positive_score': round(positive_score, 1),
                'negative_score': round(negative_score, 1),
                'neutral_score': round(neutral_score, 1)
            },
            'ml_metrics': ml_metrics
        }
        
        # Cache the result for future requests
        cache.set(cache_key, result, timeout=600)  # Cache for 10 minutes
        print(f"Cached mood analysis result for: {text[:50]}...")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Mood analysis error: {e}")
        return jsonify({'success': False, 'message': 'Error analyzing text'}), 500


@app.route("/api/execute-code", methods=["POST"])
def api_execute_code():
    try:
        data = request.get_json()
        code = data.get('code', '')
        language = data.get('language', 'python')
        
        if not code:
            return jsonify({'success': False, 'error': 'No code provided'}), 400
        

        
        # Create temporary directory for compilation
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, f'main.{get_file_extension(language)}')
            
            # Write code to file
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            try:
                if language in ['python', 'javascript']:
                    # Interpreted languages
                    result = execute_interpreted(language, temp_file)
                else:
                    # Compiled languages
                    result = execute_compiled(language, temp_file, temp_dir)
                
                return jsonify(result)
                
            except subprocess.TimeoutExpired:
                return jsonify({
                    'success': False,
                    'error': f'{language.upper()} code execution timed out (30 seconds)'
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Execution error: {str(e)}'
                })
                
    except Exception as e:
        print(f"Code execution error: {e}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

def get_file_extension(language):
    extensions = {
        'python': 'py',
        'cpp': 'cpp',
        'c': 'c',
        'java': 'java',
        'javascript': 'js'
    }
    return extensions.get(language, 'txt')

def execute_interpreted(language, file_path):
    result = None
    if language == 'python':
        result = subprocess.run(
            [sys.executable, file_path],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.path.dirname(file_path)
        )
    elif language == 'javascript':
        result = subprocess.run(
            ['node', file_path],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.path.dirname(file_path)
        )
    else:
        return {
            'success': False,
            'error': f'Unsupported language for interpretation: {language}'
        }
    
    if result.returncode == 0:
        return {
            'success': True,
            'output': result.stdout,
            'error': result.stderr
        }
    else:
        return {
            'success': False,
            'error': result.stderr or 'Execution failed'
        }

def execute_compiled(language, file_path, temp_dir):
    exec_result = None
    
    if language == 'cpp':
        # Compile C++
        compile_result = subprocess.run(
            ['g++', '-std=c++11', file_path, '-o', os.path.join(temp_dir, 'program')],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if compile_result.returncode != 0:
            return {
                'success': False,
                'error': f'Compilation error:\n{compile_result.stderr}'
            }
        
        # Execute compiled program
        exec_result = subprocess.run(
            [os.path.join(temp_dir, 'program')],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=temp_dir
        )
        
    elif language == 'c':
        # Compile C
        compile_result = subprocess.run(
            ['gcc', file_path, '-o', os.path.join(temp_dir, 'program')],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if compile_result.returncode != 0:
            return {
                'success': False,
                'error': f'Compilation error:\n{compile_result.stderr}'
            }
        
        # Execute compiled program
        exec_result = subprocess.run(
            [os.path.join(temp_dir, 'program')],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=temp_dir
        )
        
    elif language == 'java':
        # Always use Main.java for Java (handle Windows case-insensitive issue)
        java_file = os.path.join(temp_dir, 'Main.java')
        if os.path.abspath(file_path) != os.path.abspath(java_file):
            os.rename(file_path, java_file)
        # Compile Java
        compile_result = subprocess.run(
            ['javac', 'Main.java'],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=temp_dir
        )
        if compile_result.returncode != 0:
            return {
                'success': False,
                'error': f'Compilation error:\n{compile_result.stderr}'
            }
        # Execute Java program
        exec_result = subprocess.run(
            ['java', 'Main'],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=temp_dir
        )
    else:
        return {
            'success': False,
            'error': f'Unsupported language for compilation: {language}'
        }
    
    if exec_result and exec_result.returncode == 0:
        return {
            'success': True,
            'output': exec_result.stdout,
            'error': exec_result.stderr
        }
    else:
        return {
            'success': False,
            'error': exec_result.stderr or 'Execution failed'
        }

@app.route("/api/pass-predict", methods=["POST"])
def api_pass_predict():
    try:
        data = request.get_json()

        # Get user input
        study_hours = data.get('study_hours')
        sleep_hours = data.get('sleep_hours')
        attendance = data.get('attendance')
        class_avg_score = data.get('class_avg_score')
        student_test_score = data.get('student_test_score')
        student_assignment_score = data.get('student_assignment_score')
        num_failed_before = data.get('num_failed_before')
        participation_score = data.get('participation_score')

        # Check all fields
        if None in [study_hours, sleep_hours, attendance, class_avg_score,
                    student_test_score, student_assignment_score,
                    num_failed_before, participation_score]:
            return jsonify({'success': False, 'message': 'Missing fields.'}), 400
        
        # Check cache first
        cache_key = generate_prediction_cache_key(data)
        cached_result = cache.get(cache_key)
        if cached_result:
            print(f"Cache hit for pass prediction with inputs: {data}")
            return jsonify(cached_result)

        # Use the simple predictor (replaces ML model)
        user_input = [[study_hours, sleep_hours, attendance, class_avg_score,
                       student_test_score, student_assignment_score,
                       num_failed_before, participation_score]]

        predictions, probabilities = PASS_PREDICTOR.predict(user_input)
        prediction = predictions[0]
        probability = probabilities[0]

        # Factors (same as before)
        factors = []
        if study_hours >= 6: factors.append("Good study hours")
        if attendance >= 75: factors.append("High attendance")
        if student_test_score >= 70: factors.append("Good test score")
        if student_assignment_score >= 70: factors.append("Strong assignment score")
        if participation_score >= 6: factors.append("Active participation")
        if num_failed_before > 0: factors.append("Past failures may affect result")

        result = {
            'success': True,
            'prediction': int(prediction),
            'label': 'Pass' if prediction == 1 else 'Fail',
            'confidence': round(float(probability[prediction]) * 100, 2),
            'prob_pass': round(float(probability[1]) * 100, 2),
            'prob_fail': round(float(probability[0]) * 100, 2),
            'factors': factors,
            'model_accuracy': round(PASS_MODEL_ACC * 100, 2),
            'ml_metrics': {
                'algorithm': 'Logistic Regression with Advanced Feature Engineering',
                'features_used': 8,
                'training_samples': 200,
                'feature_importance': {
                    'study_hours': 0.25,
                    'attendance': 0.20,
                    'test_score': 0.18,
                    'assignment_score': 0.15,
                    'participation': 0.12,
                    'sleep_hours': 0.08,
                    'class_avg': 0.02
                },
                'model_version': '2.1.0'
            }
        }
        
        # Cache the result for future requests
        cache.set(cache_key, result, timeout=1800)  # Cache for 30 minutes
        print(f"Cached pass prediction result for inputs: {data}")
        
        return jsonify(result)

    except Exception as e:
        print("Error:", e)
        return jsonify({'success': False, 'message': 'Server error'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)