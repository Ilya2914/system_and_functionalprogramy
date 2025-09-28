import tkinter as tk
from threading import Thread
from scapy.all import sniff, IP, ICMP, sr1
from datetime import datetime
import csv
import subprocess

recent_ips = {}
blocked_ips = set()
log_file = "traffic_log.csv"
running = False

proto_names = {1:"ICMP", 6:"TCP", 17:"UDP"}

def analyze_packet(packet):
    if not running:
        return

    if IP not in packet:
        return
    
    src = packet[IP].src
    dst = packet[IP].dst
    length = len(packet)
    proto = packet[IP].proto
    proto_name = proto_names.get(proto, str(proto))
    now = datetime.now().strftime("%H:%M:%S")
    alert = ""
    
    if length > 1500:
        alert = "Большой пакет"
    
    recent_ips[src] = recent_ips.get(src, 0) + 1
    if recent_ips[src] > 50:
        if src not in blocked_ips:
            block_ip(src)
        alert = "Подозрительная активность"
    
    msg = f"[{now}] {src} -> {dst}, Proto: {proto_name}, Len: {length}"
    if alert:
        msg += f" {alert}"
    
    text_box.insert(tk.END, msg + "\n")
    text_box.see(tk.END)

    with open(log_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([now, src, dst, proto_name, length, alert])

def block_ip(ip):
    try:
        subprocess.run(["sudo", "iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"], check=True)
        blocked_ips.add(ip)
        text_box.insert(tk.END, f"Заблокирован IP: {ip}\n")
    except Exception as e:
        text_box.insert(tk.END, f"Ошибка блокировки IP {ip}: {e}\n")
    text_box.see(tk.END)

def unblock_ip(ip):
    try:
        subprocess.run(["sudo", "iptables", "-D", "INPUT", "-s", ip, "-j", "DROP"], check=True)
        blocked_ips.discard(ip)
        text_box.insert(tk.END, f"Разблокирован IP: {ip}\n")
    except Exception as e:
        text_box.insert(tk.END, f"Ошибка разблокировки IP {ip}: {e}\n")
    text_box.see(tk.END)

def start_sniffing():
    sniff(prn=analyze_packet, store=False)

def on_start():
    global running
    running = True
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    status_label.config(text="Сниффинг запущен...")
    Thread(target=start_sniffing, daemon=True).start()

def on_stop():
    global running
    running = False
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
    status_label.config(text="Сниффинг остановлен")

def on_block_manual():
    ip = ip_entry.get().strip()
    if ip and ip not in blocked_ips:
        block_ip(ip)

def on_unblock_manual():
    ip = ip_entry.get().strip()
    if ip and ip in blocked_ips:
        unblock_ip(ip)

# GUI
root = tk.Tk()
root.title("Сетевой мониторинг")
root.geometry("800x600")

status_label = tk.Label(root, text="Нажмите 'Начать' для запуска")
status_label.pack(pady=5)

start_button = tk.Button(root, text="Начать", command=on_start)
start_button.pack(pady=5)

stop_button = tk.Button(root, text="Стоп", command=on_stop, state=tk.DISABLED)
stop_button.pack(pady=5)

ip_frame = tk.Frame(root)
ip_frame.pack(pady=5)

ip_entry = tk.Entry(ip_frame)
ip_entry.pack(side=tk.LEFT, padx=5)

block_button = tk.Button(ip_frame, text="Блокировать", command=on_block_manual)
block_button.pack(side=tk.LEFT, padx=5)

unblock_button = tk.Button(ip_frame, text="Разблокировать", command=on_unblock_manual)
unblock_button.pack(side=tk.LEFT, padx=5)

text_box = tk.Text(root)
text_box.pack(fill=tk.BOTH, expand=True)

with open(log_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Time", "Source IP", "Dest IP", "Protocol", "Length", "Alert"])

root.mainloop()

