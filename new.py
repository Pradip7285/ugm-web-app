import platform
import socket
import uuid
import psutil
import getpass
import os
import subprocess
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pathlib import Path
from datetime import datetime

def get_system_info():
    info = {}

    info['Hostname'] = socket.gethostname()
    info['IP Address'] = socket.gethostbyname(info['Hostname'])
    info['MAC Address'] = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                                    for elements in range(0, 2*6, 8)][::-1])
    info['Username'] = getpass.getuser()
    info['Operating System'] = platform.system()
    info['OS Version'] = platform.version()
    info['OS Release'] = platform.release()
    info['Architecture'] = platform.machine()
    info['Processor'] = platform.processor()
    info['CPU Cores'] = psutil.cpu_count(logical=False)
    info['Logical CPUs'] = psutil.cpu_count(logical=True)
    info['Total RAM (GB)'] = round(psutil.virtual_memory().total / (1024 ** 3), 2)

    info['Disks'] = []
    for part in psutil.disk_partitions():
        usage = psutil.disk_usage(part.mountpoint)
        info['Disks'].append({
            'Device': part.device,
            'Mountpoint': part.mountpoint,
            'File system': part.fstype,
            'Total Size (GB)': round(usage.total / (1024 ** 3), 2)
        })

    # Serial Number
    if platform.system() == 'Windows':
        try:
            serial = subprocess.check_output("wmic bios get serialnumber", shell=True).decode().split("\n")[1].strip()
            info['Serial Number'] = serial
        except Exception as e:
            info['Serial Number'] = f"Error: {str(e)}"
    else:
        try:
            serial = subprocess.check_output("sudo dmidecode -s system-serial-number", shell=True).decode().strip()
            info['Serial Number'] = serial
        except Exception as e:
            info['Serial Number'] = f"Error: {str(e)}"

    return info

def generate_pdf(info, filename='system_info.pdf'):
    downloads_path = str(Path.home() / "Downloads")
    filepath = os.path.join(downloads_path, filename)

    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica", 12)
    text_object = c.beginText(40, height - 50)
    text_object.textLine(f"System Information Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    text_object.textLine("")

    for key, value in info.items():
        if isinstance(value, list):
            text_object.textLine(f"{key}:")
            for item in value:
                for sub_key, sub_value in item.items():
                    text_object.textLine(f"    {sub_key}: {sub_value}")
                text_object.textLine("")
        else:
            text_object.textLine(f"{key}: {value}")

    c.drawText(text_object)
    c.showPage()
    c.save()

    print(f"[+] PDF saved to: {filepath}")

if __name__ == "__main__":
    system_info = get_system_info()
    generate_pdf(system_info)
