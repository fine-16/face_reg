import subprocess
import sqlite3
import datetime
import schedule
import time


class sync_unit:
    def __init__(self):
        self.conn = sqlite3.connect('attendance.db')
        self.cursor = self.conn.cursor()
        self.backup_filename = 'attendance_log/' + datetime.datetime.now().isoformat()+'.csv'
        self.prod_filename = "attendance_prod.csv"

        


    def export_csv(self,filename):
        # CSVファイルにエクスポート
        self.cursor.execute('''
            SELECT * FROM attendance
        ''')
        records = self.cursor.fetchall()

        with open(filename, 'w', encoding='utf-8') as f:
            f.write("id,timestamp,name,status\n")
            for record in records:
                f.write(','.join(map(str, record)) + '\n')


    def rclone(self,from_filename,to_filename):
        self.export_csv(from_filename)
        cmd = "rclone " + "copy " + from_filename + " MyGoogleDrive:" + to_filename

        try:
        # コマンドを実行し、完了するまで待機（エラー時は例外を発生）
            result = subprocess.run(cmd, check=True, capture_output=True, text=True,shell=True)
            print("成功:", result.stdout)
        except subprocess.CalledProcessError as e:
            print("エラーが発生しました:", e.stderr)
    
    def sync(self):
        self.rclone(self.backup_filename,"rpi_backup")
        self.rclone(self.prod_filename,"rpi_prod")

    def close(self):
        self.cursor.close()
        self.conn.close()

def job():
    sync = sync_unit()
    sync.sync()
    sync.close()

start_time=time.time()
limit_seconds = 36

schedule.every(1).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)

    elapsed_time =time.time() - start_time
    if elapsed_time > limit_seconds:
        print("Finish!!")
        break
