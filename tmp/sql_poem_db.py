def query_all_poems(db_path='poems.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT title, dynasty, author, content, full_content FROM poems')
    poems = cursor.fetchall()
    conn.close()
    return poems

for poem in query_all_poems():
    print(poem)
