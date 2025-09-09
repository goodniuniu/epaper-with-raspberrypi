import os
import sqlite3

def init_db(db_path='data/poems.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS poems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            dynasty TEXT,
            author TEXT,
            content TEXT NOT NULL,
            full_content TEXT NOT NULL,
            saved_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def get_db_path(relative_path):
    """计算数据库文件的绝对路径。"""
    dir_of_script = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(dir_of_script, '..', relative_path)

def save_poem_to_db(poem_data, db_path='poems.db'):
    db_path = get_db_path(db_path)  # 将相对路径转换为绝对路径
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO poems (title, dynasty, author, content, full_content)
        VALUES (?, ?, ?, ?, ?)
    ''', (poem_data['title'], poem_data['dynasty'], poem_data['author'], poem_data['content'], poem_data['full_content']))
    print("writing to db")
    conn.commit()
    conn.close()

def read_poem_from_db(poem_id, db_path='poems.db'):
    db_path = get_db_path(db_path)  # 将相对路径转换为绝对路径
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM poems WHERE id=?
    ''', (poem_id,))
    poem = cursor.fetchone()
    conn.close()
    return poem

def update_poem_in_db(poem_id, new_content, db_path='poems.db'):
    db_path = get_db_path(db_path)  # 将相对路径转换为绝对路径
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE poems
        SET content=?
        WHERE id=?
    ''', (new_content, poem_id))
    conn.commit()
    conn.close()

def delete_poem_from_db(poem_id, db_path='poems.db'):
    db_path = get_db_path(db_path)  # 将相对路径转换为绝对路径
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM poems
        WHERE id=?
    ''', (poem_id,))
    conn.commit()
    conn.close()


def find_poem_id_by_context(context, db_path='poems.db'):
    db_path = get_db_path(db_path)  # 将相对路径转换为绝对路径
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id FROM poems WHERE content LIKE ?
    ''', ('%' + context + '%',))
    poem_ids = cursor.fetchall()
    conn.close()
    return [poem_id[0] for poem_id in poem_ids]
