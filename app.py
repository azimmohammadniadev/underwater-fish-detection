import tkinter as tk
from tkinter import messagebox, filedialog
import subprocess
import os
import shutil

# Default folder paths
DEFAULT_FOLDER_PATH = "images"
DEFAULT_FOLDER_PATH2 = "results"

# Security credentials
PASSWORD = "1234"
SECURITY_QUESTION = "کلمه اضطراری را وارد کنید :"
SECURITY_ANSWER = "blue"

# Helper function to create a button
def create_button(parent, text, command, bg, fg, width, font):
    return tk.Button(parent, text=text, command=command, bg=bg, fg=fg, width=width, font=font)

# Function to select and copy image file
def select_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    if file_path:
        try:
            dest_path = os.path.join(DEFAULT_FOLDER_PATH, os.path.basename(file_path))
            shutil.copy(file_path, dest_path)
            messagebox.showinfo("Success", "Image copied to images folder")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy image: {str(e)}")

# Function to open results folder
def open_results_folder():
    try:
        os.startfile(DEFAULT_FOLDER_PATH2)
    except FileNotFoundError:
        messagebox.showerror("Error", "Results folder not found. Please process images first.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open results folder: {str(e)}")

# Function to run the main script with negative state option
def run_processing_script(apply_negative_var):
    try:
        # ارسال مسیر پوشه تصاویر به main.py
        subprocess.Popen(["python", "main.py", "images"])
        messagebox.showinfo("Processing", "پردازش تصاویر شروع شد. نتایج در پوشه results ذخیره می‌شوند.")
    except FileNotFoundError:
        messagebox.showerror("Error", "main.py یافت نشد. مطمئن شوید فایل در مسیر پروژه قرار دارد.")
    except Exception as e:
        messagebox.showerror("Error", f"خطا در اجرای پردازش: {str(e)}")

def run_ai():
    try:
        # اجرای test.py با پایتون
        subprocess.Popen(["python", "ai.py"])
        messagebox.showinfo("اجرای تست", "فایل ai.py با موفقیت اجرا شد.")
    except FileNotFoundError:
        messagebox.showerror("خطا", "فایل ai.py  یافت نشد. مطمئن شوید فایل در مسیر پروژه وجود دارد.")
    except Exception as e:
        messagebox.showerror("خطا", f"خطا در اجرای ai.py : {str(e)}")


# Function to validate password reset
def validate_reset_inputs(security_answer, new_password, confirm_password):
    if security_answer != SECURITY_ANSWER:
        messagebox.showerror("Password Reset Failed", "Incorrect security answer")
        return False
    if new_password != confirm_password:
        messagebox.showerror("Password Reset Failed", "Passwords do not match")
        return False
    return True

# Function to handle password reset
def handle_password_reset():
    global PASSWORD
    security_answer = entry_security_answer.get()
    new_password = entry_new_password.get()
    confirm_password = entry_confirm_password.get()
    if validate_reset_inputs(security_answer, new_password, confirm_password):
        PASSWORD = new_password
        messagebox.showinfo("Password Reset", "Password reset successful")
        reset_window.destroy()

def select_video():
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi")])
    if file_path:
        try:
            dest_path = os.path.join("videos", os.path.basename(file_path))
            shutil.copy(file_path, dest_path)
            messagebox.showinfo("Success", "ویدیو در پوشه videos ذخیره شد.")
        except Exception as e:
            messagebox.showerror("Error", f"خطا در کپی ویدیو: {str(e)}")

def run_video_processing():
    try:
        subprocess.Popen(["python", "main.py", "videos"])
        messagebox.showinfo("Processing", "پردازش ویدیو شروع شد.")
    except Exception as e:
        messagebox.showerror("Error", f"خطا در پردازش ویدیو: {str(e)}")

