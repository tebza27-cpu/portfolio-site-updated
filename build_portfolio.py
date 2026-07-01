import os

project_name = "portfolio_site"

# ---------- FILE CONTENTS ---------- #

app_py = """from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/cv')
def cv():
    return render_template('cv.html')

@app.route('/support')
def support():
    return render_template('support.html')

@app.route('/byu')
def byu():
    return render_template('byu.html')

@app.route('/cloud')
def cloud():
    return render_template('cloud.html')

@app.route('/cybersecurity')
def cybersecurity():
    return render_template('cybersecurity.html')

@app.route('/projects')
def projects():
    return render_template('projects.html')

@app.route('/certifications')
def certifications():
    return render_template('certifications.html')

@app.route('/skills')
def skills():
    return render_template('skills.html')

@app.route('/timeline')
def timeline():
    return render_template('timeline.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)
"""

style_css = """body {
    font-family: Arial;
    background: #f4f6f8;
    margin: 0;
}

nav {
    background: #1f2937;
    padding: 15px;
}

nav a {
    color: white;
    margin: 10px;
    text-decoration: none;
    font-weight: bold;
}

nav a:hover {
    color: #38bdf8;
}

.container {
    padding: 30px;
}

.card {
    background: white;
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.progress {
    background: #ddd;
    border-radius: 5px;
    margin-bottom: 10px;
}

.progress-bar {
    background: #38bdf8;
    color: white;
    padding: 5px;
}
"""

base_html = """<!DOCTYPE html>
<html>
<head>
<title>Sifiso Mokhele Portfolio</title>
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>

<nav>
<a href="/">Home</a>
<a href="/about">About</a>
<a href="/cv">CV</a>
<a href="/support">Support</a>
<a href="/byu">BYU Studies</a>
<a href="/cloud">Cloud</a>
<a href="/cybersecurity">Cybersecurity</a>
<a href="/projects">Projects</a>
<a href="/skills">Skills</a>
<a href="/timeline">Timeline</a>
<a href="/certifications">Certifications</a>
<a href="/contact">Contact</a>
</nav>

<div class="container">
{% block content %}{% endblock %}
</div>

</body>
</html>
"""

index_html = """{% extends "base.html" %}
{% block content %}
<div class="card">
<h1>Sifiso Mokhele</h1>
<p><strong>Technical Support Consultant | IT Support Specialist</strong></p>
<p>18+ years experience in IT support, ERP systems and service delivery.</p>
<p>Currently advancing skills in Cloud, Networking, Cybersecurity, and Data.</p>
</div>
{% endblock %}
"""

about_html = """{% extends "base.html" %}
{% block content %}
<div class="card">
<h1>About Me</h1>
<p>I am an IT Support and Systems Professional with over 18 years of experience.</p>
<p>I have worked across enterprise support, ERP systems and service delivery.</p>
<p>Currently pursuing a BAS in IT through BYU Pathway.</p>
</div>
{% endblock %}
"""

cv_html = """{% extends "base.html" %}
{% block content %}
<div class="card">
<h1>Experience</h1>
<ul>
<li>K8 Technical Lead – Klipboard</li>
<li>Helpdesk Analyst – Keyloop</li>
<li>Support Manager – Keyloop</li>
</ul>
<br>
<a href="{{ url_for('static', filename='Sifiso_Mokhele_CV.pdf') }}" download class="btn">
📄 Download My CV</a>
</div>
{% endblock %}
"""

support_html = """{% extends "base.html" %}
{% block content %}
<div class="card">
<h1>Technical Support Experience</h1>
<ul>
<li>ERP Support</li>
<li>Enterprise troubleshooting</li>
</ul>
</div>
{% endblock %}
"""

byu_html = """{% extends "base.html" %}
{% block content %}
<div class="card">
<h1>BYU Pathway Studies</h1>
<h3>Completed</h3>
<ul>
<li>Technical Support Engineering Certificate</li>
<li>Cloud Server Administration</li>
<li>Networking Fundamentals</li>
<li>PC Hardware Technician</li>
</ul>
<h3>In Progress</h3>
<ul>
<li>Business Intelligence Systems</li>
<li>Advanced Linux</li>
<li>Cybersecurity Foundations</li>
</ul>
</div>
{% endblock %}
"""

cloud_html = """{% extends "base.html" %}
{% block content %}
<div class="card">
<h1>Cloud & Networking</h1>
<p>Networking, cloud fundamentals, and system administration basics.</p>
</div>
{% endblock %}
"""

cybersecurity_html = """{% extends "base.html" %}
{% block content %}
<div class="card">
<h1>Cybersecurity</h1>
<p>Security fundamentals and risk awareness.</p>
</div>
{% endblock %}
"""

projects_html = """{% extends "base.html" %}
{% block content %}
<div class="card">
<h1>Projects</h1>
<ul>
<li>Flask Portfolio Website</li>
<li>Networking Labs</li>
</ul>
</div>
{% endblock %}
"""

skills_html = """{% extends "base.html" %}
{% block content %}
<div class="card">
<h1>Skills</h1>
<p>Technical Support, Networking, Cloud, SQL</p>
</div>
{% endblock %}
"""

timeline_html = """{% extends "base.html" %}
{% block content %}
<div class="card">
<h1>Timeline</h1>
<ul>
<li>2004 Diploma</li>
<li>2025 Technical Lead</li>
</ul>
</div>
{% endblock %}
"""

certifications_html = """{% extends "base.html" %}
{% block content %}
<div class="card">
<h1>Certifications</h1>
<ul>
<li>Technical Support Engineering</li>
</ul>
</div>
{% endblock %}
"""

contact_html = """{% extends "base.html" %}
{% block content %}
<div class="card">
<h1>Contact</h1>
<p>Email: smokhele@byupathway.edu</p>
<p>Phone: 064 937 3653</p>
</div>
{% endblock %}
"""

files = {
    "base.html": base_html,
    "index.html": index_html,
    "about.html": about_html,
    "cv.html": cv_html,
    "support.html": support_html,
    "byu.html": byu_html,
    "cloud.html": cloud_html,
    "cybersecurity.html": cybersecurity_html,
    "projects.html": projects_html,
    "skills.html": skills_html,
    "timeline.html": timeline_html,
    "certifications.html": certifications_html,
    "contact.html": contact_html,
}

for name, content in files.items():
    path = os.path.join(templates_dir, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

css = """
body { font-family: Arial; background:#f4f6f8; margin:0; }
nav { background:#1f2937; padding:15px; }
nav a { color:white; margin:10px; text-decoration:none; }
nav a:hover { color:#38bdf8; }
.container { padding:20px; }
.card { background:white; padding:20px; margin-bottom:20px; border-radius:8px; box-shadow:0 2px 5px rgba(0,0,0,0.1); }
.btn { background:#38bdf8; color:white; padding:10px; text-decoration:none; border-radius:5px; }
"""

with open(os.path.join(static_dir, "style.css"), "w", encoding="utf-8") as f:
    f.write(css)

print("✅ FULL PORTFOLIO SITE FIXED SUCCESSFULLY")
print("👉 Now run: python app.py")
