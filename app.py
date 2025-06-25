import os

import pyodbc, struct
from flask import Flask, render_template, request, redirect, url_for
from azure import identity

app = Flask(__name__)
DB_CONNECTION_STRING = os.environ["DB_CONNECTION_STRING"]


def get_db_connection():
    credential = identity.DefaultAzureCredential(exclude_interactive_browser_credential=False)
    token_bytes = credential.get_token("https://database.windows.net/.default").token.encode("UTF-16-LE")
    token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)
    SQL_COPT_SS_ACCESS_TOKEN = 1256  # This connection option is defined by microsoft in msodbcsql.h
    conn = pyodbc.connect(DB_CONNECTION_STRING, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct})
    return conn


# Create sample table if not exists
def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Items')
        CREATE TABLE Items (
            id INT PRIMARY KEY IDENTITY,
            name NVARCHAR(100) NOT NULL,
            created_at DATETIME DEFAULT GETDATE()
        )
        """)
        conn.commit()
    except Exception as e:
        print(f"Database error: {str(e)}")


# Routes
@app.route("/")
def index():  
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Items")
    items = cursor.fetchall()
    return render_template('index.html', items=items)


@app.route("/add", methods=['POST'])
def add_item():
    name = request.form['name']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Items (name) VALUES (?)", name)
    conn.commit()
    return redirect(url_for('index'))


if __name__ == "__main__":
    init_db()
    app.run(host='0.0.0.0', port=os.environ.get('APP_PORT', "5000"))
