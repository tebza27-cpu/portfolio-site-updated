from flask import Flask, render_template, send_file, abort, request, jsonify, url_for, redirect
from pathlib import Path
import os
import json
import base64
import mimetypes
import subprocess
import sys
import shlex
import secrets
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from datetime import datetime
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    psycopg2 = None
    RealDictCursor = None

app = Flask(__name__)

# -------- HELPER FUNCTIONS --------
def is_local_access():
    """Check if the request is from a local network or localhost"""
    remote_addr = request.remote_addr
    # Localhost
    if remote_addr in ('127.0.0.1', '::1', 'localhost'):
        return True
    # Private IP ranges
    if remote_addr.startswith('192.168.') or remote_addr.startswith('10.') or remote_addr.startswith('172.'):
        return True
    return False

def is_safe_path(file_path, allowed_base_paths):
    """Verify that file_path is within allowed directories (prevent directory traversal)"""
    try:
        real_path = os.path.realpath(file_path)
        for allowed_base in allowed_base_paths:
            allowed_real = os.path.realpath(allowed_base)
            if real_path.startswith(allowed_real):
                return True
        return False
    except:
        return False

# -------- COURSE MATERIALS PATHS --------
ONEDRIVE_BASE_PATH = r"C:\Users\User\OneDrive - BYU-Pathway Worldwide\BYU"

# Allowed paths for file viewing (security)
ALLOWED_PATHS = [
    r"F:\BYU",
    r"C:\Users\User\OneDrive - BYU-Pathway Worldwide\Documents",
    r"C:\Users\User\OneDrive - BYU-Pathway Worldwide\Recordings"
]

# OneDrive recordings folder (shared recordings link)
RECORDINGS_ONEDRIVE_LINK = "https://byupathwayworldwideprod-my.sharepoint.com/:f:/g/personal/smokhele_byupathway_edu/IgAAXsavR2q1RL4dYvxeoZNaAawbscjq6BRRRRoVZIk2Ewo?e=mQKQon"

SKILLS_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'skills.json')
TESTIMONIALS_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'testimonials.json')
TESTIMONIAL_INVITES_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'testimonial_invites.json')
SKILLS_API_KEY = os.environ.get('SKILLS_API_KEY')


def _normalize_database_url(raw_url):
    if not raw_url:
        return None
    try:
        p = urlparse(raw_url)
        scheme = p.scheme
        if scheme == 'postgres':
            scheme = 'postgresql'

        # Preserve existing query params and add sslmode=require when appropriate
        query = dict(parse_qsl(p.query, keep_blank_values=True))
        host = p.hostname or ''
        is_local = host in ('localhost', '127.0.0.1', '')
        if not is_local and 'sslmode' not in query:
            query['sslmode'] = 'require'

        new_query = urlencode(query)
        new_p = p._replace(scheme=scheme, query=new_query)
        return urlunparse(new_p)
    except Exception as e:
        # If parsing fails, return the raw value and log a warning
        try:
            app.logger.warning(f"Could not normalize DATABASE_URL: {e}")
        except Exception:
            pass
        return raw_url

def send_testimonial_invite_email(recipient_email, recipient_name, submit_url):
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    smtp_from = os.getenv('SMTP_FROM', os.getenv('RECIPIENT_EMAIL', smtp_user or 'no-reply@portfolio-site-updated.git'))
    smtp_use_tls = os.getenv('SMTP_USE_TLS', 'true').lower() not in ('false', '0', 'no')
    smtp_use_ssl = os.getenv('SMTP_USE_SSL', 'false').lower() in ('true', '1', 'yes')
    smtp_timeout = float(os.getenv('SMTP_TIMEOUT', '20'))

    if not smtp_host or not smtp_user or not smtp_password:
        return False, 'SMTP is not configured. Set SMTP_HOST, SMTP_USERNAME, and SMTP_PASSWORD.'

    msg = EmailMessage()
    msg['Subject'] = 'Testimonial invitation from Sifiso Mokhele'
    msg['From'] = formataddr(('Sifiso Mokhele', smtp_from))
    msg['To'] = recipient_email
    msg.set_content(
        f"Hello {recipient_name or 'there'},\n\n"
        "You have been invited to submit a testimonial for Sifiso Mokhele.\n\n"
        f"Please use the following secure link to submit your feedback: {submit_url}\n\n"
        "Thank you for your time and support.\n\n"
        "Best regards,\n"
        "Sifiso Mokhele"
    )
    msg.add_alternative(
        f"<html><body><p>Hello {recipient_name or 'there'},</p>"
        f"<p>You have been invited to submit a testimonial for <strong>Sifiso Mokhele</strong>.</p>"
        f"<p>Please use the following secure link to submit your feedback:<br><a href=\"{submit_url}\">{submit_url}</a></p>"
        "<p>Thank you for your time and support.</p>"
        "<p>Best regards,<br>Sifiso Mokhele</p>"
        "</body></html>", subtype='html'
    )

    try:
        if smtp_use_ssl:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=smtp_timeout) as server:
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=smtp_timeout) as server:
                server.ehlo()
                if smtp_use_tls:
                    server.starttls()
                    server.ehlo()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
        return True, f'Invitation email sent to {recipient_email}.'
    except smtplib.SMTPConnectError as exc:
        return False, f'Unable to connect to SMTP server at {smtp_host}:{smtp_port}: {exc}'
    except OSError as exc:
        return False, f'Network error connecting to SMTP server at {smtp_host}:{smtp_port}: {exc}'
    except Exception as exc:
        app.logger.exception('Failed to send testimonial invite email')
        return False, f'Failed to send invitation email: {exc}'


CLOUD_SECTION_TITLES = {
    "Business Description and Research",
    "Deployment Model",
    "Service Model",
    "Cloud Design for your Business",
    "Additional Business Research",
    "Procedures when ISP goes down",
    "Virtual Private Network",
    "Kinds of Files Stored",
    "How will the Business Connect?",
    "Domain Name System",
    "Storage Providers",
    "Content Delivery Network",
    "Research",
    "Baseline",
    "Feasibility",
    "Gap Analysis",
    "Capital and Operating Expenditures",
    "Potential Cloud Vendors",
    "Variable and Fixed Costs",
    "Licensing Model",
    "Evaluation of Cloud Vendors",
    "Service Level Agreement",
    "Migration Principles",
    "Aspects of Operating",
    "Development & Operations",
    "Financial Planning",
    "Data Sovereignty",
    "Regulatory Concerns",
    "Industry-Based Requirements",
    "International Standards",
    "Certifications",
    "Security Concerns, Measures, and Concepts",
    "Risk Assessment",
    "Risk Response",
    "Documentation",
    "Vendor Lock-In",
    "Policies and Procedures",
    "Benefits:",
    "Table of Contents"
}

SKIP_LINES = {
    "Cloud Solution",
    "for",
    "Keyloop",
    "By Sifiso Mokhele",
    "Table of Contents"
}


def _group_cloud_body_lines(lines):
    groups = []
    current = {'title': 'Overview', 'content': []}

    for line in lines:
        if not line:
            continue
        if line.startswith('Page '):
            continue
        if line in SKIP_LINES:
            continue
        if line in CLOUD_SECTION_TITLES or line.endswith(':'):
            if current['content']:
                groups.append(current)
            current = {'title': line, 'content': []}
            continue
        if len(line.split()) <= 7 and line == line.title() and not line.endswith('.') and ':' not in line:
            if current['content']:
                groups.append(current)
            current = {'title': line, 'content': []}
            continue
        current['content'].append(line)

    if current['content']:
        groups.append(current)

    return groups


