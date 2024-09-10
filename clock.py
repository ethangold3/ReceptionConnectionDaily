from apscheduler.schedulers.blocking import BlockingScheduler
import subprocess
import sys
import os

sched = BlockingScheduler()

@sched.scheduled_job('cron', hour=0)
def scheduled_job():
    print("Running update_daily.py")
    script_path = os.path.join(os.path.dirname(__file__), 'scripts', 'update_daily.py')
    result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
    print("Output:", result.stdout)
    if result.stderr:
        print("Error:", result.stderr)

if __name__ == "__main__":
    print("Starting scheduler")
    sched.start()