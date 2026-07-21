import subprocess
import sqlite3
import datetime

conn = sqlite3.connect('attendance.db')
cursor = conn.cursor()

backup_filename = 'attendance_log/' + datetime.datetime.now().isoformat()+'.csv'
prod_filename = "attendance_prod.csv"

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


def rclone(from_filename,to_filename):
    export_csv(from_filename)
    cmd = "rclone " + "copy " + from_filename + " MyGoogleDrive:" + to_filename

    try:
    # コマンドを実行し、完了するまで待機（エラー時は例外を発生）
        result = subprocess.run(cmd, check=True, capture_output=True, text=True,shell=True)
        print("成功:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("エラーが発生しました:", e.stderr)


rclone(backup_filename,"rpi_backup")
rclone(prod_filename,"rpi_prod")

cursor.close()
conn.close()