def _prepare_cloud_project(project):
    if project.get('image'):
        project['image'] = project['image'].replace('\\', '/')
    else:
        project['image'] = 'images/cloud_solution_proposal.svg'

    cloud_image_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images')
    if not project.get('images') and os.path.isdir(cloud_image_folder):
        extracted_images = sorted(
            f for f in os.listdir(cloud_image_folder)
            if f.startswith('cloud_doc_image_') and f.lower().endswith(('.png', '.jpg', '.jpeg', '.svg'))
        )
        if extracted_images:
            project['images'] = [os.path.join('images', img).replace('\\', '/') for img in extracted_images]

    if project.get('sections', {}).get('body'):
        body = [line.strip() for line in project['sections']['body'] if line and line.strip()]
        project['section_groups'] = _group_cloud_body_lines(body)
    else:
        project['section_groups'] = []

    if not project.get('summary') or project['summary'].strip().lower() in {'cloud solution', 'cloud solution\n\nfor\n\nkeyloop'}:
        project['summary'] = 'Cloud solution proposal for Keyloop that defines a secure hybrid cloud architecture, compliance strategy, and vendor evaluation to support global dealership operations.'

    project['client'] = project.get('client', 'Keyloop')
    project['industry'] = project.get('industry', 'Automotive Retail')
    project['case_study'] = {
        'title': 'Keyloop Cloud Transformation Case Study',
        'subtitle': 'A strategic hybrid cloud architecture for global automotive retail operations.',
        'points': [
            'Designed for connected dealer management, service, and analytics capabilities.',
            'Built to meet regional data sovereignty needs across GDPR and POPIA zones.',
            'Focused on resilient networking, storage, security, and SaaS integration readiness.',
            'Provides a phased migration roadmap with vendor evaluation and governance controls.'
        ]
    }

    if not project.get('focus') or len(project['focus']) > 6:
        project['focus'] = [
            'Hybrid cloud architecture with private and public cloud balance.',
            'Security and data governance aligned to automotive retail regulations.',
            'Multi-region resilience with DNS redundancy, VPN, and CDN optimization.',
            'Phased migration approach designed for confidence and operational readiness.'
        ]

    if not project.get('attachments'):
        project['attachments'] = []

    return project


def _get_database_url_from_env():
    raw = os.environ.get('DATABASE_URL') or os.environ.get('RENDER_DATABASE_URL') or os.environ.get('POSTGRES_URL')
    return _normalize_database_url(raw)


DATABASE_URL = _get_database_url_from_env()

STATIC_BI_PROJECTS = [
    {
        'title': 'Heritage Vault 20 Infrastructure Proposal',
        'link': 'https://byupathwayworldwideprod-my.sharepoint.com/:p:/g/personal/smokhele_byupathway_edu/IQDiCok6HxO-S6u3aLUKq3gYAa84iZHDmip6oa_ke8r7h8Y?e=cfWDzx',
        'asset_type': 'PowerPoint',
        'description': 'Infrastructure proposal presentation for Heritage Vault 20.',
        'source': 'BYU Pathway Power BI / Infrastructure'
    },
    {
        'title': 'Heritage Vault 20 Infrastructure Proposal Video',
        'link': 'https://byupathwayworldwideprod-my.sharepoint.com/:v:/g/personal/smokhele_byupathway_edu/IQD4mI2UJxSpQazfzF-4zIwGAZ4LdeLHBDjQcFV5q5YaTtM?e=ejk9zd',
        'asset_type': 'Video',
        'description': 'Presentation video for the Heritage Vault 20 infrastructure proposal.',
        'source': 'BYU Pathway Video Submission'
    },
    {
        'title': 'Sample Files - Present Analysis in PowerBI',
        'link': 'https://byupathwayworldwideprod-my.sharepoint.com/:u:/g/personal/smokhele_byupathway_edu/IQBSsq5Cvf14TrNuLMCxfiI3ASP8KEeca8sjKIOaO4B18lk?e=nVDlH3',
        'asset_type': 'Power BI Report',
        'description': 'Sample Power BI files for presenting analysis.',
        'source': 'BYU Pathway Power BI'
    },
    {
        'title': 'Project 4 - Presenting Analysis',
        'link': 'https://byupathwayworldwideprod-my.sharepoint.com/:u:/g/personal/smokhele_byupathway_edu/IQC4kFr-vFTERZ6xHnQYK_iUAZm9GpwjTRsmKjeK5NDWtb0?e=9YDbK1',
        'asset_type': 'Power BI Report',
        'description': 'Project 4 Power BI report for presenting analysis results.',
        'source': 'BYU Pathway Power BI'
    },
    {
        'title': 'Project 1 - Baseball Dataset, Part 6',
        'link': 'https://byupathwayworldwideprod-my.sharepoint.com/:u:/g/personal/smokhele_byupathway_edu/IQASaL0ZppeARLetMq_hFy8UAXJ0po2sh3A221swZpl_Rbg?e=bPVL5U',
        'asset_type': 'Power BI Report',
        'description': 'Baseball dataset visualization report for insights with Power BI.',
        'source': 'BYU Pathway Power BI'
    }
]

def load_skills():
    try:
        with open(SKILLS_FILE_PATH, 'r', encoding='utf-8') as fh:
            return json.load(fh)
    except FileNotFoundError:
        return []
    except Exception as exc:
        app.logger.error(f"Failed loading skills file: {exc}")
        return []


def save_skills(skills):
    os.makedirs(os.path.dirname(SKILLS_FILE_PATH), exist_ok=True)
    with open(SKILLS_FILE_PATH, 'w', encoding='utf-8') as fh:
        json.dump(skills, fh, indent=2)


def is_authorized_skills_api(api_key):
    if api_key and SKILLS_API_KEY and api_key == SKILLS_API_KEY:
        return True
    return is_local_access()


