import sqlite3


class Database:
    def __init__(self):
        self.conn = sqlite3.connect('attendance.db')
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        # テーブルが存在しない場合は作成
        #ここでタイムスタンプはJTCになっている
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT DEFAULT (datetime('now', 'localtime')),      
                name TEXT NOT NULL,
                status TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    
    def insert_record(self, name, status):
        # レコードを挿入
        self.cursor.execute('''
            INSERT INTO attendance (name, status)
            VALUES (?, ?)
        ''', (name, status))
        self.conn.commit()

    def get_last_record(self):
        # 最後のレコードを取得
        self.cursor.execute('''
            SELECT * FROM attendance ORDER BY id DESC LIMIT 1
        ''')
        return self.cursor.fetchone()

    def export_csv(self, filename):
        # CSVファイルにエクスポート
        self.cursor.execute('''
            SELECT * FROM attendance
        ''')
        records = self.cursor.fetchall()

        with open(filename, 'w', encoding='utf-8') as f:
            f.write("id,timestamp,name,status\n")
            for record in records:
                f.write(','.join(map(str, record)) + '\n')

    def delete_table(self):
        # テーブルを削除
        self.cursor.execute('''
            DROP TABLE IF EXISTS attendance
        ''')
        self.conn.commit()
    
    def close(self):
        # データベース接続を閉じる
        self.cursor.close()
        self.conn.close()



if __name__ == "__main__":
    db = Database()
    
    db.close()