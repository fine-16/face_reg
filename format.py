import sqlite3

conn = sqlite3.connect('attendance.db')
cursor = conn.cursor()

def create_table():
        # テーブルが存在しない場合は作成
        #ここでタイムスタンプはJTCになっている
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT DEFAULT (datetime('now', 'localtime')),      
                name TEXT NOT NULL,
                status TEXT NOT NULL
            )
        ''')
        conn.commit()



def delete_table():
        # テーブルを削除
        cursor.execute('''
            DROP TABLE IF EXISTS attendance
        ''')
        conn.commit()

delete_table()
create_table()


cursor.close()
conn.close()