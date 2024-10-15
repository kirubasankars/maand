import sqlite3

def get_connection():
    return sqlite3.connect('/workspace/kv.db')

def setup():
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS key_value (namespace, key, version, deleted, value)')
        connection.commit()

def put_key_value(namespace, key, value):
    __internal_put_key_value(namespace, key, value, 0)

def __internal_put_key_value(namespace, key, value, deleted):
    if type(value) is not str:
        raise TypeError('value must be a string')

    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT max(version) FROM key_value WHERE namespace = ? AND key = ? ", (namespace, key))
        row = cursor.fetchone()
        version = 0
        if row and row[0]:
            version = int(row[0])
        cursor.execute('INSERT INTO key_value (namespace, key, version, deleted, value) VALUES (?, ?, ?, ?, ?)', (namespace, key, version + 1, deleted, value))
        connection.commit()

def get_value(namespace, key):
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT value FROM key_value WHERE namespace = ? AND key = ? AND version = (SELECT max(version) FROM key_value WHERE namespace = ? AND key = ?) AND deleted = 0', (namespace, key, namespace, key))
        row = cursor.fetchone()
        return row[0] if row else None

def delete_key(namespace, key):
    __internal_put_key_value(namespace, key, get_value(namespace, key), 1)

def gc():
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT namespace, key, max(version) FROM key_value group by key')
        rows = cursor.fetchall()
        for row in rows:
            namespace, key, version = row
            version = version - 7
            if version < 1:
                continue
            cursor.execute("DELETE FROM key_value WHERE namespace = ? AND key = ? AND version = ?", (namespace, key, version))