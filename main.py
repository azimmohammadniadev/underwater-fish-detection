import os
import sys
import cv2 as cv
from utility import NUCE, process_video_with_nuce

# مسیر ورودی به صورت آرگومان (مثلاً images یا videos)
input_folder = sys.argv[1] if len(sys.argv) > 1 else "images"
ext_image = [".jpg", ".jpeg", ".png"]
ext_video = [".mp4", ".avi"]

# اطمینان از وجود پوشه خروجی
if not os.path.exists("results"):
    os.makedirs("results")

# پردازش فایل‌ها داخل پوشه ورودی
for filename in os.listdir(input_folder):
    file_path = os.path.join(input_folder, filename)
    ext = os.path.splitext(filename)[1].lower()

    if ext in ext_image:
        print(f"🖼 پردازش تصویر: {filename}")
        img = cv.imread(file_path, 1)
        if img is None:
            print("⚠ تصویر بارگذاری نشد.")
            continue
        result = NUCE(img)
        output_path = os.path.join("results", filename)
        cv.imwrite(output_path, result)
        print(f"✅ ذخیره شد: {output_path}")

    elif ext in ext_video:
        print(f"\n🎞 پردازش ویدیو: {filename}")
        output_path = os.path.join("results", f"processed_{filename}")
        process_video_with_nuce(file_path, output_path, update_progress=lambda x: None)
        print(f"\n✅ خروجی ویدیو ذخیره شد: {output_path}")

    else:
        print(f"❌ فرمت پشتیبانی نمی‌شود: {filename}")