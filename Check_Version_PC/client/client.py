
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import subprocess
import platform
import threading
import socket
import os
import psutil
import sys
import time

from config import SERVER_URL
from config import DEPARTMENTS
from config import ASSET_TYPES

# =========================
# CHẠY COMMAND
# =========================
def run_command(commands):

    for cmd in commands:

        try:

            result = subprocess.check_output(
                cmd,
                shell=True,
                text=True,
                encoding="utf-8",
                errors="ignore"
            )

            result = result.strip()

            if result:

                lines = [
                    line.strip()
                    for line in result.splitlines()
                    if line.strip()
                ]

                if len(lines) >= 2:
                    return " ".join(lines[1:])

                elif len(lines) == 1:
                    return lines[0]

        except Exception:
            pass

    return "Không lấy được"

# =========================
# RAM INFO
# =========================
def get_ram_info():
    try:
        total_ram_gb = psutil.virtual_memory().total / (1024**3)
        return f"{total_ram_gb:.2f} GB"
    except:
        return "Không lấy được"

# =========================
# CPU INFO
# =========================
def get_cpu_info():
    try:
        cpu_model = run_command([
            'powershell "(Get-CimInstance Win32_Processor).Name"',
            "wmic cpu get name"
        ])

        if cpu_model and cpu_model != "Không lấy được":
            cpu_count = psutil.cpu_count()
            return f"{cpu_model} ({cpu_count} cores)"

        return "Không lấy được"

    except:
        return "Không lấy được"

# =========================
# DISK INFO
# =========================
def get_disk_info():

    try:

        total_disk = 0

        disk_details = []

        for drive in ['C:', 'D:', 'E:', 'F:', 'G:', 'H:']:

            try:

                disk_usage = psutil.disk_usage(drive + '\\')

                total_gb = disk_usage.total / (1024**3)

                total_disk += disk_usage.total

                disk_details.append(
                    f"{drive}: {total_gb:.2f}GB"
                )

            except:
                pass

        if total_disk > 0:

            total_disk_gb = total_disk / (1024**3)

            details_str = " | ".join(disk_details)

            return f"Tổng: {total_disk_gb:.2f} GB ({details_str})"

        return "Không lấy được"

    except:
        return "Không lấy được"

# =========================
# VGA INFO
# =========================
def get_vga_info():

    try:

        return run_command([
            'powershell "(Get-CimInstance Win32_VideoController).Name"',
            "wmic path win32_VideoController get name"
        ])

    except:
        return "Không lấy được"

# =========================
# DISK POWER ON HOURS
# =========================
def get_disk_power_on_hours():

    try:

        result = run_command([
            'powershell "Get-PhysicalDisk | Select FriendlyName, MediaType"'
        ])

        return result

    except:
        return "Không lấy được"

# =========================
# NHIỆT ĐỘ
# =========================
def get_temperature_info():

    try:
        temperatures = psutil.sensors_temperatures()
        readings = []

        for sensor_name, entries in temperatures.items():
            for entry in entries:
                if entry.current is not None:
                    label = entry.label or sensor_name
                    readings.append(f"{label}: {entry.current:.1f}°C")

        if readings:
            return " | ".join(readings)
    except Exception:
        pass

    acpi_temperature = run_command([
        'powershell "Get-CimInstance -Namespace root/wmi -ClassName MSAcpi_ThermalZoneTemperature | ForEach-Object { [math]::Round($_.CurrentTemperature / 10 - 273.15, 1) }"'
    ])

    if acpi_temperature != "Không lấy được":
        return f"Vùng nhiệt hệ thống: {acpi_temperature}°C"

    return "Chưa đọc được (Windows không cung cấp cảm biến nhiệt)"

