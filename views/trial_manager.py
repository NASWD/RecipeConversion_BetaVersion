import uuid,platform,hashlib,os
from datetime import datetime
from PyQt5.QtCore import QSettings

TRIAL_PERIOD_DAYS=14


def get_machine_id():
    system_info=platform.node()+platform.system()+platform.processor()
    mac=hex(uuid.getnode())
    raw_id=system_info+mac
    return hashlib.sha256(raw_id.encode()).hexdigest()


def is_trial_expired():
    settings=QSettings("Nordson","Recipe Conversion")
    machine_id=get_machine_id()

    # Unique keys per machine
    trial_key=f"trial_start_{machine_id}"
    last_run_key=f"last_run_{machine_id}"

    # Today's date
    today=datetime.today()

    # Check trial start
    trial_start_str=settings.value(trial_key)
    last_run_str=settings.value(last_run_key)

    if trial_start_str:
        trial_start=datetime.strptime(trial_start_str,"%Y-%m-%d")
        days_used=(today-trial_start).days

        # Clock rollback check
        if last_run_str:
            last_run=datetime.strptime(last_run_str,"%Y-%m-%d")
            if today<last_run:
                return True  # User tampered with system clock

        # Update last run date
        settings.setValue(last_run_key,today.strftime("%Y-%m-%d"))

        return days_used>TRIAL_PERIOD_DAYS

    else:
        # FIRST INSTALL DETECTED
        # Write trial start and last run
        settings.setValue(trial_key,today.strftime("%Y-%m-%d"))
        settings.setValue(last_run_key,today.strftime("%Y-%m-%d"))
        return False
