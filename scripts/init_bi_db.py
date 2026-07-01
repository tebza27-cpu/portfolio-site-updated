import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

# Accept DATABASE_URL from env or first CLI arg
DATABASE_URL = os.environ.get('DATABASE_URL') or (sys.argv[1] if len(sys.argv) > 1 else None)

if not DATABASE_URL:
    print("Usage: set DATABASE_URL or pass the URL as the first argument")
    sys.exit(1)

print('Connecting to', DATABASE_URL)
try:
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
except Exception as e:
    print('Connection failed:', e)
    sys.exit(2)

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
    print('Initialization complete')
except Exception as e:
    print('Initialization failed:', e)
finally:
    conn.close()
