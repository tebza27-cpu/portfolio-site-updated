import os

base_dir = r"C:\Users\User\portfolio_site"
templates_dir = os.path.join(base_dir, "templates")
static_dir = os.path.join(base_dir, "static")

# Ensure folders exist
os.makedirs(templates_dir, exist_ok=True)
os.makedirs(static_dir, exist_ok=True)

# ---------- BASE TEMPLATE ----------
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

# ---------- PAGE TEMPLATE FUNCTION ----------
def create_page(title, body):
    return f"""{{% extends "base.html" %}}
{{% block content %}}

<div class="card">
<h1>{title}</h1>
{body}
</div>

{{% endblock %}}
"""

# ---------- PAGES ----------
files = {
    "base.html": base_html,
    "index.html": create_page("Sifiso Mokhele",
        """<p><strong>Technical Support Consultant | IT Support Specialist</strong></p>
<p>18+ years experience in IT support, ERP systems and service delivery.</p>

<a href="{{ url_for('static', filename='Sifiso_Mokhele_CV.pdf') }}" download class="btn">
📄 Download My CV</a>"""),

    "about.html": create_page("About Me",
        "<p>IT Support professional with 18+ years experience.</p>"),

    "cv.html": create_page("Professional Experience",
        """<ul>
<li>K8 Technical Lead – Klipboard</li>
<li>Helpdesk Analyst – Keyloop</li>
<li>Support Manager – Keyloop</li>
</ul>
<br>
<a href="{{ url_for('static', filename='Sifiso_Mokhele_CV.pdf') }}" download class="btn">
📄 Download My CV</a>"""),

    "support.html": create_page("Technical Support Experience",
        "<ul><li>ERP Support</li><li>Enterprise troubleshooting</li></ul>"),

    "byu.html": create_page("BYU Pathway Studies",
        """<h3>Completed</h3>
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
</ul>"""),

    "cloud.html": create_page("Cloud & Networking",
        "<p>Networking, cloud fundamentals, system admin basics</p>"),

    "cybersecurity.html": create_page("Cybersecurity",
        "<p>Security fundamentals and risk awareness</p>"),

    "projects.html": create_page("Projects",
        "<ul><li>Flask Portfolio Website</li><li>Networking Labs</li></ul>"),

    "skills.html": create_page("Skills",
        "<p>Technical Support, Networking, Cloud, SQL</p>"),

    "timeline.html": create_page("Timeline",
        "<ul><li>2004 Diploma</li><li>2025 Technical Lead</li></ul>"),

    "certifications.html": create_page("Certifications",
        "<ul><li>Technical Support Engineering</li></ul>"),

    "contact.html": create_page("Contact",
        """<p>Email: smokhele@byupathway.edu</p>
<p>Phone: 064 937 3653</p>"""),
}

# ---------- WRITE FILES ----------
for name, content in files.items():
    path = os.path.join(templates_dir, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

# ---------- CSS ----------
css = """
body { font-family: Arial; background:#f4f6f8; margin:0; }
nav { background:#1f2937; padding:15px; }
nav a { color:white; margin:10px; text-decoration:none; }
.container { padding:20px; }
.card { background:white; padding:20px; margin-bottom:20px; }
.btn { background:#38bdf8; color:white; padding:10px; text-decoration:none; border-radius:5px; }
"""

with open(os.path.join(static_dir, "style.css"), "w") as f:
    f.write(css)

print("✅ FULL PORTFOLIO SITE FIXED SUCCESSFULLY")
print("👉 Now run: python app.py")