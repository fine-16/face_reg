import subprocess
import sqlite3
import datetime

conn = sqlite3.connect('attendance.db')
cursor = conn.cursor()

filename = 'attendance_log/' + str(datetime.datetime.now())+'.csv'

def export_csv(filename):
        # CSVファイルにエクスポート
        cursor.execute('''
            SELECT * FROM attendance
        ''')
        records = cursor.fetchall()

        with open(filename, 'w', encoding='utf-8') as f:
            f.write("id,timestamp,name,status\n")
            for record in records:
                f.write(','.join(map(str, record)) + '\n')

export_csv(filename)

subprocess.call("rclone copy " + filename + "MyGoogleDrive:rpi_backup")

cursor.close()
conn.close()


