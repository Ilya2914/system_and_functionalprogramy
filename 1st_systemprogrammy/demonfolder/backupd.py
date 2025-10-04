import os
import time
import yaml
import shutil
import logging
from datetime import datetime

CONFIG_PATH = "/etc/backupd.yaml"

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

def setup_logging(log_path):
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    logging.info("=== Демон запущен и готов к работе ===")

def create_backup(source, destination):
    try:
        if not os.path.exists(source):
            logging.error(f"Исходная директория не найдена: {source}")
            return

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = os.path.join(destination, f"backup-{timestamp}")
        shutil.copytree(source, backup_path)

        logging.info(f" Успешно создана резервная копия: {backup_path}")

    except Exception as e:
        logging.error(f" Ошибка при создании резервной копии: {e}")

def main():
    cfg = load_config()
    source = cfg["source_dir"]
    destination = cfg["backup_dir"]
    interval = cfg.get("interval_minutes", 60)
    log_file = cfg.get("log_file", "/var/log/backupd.log")

    setup_logging(log_file)

    logging.info(f"Источник: {source}")
    logging.info(f"Каталог для резервных копий: {destination}")
    logging.info(f"Интервал копирования: {interval} мин.")

    while True:
        create_backup(source, destination)
        time.sleep(interval * 60)

if __name__ == "__main__":
    main()

