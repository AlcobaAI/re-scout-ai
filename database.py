import sqlite3
from datetime import datetime

DB_NAME = "research_archive.db"

def setup_db():
    """Initializes the research database with relational tables."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        # 1. Datasets Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS datasets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_accessed TEXT,
                name TEXT,
                url TEXT,
                task TEXT,
                languages TEXT,
                UNIQUE(url, task) ON CONFLICT IGNORE
            )
        ''')

        # 2. Papers Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS papers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_accessed TEXT,
                title TEXT,
                arxiv_id TEXT UNIQUE,
                summary TEXT,
                pdf_link TEXT,
                authors TEXT
            )
        ''')

        # 3. Join Table (Relationships)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS paper_datasets (
                paper_id INTEGER,
                dataset_id INTEGER,
                FOREIGN KEY(paper_id) REFERENCES papers(id),
                FOREIGN KEY(dataset_id) REFERENCES datasets(id),
                PRIMARY KEY(paper_id, dataset_id)
            )
        ''')
        conn.commit()

def save_paper(title, arxiv_id, summary, pdf_link, authors):
    """Saves a paper and returns its database ID."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO papers (date_accessed, title, arxiv_id, summary, pdf_link, authors)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (datetime.now().strftime("%Y-%m-%d"), title, arxiv_id, summary, pdf_link, authors))
        
        # If ignore happened, we fetch the existing ID
        if cursor.lastrowid == 0:
            cursor.execute("SELECT id FROM papers WHERE arxiv_id = ?", (arxiv_id,))
            return cursor.fetchone()[0]
        
        conn.commit()
        return cursor.lastrowid

def save_dataset(name, url, task, languages):
    """Saves a dataset and returns its database ID."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO datasets (date_accessed, name, url, task, languages)
            VALUES (?, ?, ?, ?, ?)
        ''', (datetime.now().strftime("%Y-%m-%d"), name, url, task, languages))
        
        if cursor.lastrowid == 0:
            cursor.execute("SELECT id FROM datasets WHERE url = ? AND task = ?", (url, task))
            return cursor.fetchone()[0]
            
        conn.commit()
        return cursor.lastrowid

def link_paper_to_dataset(paper_id, dataset_id):
    """Creates a relationship between a paper and a dataset."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO paper_datasets (paper_id, dataset_id)
            VALUES (?, ?)
        ''', (paper_id, dataset_id))
        conn.commit()
        return conn.total_changes > 0

def get_research_summary():
    """SQL Join to show which papers used which datasets."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        query = '''
            SELECT p.title, d.name, d.url
            FROM papers p
            JOIN paper_datasets pd ON p.id = pd.paper_id
            JOIN datasets d ON d.id = pd.dataset_id
        '''
        return cursor.fetchall()