# Function to open reset password window
def open_reset_window():
    global reset_window, entry_security_answer, entry_new_password, entry_confirm_password
    reset_window = tk.Toplevel(login_window)
    reset_window.title("Reset Password")
    reset_window.geometry("500x400")
    reset_window.configure(background='gray')

    tk.Label(reset_window, text=SECURITY_QUESTION, font=("Arial", 12), fg="black", bg="white").pack(pady=5)
    entry_security_answer = tk.Entry(reset_window, show="*", font=("Arial", 12))
    entry_security_answer.pack(pady=5)

    tk.Label(reset_window, text="رمز عبور جدید:", font=("Arial", 12), fg="black", bg="white").pack(pady=5)
    entry_new_password = tk.Entry(reset_window, show="*", font=("Arial", 12))
    entry_new_password.pack(pady=5)

    tk.Label(reset_window, text="تایید رمز عبور :", font=("Arial", 12), fg="black", bg="white").pack(pady=5)
    entry_confirm_password = tk.Entry(reset_window, show="*", font=("Arial", 12))
    entry_confirm_password.pack(pady=5)

    create_button(
        reset_window, "تایید", handle_password_reset, "skyblue", "black", None, ("Arial", 12, "bold")
    ).pack(pady=5)

# Function to validate login
def validate_login():
    password = entry_password.get()
    if password == PASSWORD:
        open_main_window()
        login_window.destroy()
    else:
        messagebox.showerror("Login Failed", "Invalid password")

# Function to open main window
def open_main_window():
    main_window = tk.Tk()
    main_window.title("نرم افزار افزایش کیفیت تصویر از بستر دریا")
    main_window.geometry("800x500")
    main_window.configure(background='gray')

    tk.Label(
        main_window, text="نرم افزار افزایش کیفیت تصویر از بستر دریا", 
        font=("Arial", 28, "bold"), fg="black", bg="white"
    ).pack(pady=20)

    create_button(
        main_window, "بارگذاری تصویر", select_image, "skyblue", "black", 20, ("Arial", 16, "bold")
    ).pack(pady=10)

    # دکمه بارگذاری ویدیو
    create_button(
    main_window, "بارگذاری ویدیو", select_video, "skyblue", "black", 20, ("Arial", 16, "bold")
    ).pack(pady=10)

    # هوش مصنوعی تشخیص ماهی
    create_button(
    main_window, "هوش مصنوعی تشخیص ماهی", run_ai, "skyblue", "black", 20, ("Arial", 16, "bold")
    ).pack(pady=10)

    # دکمه شروع پردازش ویدیو
    create_button(
    main_window, "شروع عملیات ویدیو", run_video_processing, "orange", "black", 20, ("Arial", 16, "bold")
    ).pack(pady=10)

    # Checkbox for negative state
    apply_negative_var = tk.BooleanVar()
    tk.Checkbutton(
        main_window, text="اعمال حالت منفی", variable=apply_negative_var, font=("Arial", 12), bg="gray"
    ).pack(pady=5)

    create_button(
        main_window, "شروع عملیات", lambda: run_processing_script(apply_negative_var), "orange", "black", 20, ("Arial", 16, "bold")
    ).pack(pady=10)

    create_button(
        main_window, "مشاهده خروجی", open_results_folder, "skyblue", "black", 20, ("Arial", 16, "bold")
    ).pack(pady=10)

    main_window.mainloop()

# Create login window
login_window = tk.Tk()
login_window.title("Login")
login_window.geometry("800x500")
login_window.configure(background='gray')

tk.Label(login_window, text="رمز عبور را وارد کنید:", font=("Arial", 16), fg="black", bg="white").pack(pady=10)
entry_password = tk.Entry(login_window, show="*", font=("Arial", 16))
entry_password.pack(pady=10)

create_button(
    login_window, "ورود", validate_login, "skyblue", "black", None, ("Arial", 16, "bold")
).pack(pady=10)

create_button(
    login_window, "فراموشی رمز عبور", open_reset_window, "white", "black", None, ("Arial", 12)
).pack(pady=5)

# Ensure default folders exist
os.makedirs(DEFAULT_FOLDER_PATH, exist_ok=True)
os.makedirs(DEFAULT_FOLDER_PATH2, exist_ok=True)

login_window.mainloop()