# =========================
# ĐÁNH GIÁ TÌNH TRẠNG MÁY
# =========================
def get_system_health():

    health_lines = []

    try:
        cpu_load = psutil.cpu_percent(interval=1)
        cpu_status = "Ổn định" if cpu_load < 85 else "Cao"
        health_lines.append(
            f"CPU: {cpu_status} - mức sử dụng hiện tại {cpu_load:.1f}%"
        )
    except Exception:
        health_lines.append("CPU: Không kiểm tra được")

    try:
        memory = psutil.virtual_memory()
        memory_status = "Ổn định" if memory.percent < 85 else "Cao"
        health_lines.append(
            f"RAM: {memory_status} - đang sử dụng {memory.percent:.1f}%"
        )
    except Exception:
        health_lines.append("RAM: Không kiểm tra được")

    try:
        checked_drives = []
        for partition in psutil.disk_partitions(all=False):
            if not os.path.exists(partition.mountpoint):
                continue

            usage = psutil.disk_usage(partition.mountpoint)
            free_percent = usage.free / usage.total * 100
            disk_status = "Ổn định" if free_percent >= 15 else "Sắp đầy"
            checked_drives.append(
                f"{partition.mountpoint}: {disk_status} - còn {free_percent:.1f}%"
            )

        health_lines.extend(checked_drives)
    except Exception:
        health_lines.append("Ổ đĩa: Không kiểm tra được")

    physical_disk_status = run_command([
        'powershell "Get-PhysicalDisk | Select FriendlyName,HealthStatus,OperationalStatus | Format-Table -HideTableHeaders | Out-String"'
    ])
    health_lines.append(f"Sức khỏe thiết bị lưu trữ: {physical_disk_status}")
    health_lines.append(f"Nhiệt độ: {get_temperature_info()}")

    return "\n".join(health_lines)

# =========================
# STATUS
# =========================
def set_status(message, color="black"):

    status_label.config(
        text=message,
        foreground=color
    )

