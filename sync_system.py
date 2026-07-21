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

cmd = "rclone " + "copy " + filename + " MyGoogleDrive:rpi_backup"
#subprocess.call("rclone copy " + filename + " MyGoogleDrive:rpi_backup")

try:
    # コマンドを実行し、完了するまで待機（エラー時は例外を発生）
    result = subprocess.run(cmd, check=True, capture_output=True, text=True,shell=True)
    print("成功:", result.stdout)
except subprocess.CalledProcessError as e:
    print("エラーが発生しました:", e.stderr)

cursor.close()
conn.close()


