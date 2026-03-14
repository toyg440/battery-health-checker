#!/usr/bin/env python3
import sys
import subprocess

def check_tkinter():
    try:
        import tkinter
        return True
    except ImportError:
        print("\nTkinter is not installed.\n")
        print("Install it using:\n")
        print("    sudo apt install python3-tk\n")

        try:
            distro = subprocess.check_output(
                ["lsb_release", "-is"], text=True
            ).strip()
            print(f"Detected distro: {distro}")
        except:
            pass

        input("\nPress Enter to exit...")
        return False


if not check_tkinter():
    sys.exit(1)

import tkinter as tk
import re
from datetime import datetime
import os

BATTERY_PATH = "/org/freedesktop/UPower/devices/battery_BAT0"


#battery parsing
def get_battery_info():
    try:
        output = subprocess.check_output(
            ["upower", "-i", BATTERY_PATH],
            text=True
        )
        return output
    except:
        return None


def parse_battery_data(data):
    def find(pattern):
        match = re.search(pattern, data)
        return match.group(1) if match else "N/A"

    energy_full = find(r"energy-full:\s+([\d\.]+)")
    energy_design = find(r"energy-full-design:\s+([\d\.]+)")
    percentage = find(r"percentage:\s+(\d+%)")
    state = find(r"state:\s+(\w+)")
    cycles = find(r"cycle count:\s+(\d+)")

    if energy_full != "N/A" and energy_design != "N/A":
        health = (float(energy_full) / float(energy_design)) * 100
    else:
        health = 0

    return {
        "health": health,
        "full": energy_full,
        "design": energy_design,
        "percentage": percentage,
        "state": state,
        "cycles": get_cycle_count(),
    }

def get_cycle_count():
    path = "/sys/class/power_supply/BAT0/cycle_count"

    try:
        with open(path) as f:
            return f.read().strip()
    except:
        return "N/A"



def check_battery():
    data = get_battery_info()

    if not data:
        result_label.config(text="could not read battery info!")
        return

    info = parse_battery_data(data)

    result_text = (
        f"battery health: {info['health']:.2f}%\n"
        f"full charge: {info['full']} Wh\n"
        f"design capacity: {info['design']} Wh\n"
        f"charge: {info['percentage']}\n"
        f"state: {info['state']}\n"
        f"cycles: {info['cycles']}"
    )

    result_label.config(text=result_text)

    global last_report
    last_report = result_text


def generate_report():
    if not last_report:
        result_label.config(text="now run 'check battery'")
        return

    path = os.path.expanduser("~/battery_report.txt")

    with open(path, "w") as f:
        f.write("battery report\n")
        f.write("====================\n")
        f.write(f"generated: {datetime.now()}\n\n")
        f.write(last_report)

    result_label.config(text=f"report saved to:\n{path}")


#animations stff

class AnimatedButton(tk.Button):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.target_y = 0
        self.current_y = 0

    def place_animated(self, x, y):
        self.target_y = y
        self.current_y = y + 60
        self.place(x=x, y=self.current_y)
        self.animate()

    def animate(self):
        distance = self.target_y - self.current_y
        self.current_y += distance * 0.2
        self.place(y=int(self.current_y))

        if abs(distance) > 1:
            self.after(10, self.animate)


#ui stuff

root = tk.Tk()
root.title("battery health checker")
root.geometry("700x600")

title_label = tk.Label(
    root,
    text="click 'generate report' for the latest details",
    font=("Cascadia Code", 9),
)
title_label.place(x=120, y=40)


btn_check = AnimatedButton(
    root,
    text="check battery",
    command=check_battery,
    font=("Cascadia Code", 10),
)

btn_report = AnimatedButton(
    root,
    text="generate report",
    command=generate_report,
    font=("Cascadia Code", 10),
)

result_label = tk.Label(
    root,
    text="battery health: N/A",
    font=("Cascadia Code", 11),
    wraplength=380,
    justify="center"
)
result_label.place(x=150, y=260)

last_report = ""

root.after(200, lambda: btn_check.place_animated(220, 120))
root.after(400, lambda: btn_report.place_animated(210, 180))

root.mainloop()