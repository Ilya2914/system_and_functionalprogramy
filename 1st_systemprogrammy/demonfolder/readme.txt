sudo systemctl daemon-reload
sudo systemctl enable backupd  #автозапуск
sudo systemctl start backupd   # запустить сейчас
sudo systemctl stop backupd   # остановка
sudo systemctl restart backupd   # перезагрузка




sudo chown -R ilya29:ilya29 /home/ilya29/Desktop/demonfolder/copytest/

rm -rf /home/ilya29/Desktop/demonfolder/copytest/

systemctl status backupd
journalctl -u backupd -f


sudo nano /etc/systemd/system/backupd.service  #для unit файла
sudo nano /etc/backupd.yaml #Для конфига
