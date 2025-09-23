import os, time, shutil, yaml, logging, logging.handlers
from datetime import datetime

CONFIG = "/etc/backupd.yaml"

def load_config():
    with open(CONFIG, "r") as f:
        return yaml.safe_load(f)

def setup_logger():
    logger = logging.getLogger("backupd")
    logger.setLevel(logging.INFO)
    handler = logging.handlers.SysLogHandler(address="/dev/log")
    logger.addHandler(handler)
    return logger

def backup(src, dst, logger):
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    target = os.path.join(dst, f"backup-{ts}")
    try:
        shutil.copytree(src, target)
        logger.info(f"Backup successful: {src} -> {target}")
    except Exception as e:
        logger.error(f"Backup failed: {e}")

def main():
    cfg = load_config()
    logger = setup_logger()
    interval = cfg.get("interval", 3600)
    while True:
        backup(cfg["source"], cfg["destination"], logger)
        time.sleep(interval)

if __name__ == "__main__":
    main()