def load_json_file(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            return json.load(fh)
    except Exception:
        return default


def save_json_file(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(data, fh, indent=2)


def load_testimonials():
    return load_json_file(TESTIMONIALS_FILE_PATH, [])


def save_testimonials(testimonials):
    save_json_file(TESTIMONIALS_FILE_PATH, testimonials)


def load_testimonial_invites():
    return load_json_file(TESTIMONIAL_INVITES_FILE_PATH, [])


def save_testimonial_invites(invites):
    save_json_file(TESTIMONIAL_INVITES_FILE_PATH, invites)


BI_PROJECT_DETAILS = [
    {
        'slug': 'week-3-basic-sql-functions',
        'title': 'Week 3 - Basic SQL Functions',
        'tag': 'SQL Foundations',
        'summary': 'Built foundational SQL expressions and data transformations to prepare datasets for reporting and analysis.',
        'focus': [
            'SELECT and WHERE logic for filtered datasets.',
            'Column functions, aliases, and formatting.',
            'Grouping and aggregation for summary metrics.',
            'Preparing query output for BI visualization.'
        ],
        'attachments': [
            '3.3 Basic SQL Functions.docx',
            '3.5 Project 1 Baseball Dataset.docx'
        ],
        'image': 'images/bi_week3.svg',
        'asset_link': 'https://byupathwayworldwideprod-my.sharepoint.com/:u:/g/personal/smokhele_byupathway_edu/IQASaL0ZppeARLetMq_hFy8UAXJ0po2sh3A221swZpl_Rbg?e=bPVL5U',
        'asset_description': 'Baseball dataset query report and supporting SQL definitions.'
    },
    {
        'slug': 'week-4-common-table-expressions',
        'title': 'Week 4 - Common Table Expressions',
        'tag': 'Query Design',
        'summary': 'Developed modular SQL logic using CTEs to support reusable analysis and easier report validation.',
        'focus': [
            'Building reusable subqueries with CTEs.',
            'Combining data sources for comparative analysis.',
            'Applying logical steps in stages for clarity.',
            'Simplifying complex reporting queries.'
        ],
        'attachments': [
            '4.3 Common Table Expressions.docx',
            '4.4 Project 3 – Writing SQL Queries.docx'
        ],
        'image': 'images/bi_week4.svg',
        'asset_link': None,
        'asset_description': 'SQL design documentation and query refinement examples.'
    },
    {
        'slug': 'week-5-enhancing-queries',
        'title': 'Week 5 - Enhancing Queries with Intermediate SQL',
        'tag': 'Query Optimization',
        'summary': 'Refined SQL techniques using intermediate functions and query structure for stronger BI-ready datasets.',
        'focus': [
            'Using intermediate functions for data transformation.',
            'Applying conditional logic and calculated columns.',
            'Improving query readability and maintainability.',
            'Preparing transactional data for dashboard reporting.'
        ],
        'attachments': [
            '4.5 Enhancing Queries with Intermediate SQL.docx'
        ],
        'image': 'images/bi_week5.svg',
        'asset_link': None,
        'asset_description': 'Intermediate SQL concepts and data transformation examples.'
    },
    {
        'slug': 'week-6-advanced-sql-functions',
        'title': 'Week 6 - Advanced SQL Functions and BI Reporting',
        'tag': 'BI Reporting',
        'summary': 'Combined advanced SQL logic with report-focused data preparation for a BI-ready business analysis deliverable.',
        'focus': [
            'Advanced SQL functions for data modeling.',
            'Final report preparation and data validation.',
            'Generating business-ready output for dashboards.',
            'Documenting analysis findings for stakeholders.'
        ],
        'attachments': [
            '5.2 Sample Files - Advanced SQL Functions.docx',
            '5.3 Project 4 - Writing SQL Queries.docx'
        ],
        'image': 'images/bi_week6.svg',
        'asset_link': 'https://byupathwayworldwideprod-my.sharepoint.com/:u:/g/personal/smokhele_byupathway_edu/IQBSsq5Cvf14TrNuLMCxfiI3ASP8KEeca8sjKIOaO4B18lk?e=nVDlH3',
        'asset_description': 'Final BI reporting sources and sample Power BI files.'
    }
]

CLOUD_PROJECT_DETAILS = [
    {
        'slug': 'cloud-solution-proposal',
        'title': 'Cloud Solution Proposal',
        'tag': 'Cloud Architecture',
        'summary': 'A semester-long cloud infrastructure proposal focused on secure deployment, cost optimization, and operational efficiency.',
        'focus': [
            'Designing a secure hybrid cloud architecture.',
            'Implementing cloud governance and compliance controls.',
            'Optimizing infrastructure costs and service selection.',
            'Automating deployment and monitoring for reliability.'
        ],
        'attachments': [
            'CloudSolutionProposal_IT160_sMokhele.docx'
        ],
        'image': 'images/cloud_solution_proposal.svg',
        'asset_link': None,
        'asset_description': 'Cloud solution architecture proposal with cost and security recommendations.'
    }
]


def get_db_connection():
    if not DATABASE_URL or psycopg2 is None:
        return None
    try:
        return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    except Exception as e:
        app.logger.error(f"Database connect failed: {e}")
        return None

# If an extracted cloud project JSON exists, load and prefer it for the cloud page
try:
    CLOUD_JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'cloud_project.json')
    if os.path.exists(CLOUD_JSON_PATH):
        with open(CLOUD_JSON_PATH, 'r', encoding='utf-8') as _fh:
            _loaded = json.load(_fh)
            if isinstance(_loaded, dict):
                CLOUD_PROJECT_DETAILS = [_prepare_cloud_project(_loaded)]
            elif isinstance(_loaded, list):
                CLOUD_PROJECT_DETAILS = [_prepare_cloud_project(_p) for _p in _loaded]
except Exception as _err:
    app.logger.error(f"Failed to load extracted cloud project JSON: {_err}")


def init_bi_projects_table():
    conn = get_db_connection()
    if conn is None:
        return
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS bi_projects (
                        id SERIAL PRIMARY KEY,
                        title TEXT NOT NULL,
                        link TEXT NOT NULL,
                        asset_type TEXT,
                        description TEXT,
                        source TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                cur.execute("SELECT COUNT(*) AS count FROM bi_projects")
                row = cur.fetchone()
                if row and row['count'] == 0:
                    seed_projects = [
                        {
                            'title': 'Heritage Vault 20 Infrastructure Proposal',
                            'link': 'https://byupathwayworldwideprod-my.sharepoint.com/:p:/g/personal/smokhele_byupathway_edu/IQDiCok6HxO-S6u3aLUKq3gYAa84iZHDmip6oa_ke8r7h8Y?e=cfWDzx',
                            'asset_type': 'PowerPoint',
                            'description': 'Infrastructure proposal presentation for Heritage Vault 20.',
                            'source': 'BYU Pathway Power BI / Infrastructure'
                        },
                        {
                            'title': 'Heritage Vault 20 Infrastructure Proposal Video',
                            'link': 'https://byupathwayworldwideprod-my.sharepoint.com/:v:/g/personal/smokhele_byupathway_edu/IQD4mI2UJxSpQazfzF-4zIwGAZ4LdeLHBDjQcFV5q5YaTtM?e=ejk9zd',
                            'asset_type': 'Video',
                            'description': 'Presentation video for the Heritage Vault 20 infrastructure proposal.',
                            'source': 'BYU Pathway Video Submission'
                        },
                        {
                            'title': 'Sample Files - Present Analysis in PowerBI',
                            'link': 'https://byupathwayworldwideprod-my.sharepoint.com/:u:/g/personal/smokhele_byupathway_edu/IQBSsq5Cvf14TrNuLMCxfiI3ASP8KEeca8sjKIOaO4B18lk?e=nVDlH3',
                            'asset_type': 'Power BI Report',
                            'description': 'Sample Power BI files for presenting analysis.',
                            'source': 'BYU Pathway Power BI'
                        },
                        {
                            'title': 'Project 4 - Presenting Analysis',
                            'link': 'https://byupathwayworldwideprod-my.sharepoint.com/:u:/g/personal/smokhele_byupathway_edu/IQC4kFr-vFTERZ6xHnQYK_iUAZm9GpwjTRsmKjeK5NDWtb0?e=9YDbK1',
                            'asset_type': 'Power BI Report',
                            'description': 'Project 4 Power BI report for presenting analysis results.',
                            'source': 'BYU Pathway Power BI'
                        },
                        {
                            'title': 'Project 1 - Baseball Dataset, Part 6',
                            'link': 'https://byupathwayworldwideprod-my.sharepoint.com/:u:/g/personal/smokhele_byupathway_edu/IQASaL0ZppeARLetMq_hFy8UAXJ0po2sh3A221swZpl_Rbg?e=bPVL5U',
                            'asset_type': 'Power BI Report',
                            'description': 'Baseball dataset visualization report for insights with Power BI.',
                            'source': 'BYU Pathway Power BI'
                        }
                    ]
                    for project in seed_projects:
                        cur.execute(
                            "INSERT INTO bi_projects (title, link, asset_type, description, source) VALUES (%s, %s, %s, %s, %s)",
                            (project['title'], project['link'], project['asset_type'], project['description'], project['source'])
                        )
    except Exception as e:
        app.logger.error(f"Database initialization failed: {e}")
    finally:
        conn.close()


def fetch_bi_projects():
    conn = get_db_connection()
    if conn is None:
        return STATIC_BI_PROJECTS
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, title, link, asset_type, description, source FROM bi_projects ORDER BY id")
                projects = cur.fetchall()
                if projects:
                    return projects
                return STATIC_BI_PROJECTS
    except Exception as e:
        app.logger.error(f"Database query failed: {e}")
        return STATIC_BI_PROJECTS
    finally:
        conn.close()

# -------- COURSE INFORMATION --------
COURSES = {
    "pc-hardware": {
        "title": "PC Hardware Technician",
        "certificate": "Technical Support Engineer",
        "description": "Learn the fundamentals of PC hardware, including components, assembly, troubleshooting, and maintenance.",
        "url": "https://www.byupathway.edu",
        "local_folder": "IT102 PC Hardware Technician",
        "onedrive_link": "https://byupathwayworldwideprod-my.sharepoint.com/:f:/g/personal/smokhele_byupathway_edu/IgBJ4I2SAS8mTKvJkgPxsLSxAWQIt5Dcvj7yeDLKbM806jw?e=BxTziD"
    },
    "networking-fundamentals": {
        "title": "Networking Fundamentals",
        "certificate": "Technical Support Engineer",
        "description": "Introduction to networking concepts, protocols, and network infrastructure basics.",
        "url": "https://www.byupathway.edu",
        "local_folder": "IT255 Networking Fundamentals",
        "onedrive_link": ""  # Add your OneDrive share link here
    },
    "cloud-server": {
        "title": "Cloud Server Administration",
        "certificate": "Technical Support Engineer",
        "description": "Learn to administer cloud-based servers and cloud infrastructure platforms.",
        "url": "https://www.byupathway.edu",
        "local_folder": "IT235 - Cloud server administration",
        "onedrive_link": ""  # Add your OneDrive share link here
    },
    "intro-it": {
        "title": "Introduction to Information Technology",
        "certificate": "Technical Support Engineer",
        "description": "Foundational concepts in Information Technology and the IT industry.",
        "url": "https://www.byupathway.edu",
        "local_folder": "IT125 Intro to Information Technology",
        "onedrive_link": "https://byupathwayworldwideprod-my.sharepoint.com/:f:/g/personal/smokhele_byupathway_edu/IgBvS-sSsknIT7HYo82_wUM3AWQeBr-IgWkN6aFSLJvAgnQ?e=HQBiMx"
    },
    "applied-programming": {
        "title": "Foundations of Applied Programming",
        "certificate": "Technical Support Engineer",
        "description": "Introduction to programming fundamentals and software development principles.",
        "url": "https://www.byupathway.edu",
        "local_folder": "CS104 Foundations of Applied Programming",
        "onedrive_link": "https://byupathwayworldwideprod-my.sharepoint.com/:f:/g/personal/smokhele_byupathway_edu/IgCKPC7nHTdzR7HjE7DKILvjAaqeCiO75vZojPBQkm2qTUI?e=kuNrwn"
    },
    "database-design": {
        "title": "Database Design and Analysis",
        "certificate": "IT Professional",
        "description": "Learn database design principles, SQL, and data management.",
        "url": "https://www.byupathway.edu",
        "local_folder": "IT 143 Database Design and Analysis",
        "onedrive_link": "https://byupathwayworldwideprod-my.sharepoint.com/:f:/g/personal/smokhele_byupathway_edu/IgCswwNvuCkzTKtS9dd3at0eAbvqlJxYWSsV0gXTPo37jLw?e=Q9sT0j"
    },
    "linux-fundamentals": {
        "title": "Linux Fundamentals",
        "certificate": "IT Professional",
        "description": "Master Linux operating system basics, commands, and system administration.",
        "url": "https://www.byupathway.edu",
        "local_folder": "IT210 Linux Fundamentals",
        "onedrive_link": "https://byupathwayworldwideprod-my.sharepoint.com/:f:/g/personal/smokhele_byupathway_edu/IgDO7_2OGwHdT4AE1LKJwsZKAXfPNe7Iia1X1O6aF3LaWK8?e=LaidyB"
    },
    "cloud-computing": {
        "title": "Cloud Computing Essentials",
        "certificate": "IT Professional",
        "description": "Core concepts of cloud computing, deployment models, and cloud services.",
        "url": "https://www.byupathway.edu",
        "local_folder": "IT 160 Cloud Computing Essentials",
        "onedrive_link": "https://byupathwayworldwideprod-my.sharepoint.com/:f:/g/personal/smokhele_byupathway_edu/IgBdYk-rqyVWRoxBxn3QkSe8ASeqIPGKTn7aunzxw6IRobw?e=yvaLHw"
    },
    "network-config": {
        "title": "Network Configuration & Design",
        "certificate": "IT Professional",
        "description": "Network design, configuration, and best practices for enterprise networks.",
        "url": "https://www.byupathway.edu",
        "local_folder": "IT 350 Network Configuration & Design",
        "onedrive_link": "https://byupathwayworldwideprod-my.sharepoint.com/:f:/g/personal/smokhele_byupathway_edu/IgDe-H6FSybYRY7ZSASunPGnAV-HzZ1AA2RfXrN83thrJcg?e=hPZbw7"
    },
    "cybersecurity-foundations": {
        "title": "Cybersecurity Foundations",
        "certificate": "IT Professional",
        "description": "Introduction to cybersecurity principles, threats, and defense mechanisms.",
        "url": "https://www.byupathway.edu",
        "local_folder": "IT 312 Cybersecurity",
        "onedrive_link": "https://byupathwayworldwideprod-my.sharepoint.com/:f:/g/personal/smokhele_byupathway_edu/IgDuJxwBOzdVQLmc7F2ik_8qAWfFsr_rPVC-jzyRsPTMBQc?e=OsI0Ff"
    },
    "business-intelligence": {
        "title": "Business Intelligence Systems",
        "certificate": "System Administration",
        "description": "Learn to work with BI tools, data analytics, and business intelligence platforms.",
        "url": "https://www.byupathway.edu",
        "local_folder": "IT 340 Business Intelligence Systems",
        "onedrive_link": "https://byupathwayworldwideprod-my.sharepoint.com/:f:/g/personal/smokhele_byupathway_edu/IgBx73_z5374T4NCwCjIfDUbAV1AqkiURxqSgcuv2UVjkos?e=xmr6me"
    },
    "advanced-linux": {
        "title": "Advanced Linux",
        "certificate": "System Administration",
        "description": "Advanced Linux system administration, scripting, and performance tuning.",
        "url": "https://www.byupathway.edu",
        "local_folder": "IT 370 Advanced Linux",
        "onedrive_link": "https://byupathwayworldwideprod-my.sharepoint.com/:f:/g/personal/smokhele_byupathway_edu/IgBbUVpk1e3tRYhHHvJlM3C1AUYMZLzHptx1ATb5wmqtqeY?e=3IB9pF"
    },
    "networking-fundamentals": {
        "title": "Networking Fundamentals",
        "certificate": "Information Technology",
        "description": "Networking fundamentals, protocols, and infrastructure design.",
        "url": "https://www.byupathway.edu",
        "onedrive_link": "https://byupathwayworldwideprod-my.sharepoint.com/:f:/g/personal/smokhele_byupathway_edu/IgCcpZTs2DfEQq-U3GqvZQghAReSYi_TGOtGwIr-AzdsKSI?e=7xvZ6Z"
    },
    "scripting-security": {
        "title": "Scripting for Security Operations",
        "certificate": "System Administration",
        "description": "Learn scripting languages for security automation and operations.",
        "url": "https://www.byupathway.edu"
    },
    "azure-tech": {
        "title": "Azure Technologies",
        "certificate": "System Administration",
        "description": "Microsoft Azure cloud platform services and administration.",
        "url": "https://www.byupathway.edu"
    },
    "aws-practitioner": {
        "title": "AWS Cloud Practitioner",
        "certificate": "System Administration",
        "description": "Amazon Web Services fundamentals and cloud best practices.",
        "url": "https://www.byupathway.edu"
    }
}

CERTIFICATE_TRACKS = [
    {
        "id": "technical-support-engineer",
        "title": "Technical Support Engineer",
        "summary": "Practical IT support skills for hardware, networking, desktop support, and programming fundamentals.",
        "status": "Completed",
        "detail": "All 5 courses completed",
        "courses": [
            {"id": "pc-hardware", "note": "Completed", "grade": "A"},
            {"id": "networking-fundamentals", "note": "Completed", "grade": "C"},
            {"id": "cloud-server", "note": "Completed", "grade": "A"},
            {"id": "intro-it", "note": "Completed", "grade": "A"},
            {"id": "applied-programming", "note": "Completed", "grade": "A"}
        ]
    },
    {
        "id": "it-professional",
        "title": "IT Professional",
        "summary": "Advanced IT skills in databases, Linux, cloud, networking, and cybersecurity.",
        "status": "Completed",
        "detail": "All 5 courses complete — certificate pending upload",
        "courses": [
            {"id": "database-design", "note": "Completed", "grade": "B+"},
            {"id": "linux-fundamentals", "note": "Completed", "grade": "B+"},
            {"id": "cloud-computing", "note": "Completed", "grade": "B+"},
            {"id": "network-config", "note": "Completed", "grade": "A"},
            {"id": "cybersecurity-foundations", "note": "Completed", "grade": "A"}
        ]
    },
    {
        "id": "system-administration",
        "title": "System Administration",
        "summary": "Foundational server and network administration training for entry-level sysadmin roles.",
        "status": "In Progress",
        "detail": "2 completed, 3 in progress",
        "courses": [
            {"id": "business-intelligence", "note": "Completed", "grade": "A"},
            {"id": "advanced-linux", "note": "Completed", "grade": "A"},
            {"id": "scripting-security", "note": "In Progress", "grade": ""},
            {"id": "azure-tech", "note": "In Progress", "grade": ""},
            {"id": "aws-practitioner", "note": "In Progress", "grade": ""}
        ]
    }
]

# ---------------- HOME ----------------
@app.route('/')
def home():
    return render_template('index.html')

# ---------------- STATIC PAGES ----------------
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
    return render_template('cloud.html', projects=CLOUD_PROJECT_DETAILS)

@app.route('/cloud/attachment/<filename>')
def cloud_attachment(filename):
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(data_dir, safe_filename)
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        abort(404)
    return send_file(file_path, as_attachment=True, download_name=safe_filename)

@app.route('/cloud/<slug>')
def cloud_project_detail(slug):
    project = next((item for item in CLOUD_PROJECT_DETAILS if item['slug'] == slug), None)
    if project is None:
        abort(404)
    return render_template('cloud_project_detail.html', project=project)


@app.route('/cloud/solution-proposal')
def cloud_solution_proposal():
    return redirect(url_for('cloud_project_detail', slug='cloud-solution-proposal'))


@app.route('/cybersecurity')
def cybersecurity():
    return render_template('cybersecurity.html')

@app.route('/cybersecurity/hids-siem')
def hids_siem():
    project_images = [
        f"project10_image_{i}.png" for i in range(1, 20)
    ]
    return render_template('hids_siem.html', project_images=project_images)

@app.route('/cybersecurity/anatomy-of-a-hack')
def anatomy_of_a_hack():
    return render_template('anatomy_of_a_hack.html')

@app.route('/cybersecurity/metasploit-lab')
def metasploit_lab():
    return render_template('metasploit_lab.html')

@app.route('/cybersecurity/dashboard')
def cybersecurity_dashboard():
    return render_template('cybersecurity_dashboard.html')

def find_certificate_file(certificate):
    static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    candidates = [
        f"{certificate['id']}.pdf",
        f"{certificate['title'].replace(' ', '_')}.pdf",
        f"{certificate['title'].replace(' ', '_').replace('-', '_')}.pdf",
        f"{certificate['title'].replace(' ', '_').replace('&', 'and')}.pdf"
    ]
    for candidate in candidates:
        candidate_path = os.path.join(static_folder, candidate)
        if os.path.exists(candidate_path):
            return url_for('static', filename=candidate)
    return None


@app.route('/certifications')
def certifications():
    certificates = []
    for cert in CERTIFICATE_TRACKS:
        courses = []
        completed = 0
        for item in cert['courses']:
            course = COURSES.get(item['id'], {})
            title = course.get('title', item['id'].replace('-', ' ').replace('_', ' ').title())
            url = url_for('course_detail', course_id=item['id']) if item['id'] in COURSES else None
            note = item['note']
            if note == 'Completed':
                completed += 1
            courses.append({
                'id': item['id'],
                'title': title,
                'url': url,
                'note': note,
                'grade': item.get('grade', '')
            })

        certificates.append({
            'id': cert['id'],
            'title': cert['title'],
            'summary': cert['summary'],
            'status': cert['status'],
            'detail': cert['detail'],
            'courses': courses,
            'completed': completed,
            'total': len(courses),
            'certificate_file': find_certificate_file(cert)
        })

    return render_template('certifications.html', certificates=certificates)

@app.route('/skills')
def skills():
    skills = load_skills()
    return render_template('skills.html', skills=skills)


@app.route('/testimonials')
def testimonials():
    testimonial_items = sorted(load_testimonials(), key=lambda item: item.get('created_at', ''), reverse=True)
    return render_template('testimonials.html', testimonials=testimonial_items)


@app.route('/testimonials/manage', methods=['GET', 'POST'])
def manage_testimonials():
    if not is_local_access():
        abort(403)

    invites = sorted(load_testimonial_invites(), key=lambda item: item.get('created_at', ''), reverse=True)

    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        email = (request.form.get('email') or '').strip().lower()
        phone = (request.form.get('phone') or '').strip()
        relationship = (request.form.get('relationship') or '').strip()
        note = (request.form.get('note') or '').strip()

        if not name or (not email and not phone):
            return render_template('testimonial_manage.html', invites=invites, error='Please enter a name and at least one contact detail.', new_invite=None)

        token = secrets.token_urlsafe(10)
        invite = {
            'token': token,
            'name': name,
            'email': email,
            'phone': phone,
            'relationship': relationship,
            'note': note,
            'created_at': datetime.utcnow().isoformat(),
            'used_at': None
        }
        invites.insert(0, invite)
        save_testimonial_invites(invites)

        submit_url = url_for('submit_testimonial', token=token, _external=True)
        email_sent = False
        email_message = None
        if email:
            email_sent, email_message = send_testimonial_invite_email(email, name, submit_url)

        return render_template(
            'testimonial_manage.html',
            invites=invites,
            success=f'Invitation created for {name}.',
            submit_url=submit_url,
            new_invite=invite,
            email_sent=email_sent,
            email_message=email_message
        )

    return render_template('testimonial_manage.html', invites=invites, error=None, success=None, submit_url=None, new_invite=None)


@app.route('/testimonials/submit', methods=['GET', 'POST'])
def submit_testimonial():
    token = request.args.get('token') or request.form.get('token') or ''
    invites = load_testimonial_invites()
    invite = next((item for item in invites if item.get('token') == token), None)

    if not invite:
        return render_template('testimonial_submit.html', invite=None, error='This invitation link is not valid.', success=None)

    if invite.get('used_at'):
        return render_template('testimonial_submit.html', invite=invite, error='This invitation has already been used.', success=None)

    if request.method == 'POST':
        submitted_email = (request.form.get('email') or '').strip().lower()
        submitted_phone = (request.form.get('phone') or '').strip()
        quote = (request.form.get('quote') or '').strip()
        company = (request.form.get('company') or '').strip()
        role = (request.form.get('role') or '').strip()

        matches_email = bool(invite.get('email')) and submitted_email == invite.get('email')
        matches_phone = bool(invite.get('phone')) and submitted_phone == invite.get('phone')
        if not (matches_email or matches_phone):
            return render_template('testimonial_submit.html', invite=invite, error='Please enter the email or phone number that was used in your invitation.', success=None)

        if not quote:
            return render_template('testimonial_submit.html', invite=invite, error='Please add a testimonial before submitting.', success=None)

        testimonials = load_testimonials()
        existing = next((item for item in testimonials if item.get('invite_token') == token), None)
        now = datetime.utcnow().isoformat()
        testimonial_entry = {
            'invite_token': token,
            'name': invite.get('name'),
            'email': invite.get('email'),
            'phone': invite.get('phone'),
            'relationship': invite.get('relationship'),
            'company': company,
            'role': role,
            'quote': quote,
            'created_at': existing.get('created_at', now) if existing else now,
            'updated_at': now
        }

        if existing:
            existing.update(testimonial_entry)
        else:
            testimonials.append(testimonial_entry)

        save_testimonials(testimonials)

        invite['used_at'] = now
        save_testimonial_invites(invites)

        return render_template('testimonial_submit.html', invite=invite, success='Thank you. Your testimonial has been saved.', error=None)

    return render_template('testimonial_submit.html', invite=invite, error=None, success=None)


@app.route('/api/skills', methods=['GET', 'POST'])
def api_skills():
    if request.method == 'GET':
        return jsonify({'skills': load_skills()})

    api_key = request.headers.get('X-Api-Key') or request.args.get('api_key')
    if not is_authorized_skills_api(api_key):
        return jsonify({'error': 'Unauthorized'}), 403

    payload = request.get_json(silent=True) or {}
    category = payload.get('category')
    name = payload.get('name')
    description = payload.get('description', '')
    if not category or not name:
        return jsonify({'error': 'category and name are required'}), 400

    skills = load_skills()
    section = next((item for item in skills if item.get('title', '').lower() == category.lower()), None)
    if section is None:
        section = {'title': category, 'description': '', 'items': []}
        skills.append(section)

    normalized_name = name.strip()
    if not any(item.get('name', '').lower() == normalized_name.lower() for item in section['items']):
        section['items'].append({'name': normalized_name, 'description': description.strip()})
        save_skills(skills)

    return jsonify({'skills': skills, 'added': normalized_name})


@app.route('/timeline')
def timeline():
    return render_template('timeline.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# -------- FILE VIEWING API (VIEW-ONLY) --------
@app.route('/api/file-content', methods=['POST'])
def get_file_content():
    """Serve file content for viewing (view-only, no edit/delete)"""
    try:
        file_path = request.json.get('path')
        
        if not file_path:
            return jsonify({'error': 'No file path provided'}), 400
        
        # Security check: verify path is within allowed directories
        if not is_safe_path(file_path, ALLOWED_PATHS):
            return jsonify({'error': 'Access denied to this file'}), 403
        
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Get file size to decide how to handle it
        file_size = os.path.getsize(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        
        # For text files, return content
        text_extensions = {'.txt', '.py', '.sh', '.sql', '.js', '.html', '.css', '.json', '.csv', '.xml', '.md'}
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext in text_extensions or (mime_type and mime_type.startswith('text/')):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    return jsonify({
                        'success': True,
                        'content': content,
                        'filename': os.path.basename(file_path),
                        'type': 'text',
                        'file_ext': file_ext
                    })
            except Exception as e:
                return jsonify({'error': f'Could not read file: {str(e)}'}), 500
        
        # For binary files, return file info and download link
        else:
            return jsonify({
                'success': True,
                'filename': os.path.basename(file_path),
                'type': 'binary',
                'file_ext': file_ext,
                'size': file_size,
                'mime_type': mime_type or 'application/octet-stream',
                'message': f'This is a binary file. Click the download button to view/save it.'
            })
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

# -------- FILE DOWNLOAD API (VIEW-ONLY) --------
@app.route('/api/file-download', methods=['POST'])
def download_file():
    """Download file for viewing (view-only)"""
    try:
        file_path = request.json.get('path')
        
        if not file_path:
            return jsonify({'error': 'No file path provided'}), 400
        
        # Security check
        if not is_safe_path(file_path, ALLOWED_PATHS):
            return jsonify({'error': 'Access denied to this file'}), 403
        
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(file_path, as_attachment=True, download_name=os.path.basename(file_path))
    
    except Exception as e:
        return jsonify({'error': f'Download error: {str(e)}'}), 500

# -------- COURSE DETAILS --------
@app.route('/course/<course_id>')
def course_detail(course_id):
    course = COURSES.get(course_id)
    if not course:
        return "Course not found", 404
    
    # Check access type and get course materials info
    is_local = is_local_access()
    course_materials = None
    
    if 'local_folder' in course or 'onedrive_link' in course:
        if is_local and 'local_folder' in course:
            # Local access - show file path from OneDrive
            course_folder = course.get('local_folder')
            local_path = os.path.join(ONEDRIVE_BASE_PATH, course_folder)
            if os.path.exists(local_path):
                course_materials = {
                    'type': 'local',
                    'path': local_path,
                    'display': course_folder
                }
        elif 'onedrive_link' in course and course.get('onedrive_link'):
            # Remote access - show OneDrive link
            course_materials = {
                'type': 'cloud',
                'url': course.get('onedrive_link'),
                'display': course.get('local_folder', course.get('title'))
            }
    
    return render_template('course_detail.html', course_id=course_id, course=course, course_materials=course_materials)

# ---------------- PROJECTS (DYNAMIC) ----------------
@app.route('/projects')
def projects():

    courses = []
    source_roots = [
        r"F:\\BYU",
        r"C:\\Users\\User\\OneDrive - BYU-Pathway Worldwide\\Documents"
    ]
    one_drive_course_names = [
        "CS104 Foundations of Applied Programming",
        "IT102 PC Hardware Technician",
        "IT125 Intro to Information Technology",
        "IT210 Linux Fundamentals",
        "IT235 - Cloud server administration",
        "IT255 Networking Fundamentals"
    ]

    def collect_course_path(course_name, root_path):
        course_path = os.path.join(root_path, course_name)
        if os.path.isdir(course_path):
            return course_path
        return None

    def collect_files_from_folder(folder_path):
        files = []
        for file in sorted(os.listdir(folder_path)):
            if file.startswith('.'):
                continue
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                file_type = file.split('.')[-1].lower() if '.' in file else "other"
                files.append({
                    "name": file,
                    "type": file_type,
                    "path": file_path
                
                })
        return files

    def collect_weeks(course_path):
        weeks = []
        root_files = []
        for entry in sorted(os.listdir(course_path)):
            entry_path = os.path.join(course_path, entry)
            if entry.startswith('.'):
                continue
            if os.path.isdir(entry_path):
                week_files = collect_files_from_folder(entry_path)
                weeks.append({
                    "week": entry,
                    "files": week_files
                })
            elif os.path.isfile(entry_path):
                root_files.append({
                    "name": entry,
                    "type": entry.split('.')[-1].lower() if '.' in entry else "other"
                })

        if root_files:
            weeks.insert(0, {
                "week": "Course Files",
                "files": root_files
            })

        return weeks

    # First try the BYU shared folder, then the identified OneDrive course folders.
    for root_path in source_roots:
        if not os.path.exists(root_path):
            continue

        if root_path.endswith("Documents"):
            for course_name in one_drive_course_names:
                course_path = collect_course_path(course_name, root_path)
                if course_path:
                    weeks = collect_weeks(course_path)
                    if weeks:
                        courses.append({
                            "course": course_name,
                            "weeks": weeks
                        })
        else:
            for course_name in sorted(os.listdir(root_path)):
                course_path = os.path.join(root_path, course_name)
                if os.path.isdir(course_path):
                    weeks = collect_weeks(course_path)
                    courses.append({
                        "course": course_name,
                        "weeks": weeks
                    })

    recordings_root = r"C:\Users\User\OneDrive - BYU-Pathway Worldwide\Recordings"
    recordings_by_course = {}
    
    if os.path.exists(recordings_root) and os.path.isdir(recordings_root):
        for file in sorted(os.listdir(recordings_root)):
            if file.startswith('.'):
                continue
            file_path = os.path.join(recordings_root, file)
            if os.path.isfile(file_path):
                course_name = "Other Projects"
                
                file_lower = file.lower()
                if 'it160' in file_lower or 'csp_it160' in file_lower or 'cloud' in file_lower:
                    course_name = "IT160 - Cloud Solution Proposal"
                elif 'it255' in file_lower or 'network' in file_lower:
                    course_name = "IT255 Networking Fundamentals"
                elif 'it210' in file_lower or 'linux' in file_lower:
                    course_name = "IT210 Linux Fundamentals"
                elif 'it235' in file_lower or 'cloud server' in file_lower:
                    course_name = "IT235 - Cloud server administration"
                elif 'it125' in file_lower or 'intro' in file_lower or 'information technology' in file_lower:
                    course_name = "IT125 Intro to Information Technology"
                elif 'it102' in file_lower or 'hardware' in file_lower:
                    course_name = "IT102 PC Hardware Technician"
                elif 'cs104' in file_lower or 'applied programming' in file_lower:
                    course_name = "CS104 Foundations of Applied Programming"
                elif 'function' in file_lower or 'trigger' in file_lower:
                    course_name = "Database - Functions and Triggers"
                
                if course_name not in recordings_by_course:
                    recordings_by_course[course_name] = []
                
                recordings_by_course[course_name].append({
                    "name": file,
                    "url": Path(file_path).as_uri(),
                    "type": file.split('.')[-1].lower() if '.' in file else "other"
                })

    # Generate project links from COURSES with onedrive_link
    project_links = []
    for course_id, course in COURSES.items():
        if course.get('onedrive_link'):
            project_links.append({
                "title": course.get('title'),
                "certificate": course.get('certificate'),
                "description": course.get('description'),
                "url": course.get('onedrive_link'),
                "display": course.get('local_folder', course.get('title'))
            })

    # Add OneDrive recordings link as a top-level recordings entry
    if RECORDINGS_ONEDRIVE_LINK:
        recordings_by_course.setdefault('Project Recordings', [])
        # only add once
        if not any(r.get('url') == RECORDINGS_ONEDRIVE_LINK for r in recordings_by_course['Project Recordings']):
            recordings_by_course['Project Recordings'].insert(0, {
                'name': 'All Recordings (OneDrive)',
                'url': RECORDINGS_ONEDRIVE_LINK,
                'type': 'folder'
            })

        # Also map the recordings link under each course title for discoverability
        for course_id, course in COURSES.items():
            course_title = course.get('title')
            if not course_title:
                continue
            recordings = recordings_by_course.get(course_title, [])
            if not any(r.get('url') == RECORDINGS_ONEDRIVE_LINK for r in recordings):
                recordings.append({
                    'name': 'Recordings (OneDrive)',
                    'url': RECORDINGS_ONEDRIVE_LINK,
                    'type': 'folder'
                })
                recordings_by_course[course_title] = recordings

    return render_template("projects.html", courses=courses, recordings_by_course=recordings_by_course, project_links=project_links)


@app.route('/bi-projects')
def bi_projects():
    init_bi_projects_table()
    projects = fetch_bi_projects()
    return render_template('bi_projects.html', projects=projects, db_enabled=DATABASE_URL is not None, detail_projects=BI_PROJECT_DETAILS)


@app.route('/bi-projects/<slug>')
def bi_project_detail(slug):
    project = next((item for item in BI_PROJECT_DETAILS if item['slug'] == slug), None)
    if project is None:
        abort(404)
    return render_template('bi_project_detail.html', project=project)


@app.route('/api/bi-projects', methods=['GET'])
def api_bi_projects():
    projects = fetch_bi_projects()
    return jsonify({'projects': projects, 'db_enabled': DATABASE_URL is not None})


# ---------------- PYTHON PROJECTS (LOCAL + OneDrive links) ----------------
@app.route('/python-projects')
def python_projects():
    # local folder inside the repo where the user will place CS104 files
    repo_root = os.path.dirname(os.path.abspath(__file__))
    local_folder = os.path.join(repo_root, 'python_programs')
    metadata_path = os.path.join(local_folder, 'metadata.json')

    metadata = {}
    if os.path.exists(metadata_path) and os.path.isfile(metadata_path):
        try:
            with open(metadata_path, 'r', encoding='utf-8') as meta_file:
                metadata = json.load(meta_file)
        except Exception:
            metadata = {}

    files = []
    if os.path.exists(local_folder) and os.path.isdir(local_folder):
        for fname in sorted(os.listdir(local_folder)):
            if fname.startswith('.'):
                continue
            fpath = os.path.join(local_folder, fname)
            if os.path.isfile(fpath) and fname.lower().endswith('.py'):
                clean_name = os.path.splitext(fname)[0]
                clean_display = clean_name.replace('_', ' ').replace('-', ' ').title()
                files.append({
                    'name': fname,
                    'display_name': clean_display,
                    'description': metadata.get(fname, ''),
                    'path': fpath
                })

    # OneDrive links provided (hybrid approach) - user-supplied folders
    onedrive_links = [
        { 'title': '1-4 Integrated Development Environments', 'url': 'https://byupathwayworldwideprod-my.sharepoint.com/:f:/g/personal/smokhele_byupathway_edu/IgDSK9tZlggTTqaNAdWHXtj4AQ4KBkTr7eqEjgWQpskaVCQ?e=YkFQDj/'},
        { 'title': '2-4 First Programs', 'url': 'https://byupathwayworldwideprod-my.sharepoint.com/:f:/g/personal/smokhele_byupathway_edu/IgBg2FXuaH4-SI76VGHmq0b9AVx389O7rhQDvBndaxwwYVQ?e=UxKf2F/'},
        { 'title': '2-5 Putting Python to Work', 'url': 'https://byupathwayworldwideprod-my.sharepoint.com/:f:/g/personal/smokhele_byupathway_edu/IgDXas3A8zvLTZNEX6ZBf4z9Ab9snDBUqu3gmJY6TfkDW6Q?e=Lnd1VM/'},
        { 'title': '2-7 Flow of Information', 'url': 'https://byupathwayworldwideprod-my.sharepoint.com/:f:/g/personal/smokhele_byupathway_edu/IgBU5mKW92dgQangyems_RtpAdRghbO-mJg45b5sGhD1H3k?e=TqVGrN/'},
        { 'title': '3-4 Tilling Soil', 'url': 'https://byupathwayworldwideprod-my.sharepoint.com/:f:/g/personal/smokhele_byupathway_edu/IgDwbuiVz-E2QIZE5bo8cmv6AbYGUzAKzSGk-CcFNkcMdpw?e=Vm5sfS/'},
        { 'title': '3-5 Limiting Access', 'url': 'https://byupathwayworldwideprod-my.sharepoint.com/:f:/g/personal/smokhele_byupathway_edu/IgBRUCvbi5VlRIfRIs5wbA5_AaQLrwKrAMhcfU6zCWvekGY?e=JKlgYe/'},
        { 'title': '4-4 The Nature of Numbers', 'url': 'https://byupathwayworldwideprod-my.sharepoint.com/:f:/g/personal/smokhele_byupathway_edu/IgCZWj4ih0CySJIRl7Z15zTeATzmllPwc9vDqkRo6HClDeU?e=9KRS12/'},
        { 'title': '4-6 Iterating Through a JSON Object', 'url': 'https://byupathwayworldwideprod-my.sharepoint.com/:f:/g/personal/smokhele_byupathway_edu/IgDZ3V-v5jWyS6An_eQTxfgvASfMavn8KiM1twih8-4HjCk?e=5BteU1/'},
        { 'title': '4-7 Raspberry Pi Python Execution', 'url': 'https://byupathwayworldwideprod-my.sharepoint.com/:f:/g/personal/smokhele_byupathway_edu/IgCa03DsgMThSK5p-t62pKDoAQRymuhO8T_6uZ6xpCAqHqE?e=e4yl1b/'},
        { 'title': '5-3 Tracking Finances', 'url': 'https://byupathwayworldwideprod-my.sharepoint.com/:f:/g/personal/smokhele_byupathway_edu/IgBta1uoA823S6-ASaiN-XtnAVGDz3rbtlkILzyjrfwktP0?e=gqFLZo/'},
        { 'title': '5-4 Career Connections', 'url': 'https://byupathwayworldwideprod-my.sharepoint.com/:f:/g/personal/smokhele_byupathway_edu/IgDsAgUwH9jkRoVz8UNEJjfJAWJ3x_GYWbS9OXD_Z-aNSuY?e=26uOsQ/'},
        { 'title': '5-7 Security Device Monitoring', 'url': 'https://byupathwayworldwideprod-my.sharepoint.com/personal/smokhele_byupathway_edu/Documents/'},
        { 'title': '6-4 Creating and Filling a Database', 'url': 'https://byupathwayworldwideprod-my.sharepoint.com/personal/smokhele_byupathway_edu/Documents/'},
        { 'title': '6-8 Connecting with the WhatsApp API', 'url': 'https://byupathwayworldwideprod-my.sharepoint.com/personal/smokhele_byupathway_edu/Documents/'},
        { 'title': '7-2 Flask Routing Quiz', 'url': 'https://byupathwayworldwideprod-my.sharepoint.com/personal/smokhele_byupathway_edu/Documents/'},
        { 'title': '7-3 Reading and Revising an API', 'url': 'https://byupathwayworldwideprod-my.sharepoint.com/personal/smokhele_byupathway_edu/Documents/'}
    ]

    db_configured = DATABASE_URL is not None
    return render_template('python_projects.html', files=files, onedrive_links=onedrive_links, db_enabled=db_configured)


@app.route('/api/python-projects/files', methods=['GET'])
def python_projects_files():
    repo_root = os.path.dirname(os.path.abspath(__file__))
    local_folder = os.path.join(repo_root, 'python_programs')
    metadata_path = os.path.join(local_folder, 'metadata.json')

    metadata = {}
    if os.path.exists(metadata_path) and os.path.isfile(metadata_path):
        try:
            with open(metadata_path, 'r', encoding='utf-8') as meta_file:
                metadata = json.load(meta_file)
        except Exception:
            metadata = {}

    files = []
    if os.path.exists(local_folder) and os.path.isdir(local_folder):
        for fname in sorted(os.listdir(local_folder)):
            if fname.startswith('.'):
                continue
            fpath = os.path.join(local_folder, fname)
            if os.path.isfile(fpath) and fname.lower().endswith('.py'):
                clean_name = os.path.splitext(fname)[0]
                clean_display = clean_name.replace('_', ' ').replace('-', ' ').title()
                files.append({
                    'name': fname,
                    'display_name': clean_display,
                    'description': metadata.get(fname, ''),
                })

    return jsonify({'files': files})


@app.route('/api/run-python', methods=['POST'])
def run_python():
    data = request.json or {}
    filename = data.get('filename')
    if not filename:
        return jsonify({'error': 'No filename provided'}), 400

    repo_root = os.path.dirname(os.path.abspath(__file__))
    local_folder = os.path.join(repo_root, 'python_programs')
    target_path = os.path.join(local_folder, os.path.basename(filename))

    # Security: ensure the path is inside local_folder
    if not is_safe_path(target_path, [local_folder]):
        return jsonify({'error': 'Access denied'}), 403

    if not os.path.exists(target_path) or not os.path.isfile(target_path):
        return jsonify({'error': 'File not found'}), 404

    # Run with the same Python interpreter used by the server
    cmd = [sys.executable, target_path]

    try:
        # Ensure subprocess inherits DATABASE_URL so scripts run against Postgres when configured
        env = os.environ.copy()
        if DATABASE_URL:
            env['DATABASE_URL'] = DATABASE_URL

        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=8, cwd=local_folder, text=True, env=env)
        stdout = proc.stdout[:10000]
        stderr = proc.stderr[:10000]
        return jsonify({'success': True, 'stdout': stdout, 'stderr': stderr, 'returncode': proc.returncode})
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Execution timed out'}), 504
    except Exception as e:
        return jsonify({'error': f'Execution error: {str(e)}'}), 500


# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)