# =========================
# HIỂN THỊ THÔNG TIN MÁY
# =========================
def check_system_info():

    info_window = tk.Toplevel(root)

    info_window.title("Thông tin cấu hình máy")

    info_window.geometry("750x600")

    text = tk.Text(
        info_window,
        wrap="word",
        font=("Consolas", 10)
    )

    scrollbar = ttk.Scrollbar(
        info_window,
        command=text.yview
    )

    text.configure(
        yscrollcommand=scrollbar.set
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    text.pack(
        fill="both",
        expand=True
    )

    text.insert("end", "ĐANG KIỂM TRA CẤU HÌNH VÀ TÌNH TRẠNG MÁY...\n")

    btn_check.config(state="disabled")

    def collect_info():
        # Chạy lệnh hệ thống ngoài luồng giao diện để cửa sổ không bị treo.
        machine_name = run_command([
            'powershell "(Get-CimInstance Win32_ComputerSystem).Model"',
            "wmic csproduct get name"
        ])

        serial_number = run_command([
            'powershell "(Get-CimInstance Win32_BIOS).SerialNumber"',
            "wmic bios get serialnumber"
        ])

        cpu_info = get_cpu_info()
        ram_info = get_ram_info()
        disk_info = get_disk_info()
        vga_info = get_vga_info()
        disk_health = get_disk_power_on_hours()
        temperature_info = get_temperature_info()
        system_health = get_system_health()

        system_text = f"""
==================================================
THÔNG TIN CẤU HÌNH MÁY
==================================================

MODEL:
{machine_name}
--------------------------------------------------
SERIAL NUMBER:
{serial_number}
--------------------------------------------------
CPU:
{cpu_info}
--------------------------------------------------
RAM:
{ram_info}
--------------------------------------------------
Ổ CỨNG:
{disk_info}
--------------------------------------------------
THÔNG TIN Ổ CỨNG:
{disk_health}
--------------------------------------------------
NHIỆT ĐỘ:
{temperature_info}
--------------------------------------------------
VGA:
{vga_info}


==================================================
ĐÁNH GIÁ TÌNH TRẠNG MÁY
==================================================
{system_health}
"""

        root.after(0, lambda: show_check_result(info_window, text, system_text))

    threading.Thread(target=collect_info, daemon=True).start()


def show_check_result(info_window, text, system_text):

    if not info_window.winfo_exists():
        btn_check.config(state="normal")
        return

    text.config(state="normal")
    text.delete("1.0", "end")
    text.insert("end", system_text)
    text.config(state="disabled")
    btn_check.config(state="normal")


# =========================
# SUBMIT DATA
# =========================
def submit_data():

    full_name = entry_name.get().strip()

    employee_code = entry_code.get().strip()

    department = combo_department.get().strip()

    asset_type = combo_asset.get().strip()

    if not full_name:

        messagebox.showwarning(
            "Thông báo",
            "Vui lòng nhập họ tên"
        )

        return

    if not employee_code:

        messagebox.showwarning(
            "Thông báo",
            "Vui lòng nhập mã nhân viên"
        )

        return

    if not department:

        messagebox.showwarning(
            "Thông báo",
            "Vui lòng chọn bộ phận"
        )

        return

    if not asset_type:

        messagebox.showwarning(
            "Thông báo",
            "Vui lòng chọn loại tài sản"
        )

        return

    btn_submit.config(state="disabled")

    progress.start(10)

    set_status(
        "Đang lấy thông tin máy và gửi dữ liệu...",
        "blue"
    )

    threading.Thread(
        target=send_data_thread,
        args=(
            full_name,
            employee_code,
            department,
            asset_type
        ),
        daemon=True
    ).start()

# =========================
# OFFICE LICENSE
# =========================
def get_office_license():

    office_paths = [

        r'C:\\Program Files\\Microsoft Office\\Office16\\OSPP.VBS',

        r'C:\\Program Files (x86)\\Microsoft Office\\Office16\\OSPP.VBS',

        r'C:\\Program Files\\Microsoft Office\\root\\Office16\\OSPP.VBS',

        r'C:\\Program Files (x86)\\Microsoft Office\\root\\Office16\\OSPP.VBS'
    ]

    for path in office_paths:

        try:

            cmd = f'cscript //Nologo "{path}" /dstatus'

            result = subprocess.check_output(
                cmd,
                shell=True,
                text=True,
                encoding="utf-8",
                errors="ignore"
            )

            result_upper = result.upper()

            office_name = "Microsoft Office"

            for line in result.splitlines():

                if "LICENSE NAME" in line.upper():

                    office_name = line.split(":")[-1].strip()

                    break

            license_type = "Unknown"

            if "RETAIL" in result_upper:
                license_type = "Retail"

            elif "KMS" in result_upper:
                license_type = "KMS"

            elif "MAK" in result_upper:
                license_type = "MAK"

            elif "M365" in result_upper:
                license_type = "Microsoft 365"

            license_status = "Unknown"

            if "LICENSED" in result_upper:
                license_status = "Licensed"

            elif "NOTIFICATIONS" in result_upper:
                license_status = "Notification"

            elif "UNLICENSED" in result_upper:
                license_status = "Unlicensed"

            return (
                f"{office_name} | "
                f"{license_status} | "
                f"{license_type}"
            )

        except:
            pass

    return "Office không cài đặt"

# =========================
# SEND THREAD
# =========================
def send_data_thread(
    full_name,
    employee_code,
    department,
    asset_type
):

    try:

        machine_name = run_command([
            'powershell "(Get-CimInstance Win32_ComputerSystem).Model"',
            "wmic csproduct get name"
        ])

        serial_number = run_command([
            'powershell "(Get-CimInstance Win32_BIOS).SerialNumber"',
            "wmic bios get serialnumber"
        ])

        windows_key = run_command([
            'powershell "(Get-CimInstance SoftwareLicensingService).OA3xOriginalProductKey"',
            "wmic path softwarelicensingservice get OA3xOriginalProductKey"
        ])

        architecture = platform.machine()

        hostname = platform.node()

        try:
            windows_user = os.getlogin()
        except:
            windows_user = "Không xác định"

        try:
            ip_address = socket.gethostbyname(
                socket.gethostname()
            )
        except:
            ip_address = "Không xác định"

        office_license_status = get_office_license()

        ram_info = get_ram_info()

        cpu_info = get_cpu_info()

        disk_info = get_disk_info()

        data = {

            "full_name": full_name,

            "employee_code": employee_code,

            "department": department,

            "asset_type": asset_type,

            "machine_name": machine_name,

            "serial_number": serial_number,

            "windows_key": windows_key,

            "architecture": architecture,

            "hostname": hostname,

            "windows_user": windows_user,

            "ip_address": ip_address,

            "office_license": office_license_status,

            "ram_info": ram_info,

            "cpu_info": cpu_info,

            "disk_info": disk_info
        }

        response = requests.post(
            SERVER_URL,
            json=data,
            timeout=30
        )

        result = response.json()

        progress.stop()

        btn_submit.config(state="normal")

        if result["success"]:

            set_status(
                "Gửi dữ liệu thành công",
                "green"
            )

            messagebox.showinfo(
                "Thành công",
                "Dữ liệu đã được gửi thành công"
            )

            entry_name.delete(0, tk.END)

            entry_code.delete(0, tk.END)

            combo_department.set("")

            combo_asset.set("")

        else:

            set_status(
                result["message"],
                "red"
            )

            messagebox.showerror(
                "Lỗi",
                result["message"]
            )

    except Exception as e:

        progress.stop()

        btn_submit.config(state="normal")

        set_status(
            str(e),
            "red"
        )

        messagebox.showerror(
            "Lỗi",
            str(e)
        )

# =========================
# GUI
# =========================
root = tk.Tk()

root.title("AssetCheck")

root.geometry("520x620")

root.resizable(False, False)

# =========================
# STYLE
# =========================
style = ttk.Style()

style.theme_use("clam")

GREEN_COLOR = "#33CC33"

style.configure(
    "Header.TLabel",
    background=GREEN_COLOR,
    foreground="white",
    font=("Segoe UI", 12, "bold"),
    padding=10
)

style.configure(
    "Green.TButton",
    font=("Segoe UI", 11, "bold"),
    padding=12,
    foreground="white",
    background=GREEN_COLOR,
    borderwidth=0
)

style.map(
    "Green.TButton",
    background=[
        ("active", "#28a428"),
        ("disabled", "#bfbfbf")
    ]
)

# =========================
# MAIN FRAME
# =========================
main_frame = ttk.Frame(
    root,
    padding=25
)

main_frame.pack(
    fill="both",
    expand=True
)

# =========================
# TOP BUTTON
# =========================
top_frame = ttk.Frame(main_frame)

top_frame.pack(fill="x")

btn_check = ttk.Button(
    top_frame,
    text="Kiểm tra",
    command=check_system_info
)

btn_check.pack(anchor="e")

# =========================
# TITLE
# =========================
title_label = ttk.Label(
    main_frame,
    text="THÔNG TIN PHIÊN BẢN MÁY",
    style="Header.TLabel",
    anchor="center"
)

title_label.pack(
    fill="x",
    pady=(0, 20)
)

# =========================
# FULL NAME
# =========================
ttk.Label(
    main_frame,
    text="Họ và tên"
).pack(anchor="w")

entry_name = ttk.Entry(
    main_frame,
    width=50
)

entry_name.pack(
    pady=(5, 15)
)

# =========================
# EMPLOYEE CODE
# =========================
ttk.Label(
    main_frame,
    text="Mã số nhân viên"
).pack(anchor="w")

entry_code = ttk.Entry(
    main_frame,
    width=50
)

entry_code.pack(
    pady=(5, 15)
)

# =========================
# DEPARTMENT
# =========================
ttk.Label(
    main_frame,
    text="Bộ phận"
).pack(anchor="w")

combo_department = ttk.Combobox(
    main_frame,
    values=DEPARTMENTS,
    state="readonly",
    width=47
)

combo_department.pack(
    pady=(5, 15)
)

# =========================
# ASSET TYPE
# =========================
ttk.Label(
    main_frame,
    text="Loại tài sản"
).pack(anchor="w")

combo_asset = ttk.Combobox(
    main_frame,
    values=ASSET_TYPES,
    state="readonly",
    width=47
)

combo_asset.pack(
    pady=(5, 20)
)

# =========================
# PROGRESS
# =========================
progress = ttk.Progressbar(
    main_frame,
    mode="indeterminate",
    length=200
)

progress.pack(
    fill="x",
    pady=(0, 15)
)

# =========================
# SUBMIT BUTTON
# =========================
btn_submit = ttk.Button(
    main_frame,
    text="Gửi THÔNG TIN",
    style="Green.TButton",
    command=submit_data
)

btn_submit.pack(
    fill="x",
    pady=10
)

# =========================
# STATUS
# =========================
status_label = ttk.Label(
    main_frame,
    text="Sẵn sàng",
    font=("Segoe UI", 9),
    wraplength=420,
    justify="left"
)

status_label.pack(
    pady=(20, 0),
    fill="x",
    anchor="w"
)

# =========================
# CREDIT
# =========================
dev_label = ttk.Label(
    main_frame,
    text="@Hồ Quốc Thăng",
    font=("Segoe UI", 7, "italic"),
    foreground="gray"
)

dev_label.pack(
    pady=(15, 0),
    fill="x",
    anchor="e"
)

root.mainloop()

