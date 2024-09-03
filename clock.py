from apscheduler.schedulers.blocking import BlockingScheduler
from your_update_script import update_daily

sched = BlockingScheduler()

@sched.scheduled_job('cron', hour=0)
def scheduled_job():
    update_daily()

sched.start()