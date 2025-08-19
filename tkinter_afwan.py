import subprocess
import tkinter as tk

# Function to run the subprocess

def run_automation_afwan(arg):
    command = f"python3 automation_Afwan.py {arg}"
    subprocess.run(command, shell=True)

# Function to create the GUI
def create_gui():
    root = tk.Tk()
    root.title("Automation Afwan Runner")

    label = tk.Label(root, text="Choose an option to run:")
    label.pack(pady=10)

    options = [
        ("A - AutoBooking", "A"),
        ("CB - Check Booking PNR", "CB"),
        ("CT - Celik Tafsir fetch", "CT"),
        # ("TB - Telegram Bot", "TB"),
        # ("WS - Web Scraping", "WS"),
        # ("AAI - AI Chat test", "AAI"),
        # ("CRM - Cron Run Multiple", "CRM"),
        # ("CRPC - Cron Run PC Multiple", "CRPC"),
        # ("CRO - Cron Run Once", "CRO"),
        ("CSFTP - Check SFTP", "CSFTP"),
        ("BEXPO - Expo go export", "BEXPO"),
        ("BFT - Flutter build", "BFT"),
        # ("RP - Reminder Parking", "RP"),
        # ("FW - Flask Website afwanproductions", "FW"),
        # ("CM - Check message telegram", "CM"),
        # ("BP - Bot Polling", "BP"),
        # ("STL - Summary Today Log", "STL"),
        # ("EXPO - Expo go export", "EXPO"),
        # ("PROXY - Proxy server", "PROXY"),
        # ("PROXYWE - Proxy with edit link html", "PROXYWE"),
    ]

    for text, arg in options:
        button = tk.Button(root, text=text, command=lambda arg=arg: run_automation_afwan(arg))
        button.pack(pady=5)

    root.mainloop()

# Run the GUI if this script is executed
if __name__ == "__main__":
    create_gui()
