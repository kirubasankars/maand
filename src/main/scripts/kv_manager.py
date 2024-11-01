import functools
import os.path
import sqlite3

import const

def get_db():
    return sqlite3.connect(const.KV_DB_PATH)

def setup():
    with get_db() as connection:
        cursor = connection.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS key_value (key, value, namespace, version, ttl, created_date, rotatable, deleted)')
        connection.commit()

def put_key_value(namespace, key, value, ttl=-1, rotatable=0):
    if type(value) is not str:
        raise TypeError('value must be a string')

    with get_db() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT max(version), value FROM key_value WHERE namespace = ? AND key = ? GROUP BY key, namespace", (namespace, key))
        row = cursor.fetchone()
        version = 0
        if row:
            version = int(row[0])
            old_value = str(row[1])
        if old_value != value:
            cursor.execute('INSERT INTO key_value (key, value, namespace, version, ttl, created_date, rotatable, deleted) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (key, value, namespace, version + 1, ttl, get_global_unix_epoch(), rotatable, 0,))
        connection.commit()

def get_value(namespace, key):
    with get_db() as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT value FROM key_value WHERE namespace = ? AND key = ? AND version = (SELECT max(version) FROM key_value WHERE namespace = ? AND key = ?) AND deleted = 0', (namespace, key, namespace, key))
        row = cursor.fetchone()
        return row[0] if row else None

def delete_key(namespace, key):
    with get_db() as connection:
        cursor = connection.cursor()
        cursor.execute('INSERT INTO key_value (key, value, namespace, version, ttl, created_date, rotatable, deleted) SELECT key, value, namespace, version, ttl, created_date, rotatable, 1 FROM key_value WHERE namespace = ? AND key = ? AND version = (SELECT max(version) FROM key_value WHERE namespace = ? AND key = ?)', (namespace, key, namespace, key))
        row = cursor.fetchone()
        return row[0] if row else None

def gc():
    with get_db() as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT namespace, key, max(version) FROM key_value group by key')
        rows = cursor.fetchall()
        for row in rows:
            namespace, key, version = row
            version = version - 7
            if version < 1:
                continue
            cursor.execute("DELETE FROM key_value WHERE namespace = ? AND key = ? AND version = ?", (namespace, key, version))

def setup_global_unix_epoch():
    if not os.path.exists("/tmp/unix_epoch"):
        with get_db() as connection:
            c = connection.cursor()
            c.execute("SELECT unixepoch()")
            row = c.fetchone()
            with open("/tmp/unix_epoch", "w") as f:
                f.write(str(row[0]))

@functools.cache
def get_global_unix_epoch():
    with open("/tmp/unix_epoch", "r") as f:
        return f.read()

if __name__ == "__main__":
    setup_global_unix_epoch()
