import random
import time
import firebase_admin
from firebase_admin import credentials, db
import sys
import threading
import os
import socket
import tkinter as tk
from tkinter import messagebox

if getattr(sys, 'frozen', False):
    current_dir = os.path.dirname(sys.executable)
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))

cred_path = os.path.join(current_dir, 'hello.json')

if not os.path.exists(cred_path):
    print(f"Error: '{cred_path}' does not exist!")
    sys.exit(1)

cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://message-53c5c-default-rtdb.firebaseio.com/'
})

client_id = sys.argv[1] if len(sys.argv) > 1 else 'client_1'

status_ref = db.reference(f"status/{client_id}")
random_numbers_ref = db.reference(f"random_numbers/{client_id}")
message_ref = db.reference("hello_messages")
ms_ref = db.reference("hi")

stop_threads = False

def is_connected():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def monitor_network_status():
    network_status = None
    while not stop_threads:
        current_status = is_connected()
        if current_status != network_status:
            ms_ref.push({
                'client_id': client_id,
                'message': 'Network is online' if current_status else 'Network is offline',
                'timestamp': time.time()
            })
        network_status = current_status
        time.sleep(1)

def random_numbers_listener(event):
    if event.data:
        display_message(f"Random Number: {event.data}")

def message_listener(event):
    if event.data and event.data.get('client_id') == client_id:
        display_message(f"Received Message: {event.data['message']}")

def set_status_online():
    while not stop_threads:
        status_ref.set({
            'status': 'online',
            'timestamp': time.time()
        })
        time.sleep(30)

def generate_random_numbers():
    while not stop_threads:
        random_number = random.randint(1, 100)
        random_numbers_ref.push({
            'number': random_number,
            'timestamp': time.time()
        })
        time.sleep(1)

def handle_exit():
    status_ref.set({
        'status': 'offline',
        'timestamp': time.time()
    })

def start_application():
    global stop_threads
    stop_threads = False
    try:
        threading.Thread(target=set_status_online, daemon=True).start()
        threading.Thread(target=random_numbers_ref.listen, args=(random_numbers_listener,), daemon=True).start()
        threading.Thread(target=message_ref.listen, args=(message_listener,), daemon=True).start()
        threading.Thread(target=generate_random_numbers, daemon=True).start()
        threading.Thread(target=monitor_network_status, daemon=True).start()
    except Exception as e:
        print(f"An error occurred: {e}")
        handle_exit()

def stop_application():
    global stop_threads
    stop_threads = True
    handle_exit()
    messagebox.showinfo("Stopped", "Application has been stopped.")

def display_message(message):
    message_label.config(text=message)

def on_start_button_click():
    messagebox.showinfo("Starting", "Application is starting...")
    start_application()

def on_stop_button_click():
    stop_application()

window = tk.Tk()
window.title("Firebase Client Application")
window.geometry("400x250")

start_button = tk.Button(window, text="Start", width=20, height=2, command=on_start_button_click)
start_button.pack(pady=20)

stop_button = tk.Button(window, text="Stop", width=20, height=2, command=on_stop_button_click)
stop_button.pack(pady=10)

message_label = tk.Label(window, text="Waiting for messages...", width=40, height=4, anchor='center', justify='center')
message_label.pack(pady=20)

window.mainloop()
