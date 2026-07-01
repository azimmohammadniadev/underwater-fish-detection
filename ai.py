import os
import shutil
import torch
import cv2
from tkinter import Tk, Button, Label, filedialog, messagebox, Frame

# ---------------------------------------------------------
# بارگذاری مدل YOLOv5
# ---------------------------------------------------------
model = torch.hub.load('ultralytics/yolov5', 'custom',
                       path='weights/larg-fish-detector.pt',
                       source='github')

input_folder = "img"
output_folder = "OD-results"
os.makedirs(input_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)


# ---------------------------------------------------------
# انتخاب فایل‌ها
# ---------------------------------------------------------
def select_files():
    file_paths = filedialog.askopenfilenames(
        title="انتخاب عکس یا ویدئو",
        filetypes=[("Image and Video Files", "*.png *.jpg *.jpeg *.gif *.mp4 *.avi *.mov *.mkv")]
    )
    if file_paths:
        for file_path in file_paths:
            try:
                shutil.copy(file_path, input_folder)
                messagebox.showinfo("عملیات موفق", f"{os.path.basename(file_path)} اضافه شد.")
            except Exception as e:
                messagebox.showerror("خطا", f"کپی فایل ناموفق بود: {e}")


# ---------------------------------------------------------
# پاک‌سازی پوشه ورودی
# ---------------------------------------------------------
def clear_input_folder():
    try:
        for item in os.listdir(input_folder):
            item_path = os.path.join(input_folder, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        messagebox.showinfo("✅", "پوشه img پاک شد.")
    except Exception as e:
        messagebox.showerror("خطا", f"خطا در پاک‌سازی: {e}")


# ---------------------------------------------------------
# پردازش ویدئو و ذخیره به شکل ویدئوی خروجی
# ---------------------------------------------------------
def process_video(video_path):
    cap = cv2.VideoCapture(video_path)
    video_name = os.path.splitext(os.path.basename(video_path))[0]

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # فرمت خروجی فایل ویدئو
    fps = cap.get(cv2.CAP_PROP_FPS) or 25     # نرخ فریم ویدئوی خروجی
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    output_video_path = os.path.join(output_folder, f"{video_name}_detected.mp4")
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame_count += 1

        # پردازش هر فریم با YOLO
        results = model(frame, size=640)
        # رسم باکس‌ها مستقیم روی فریم
        annotated_frame = results.render()[0]

        out.write(annotated_frame)
        print(f"Frame {frame_count} processed for video {video_name}")

    cap.release()
    out.release()

    print(f"✅ ویدئوی خروجی ساخته شد: {output_video_path}")


# ---------------------------------------------------------
# شروع تشخیص (پردازش عکس و ویدئو)
# ---------------------------------------------------------
def start_detection():
    if not os.listdir(input_folder):
        messagebox.showwarning("توجه", "پوشه img خالی است.")
        return

    messagebox.showinfo("⏳", "در حال تشخیص ماهی — لطفاً منتظر بمانید...")

    # پاک کردن خروجی قبلی
    for item in os.listdir(output_folder):
        item_path = os.path.join(output_folder, item)
        if os.path.isfile(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)

    # پردازش فایل‌ها
    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)
        if not os.path.isfile(file_path):
            continue

        try:
            if filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                process_video(file_path)
            else:
                results = model(file_path, size=640)
                results.save(save_dir=output_folder)
                print(f"📸 Processed image: {filename}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    messagebox.showinfo("✅ پایان کار", "پردازش کامل شد. نتایج در پوشه OD-results ذخیره شدند.")


# ---------------------------------------------------------
# باز کردن پوشه خروجی
# ---------------------------------------------------------
def open_results_folder():
    try:
        os.startfile(output_folder)
    except AttributeError:
        try:
            import subprocess
            subprocess.Popen(['open', output_folder])
        except:
            messagebox.showerror("خطا", "نمی‌توان پوشه خروجی را باز کرد.")
    except Exception as e:
        messagebox.showerror("خطا", f"{e}")


# ---------------------------------------------------------
# پاکسازی پوشه خروجی
# ---------------------------------------------------------
def clear_output_folder():
    try:
        for item in os.listdir(output_folder):
            item_path = os.path.join(output_folder, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        messagebox.showinfo("پاک‌سازی", "پوشه OD-results پاک شد.")
    except Exception as e:
        messagebox.showerror("خطا", f"{e}")


# ---------------------------------------------------------
# رابط گرافیکی
# ---------------------------------------------------------
root = Tk()
root.title("نرم افزار تشخیص ماهی - YOLOv5")
root.geometry("550x420")
root.configure(bg="#d3d3d3")

header_label = Label(
    root,
    text="تشخیص ماهی با YOLOv5 (تصویر + ویدئو خروجی)",
    font=("Tahoma", 14, "bold"),
    bg="#d3d3d3",
    fg="#003366"
)
header_label.pack(pady=20)

frame1 = Frame(root, bg="#d3d3d3")
frame1.pack(pady=10)

Button(frame1, text="انتخاب فایل‌ها", command=select_files, width=20, height=2,
       bg="#FFA500", fg="white", font=("Tahoma", 10)).pack(side="left", padx=5)

Button(frame1, text="پاک‌سازی پوشه ورودی", command=clear_input_folder, width=18, height=2,
       bg="#FF6347", fg="white", font=("Tahoma", 10)).pack(side="left", padx=5)

Button(root, text="🎬 شروع عملیات تشخیص (تصویر + ویدئو نهایی)", command=start_detection,
       width=40, height=2, bg="#4682B4", fg="white", font=("Tahoma", 10)).pack(pady=20)

frame2 = Frame(root, bg="#d3d3d3")
frame2.pack(pady=10)

Button(frame2, text="مشاهده خروجی‌ها", command=open_results_folder, width=20, height=2,
       bg="#4682B4", fg="white", font=("Tahoma", 10)).pack(side="left", padx=5)

Button(frame2, text="پاک‌سازی خروجی‌ها", command=clear_output_folder, width=18, height=2,
       bg="#FF6347", fg="white", font=("Tahoma", 10)).pack(side="left", padx=5)

root.mainloop()
