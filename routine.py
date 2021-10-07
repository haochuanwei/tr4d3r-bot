import os
import plac
import pyotp
import wrappy
import robin_stocks.robinhood as rh
from io import StringIO
from pprint import pformat
from wasabi import msg as wsbm
from datetime import datetime
from importlib import import_module
from apscheduler.schedulers.blocking import BlockingScheduler
from locallib import datetime_stamp, snapshot_path
from tr4d3r.utils.misc import DATETIME_FORMAT, utcnow

def login():
    totp = pyotp.TOTP(os.environ['MFA_KEY']).now()
    login = rh.login(os.environ['RH_USERNAME'], os.environ['RH_PASSWORD'], mfa_code=totp)
    return login

@plac.pos('bot_module_path', "Bot module path")
@plac.flg('debug', "Enable debug mode")
@plac.flg('recurring', "Enable recurring mode")
def main(bot_module_path, debug=False, recurring=False):
    login_info = login()
    
    # load specified bot module
    bot_module = import_module(bot_module_path)
    folio = bot_module.get_portfolio()
    manager = bot_module.get_manager()
    chat = bot_module.get_chat()
    
    def tick_callback(execute=True):
        folio.refresh_open_orders()
        gap_seconds = manager.tick_write(folio, execute=execute)
        folio._info(f"current status\n{pformat(folio.to_dict())}")
        return gap_seconds
    
    def save_callback():
        new_snapshot_path = snapshot_path(bot_module.FOLIO_PATH_ROOT)
        for _path in [bot_module.FOLIO_PATH_LATEST, new_snapshot_path]:
            folio.dump_json(_path)
        return new_snapshot_path
    
    @wrappy.guard(print_traceback=True)
    def routine(execute=True):
        wsbm.divider(f"Routine call {utcnow().strftime(DATETIME_FORMAT)}")
        # get console and start recording
        if debug:
            wsbm.info("Setting console property")
        console = manager.__class__.CONSOLE
        prev_record = console.record
        console.record = True
        
        # actual activity of routine
        if debug:
            wsbm.info("Running tick")
        gap_seconds = tick_callback(execute=execute)
        new_snapshot_path = save_callback()
        
        # send message and report
        if debug:
            wsbm.info("Sending report")
        chat.ping(f"{bot_module.CHAT_MESSAGE_PREFIX} Routine callback: gap {int(gap_seconds)} seconds")
        with StringIO(console.export_html()) as report:
            chat.attach(report, filename=f"routine-{datetime_stamp()}.html")
        with open(bot_module.FOLIO_PATH_LATEST, 'r') as folio_json:
            chat.attach(folio_json, filename=f"routine-{datetime_stamp()}.json")
        
        # reset the console record flag
        console.record = prev_record
        wsbm.divider()
    
    def autopilot():
        routine(execute=False)
    
        scheduler = BlockingScheduler()
        if debug:
            job_kwargs = dict(
                trigger='interval',
                minutes=1,
                id='routine-debug',
            )
        else:
            job_kwargs = dict(
                trigger='cron',
                day_of_week='mon-fri',
                hour=14,
                minute=0,
                id='routine',
            )
        scheduler.add_job(routine, **job_kwargs)
        scheduler.start()
        print("Scheduler process ended")

    if recurring:
        autopilot()
    else:
        routine(execute=True)
    
if __name__ == '__main__':
    plac.call(main)
