import numpy as np
import cv2 as cv
from PSO import *

# Helper function to compute histogram for a single channel
def compute_channel_histogram(channel_data, color, ax):
    ax.hist(channel_data.flatten().ravel(), color=color, bins=256)

# Function to show histogram of all 3 channels
def color_hist(img):
    y = np.linspace(0, 256)
    fig, ax = plt.subplots(3, 1)
    compute_channel_histogram(img[:, :, 0], 'blue', ax[0])
    compute_channel_histogram(img[:, :, 1], 'green', ax[1])
    compute_channel_histogram(img[:, :, 2], 'red', ax[2])
    plt.show()

# Helper function to assign channel data
def assign_channel_data(val, channel_type):
    for p in range(len(val)):
        if val[p][1] == channel_type:
            return val[p][0]
    return None

# Stacking BGR channels in order after computation
def image(input):
    val = list(input)
    b = assign_channel_data(val, "B")
    g = assign_channel_data(val, "G")
    r = assign_channel_data(val, "R")
    stacked_channels = [b, g, r]
    img = np.dstack(stacked_channels)
    img = np.array(img, dtype=np.uint8)
    return img

# Helper function to compute mean of channel
def compute_channel_mean(channel):
    return np.mean(channel)

# Indicating superior, inferior, and intermediate channels
def superior_inferior_split(img):
    B, G, R = cv.split(img)
    pixel_means = {
        "B": compute_channel_mean(B),
        "G": compute_channel_mean(G),
        "R": compute_channel_mean(R)
    }
    pixel_ordered = dict(sorted(pixel_means.items(), key=lambda x: x[1], reverse=True))
    label = ["Pmax", "Pint", "Pmin"]
    chanel = {}
    for i, j in zip(range(len(label)), pixel_ordered.keys()):
        if j == "B":
            chanel[label[i]] = [B, j]
        elif j == "G":
            chanel[label[i]] = [G, j]
        else:
            chanel[label[i]] = [R, j]
    return chanel

# Helper function to compute adaptive gain factor
def compute_adaptive_gain(Pmax, Pother):
    sum_max = np.sum(Pmax)
    sum_other = np.sum(Pother)
    gain = (sum_max - sum_other) / (sum_max + sum_other + 1e-10)
    return np.clip(gain * np.log1p(sum_max / (sum_other + 1e-10)), 0, 1)

# Neutralize image function
def neutralize_image(img):
    track = superior_inferior_split(img)
    Pmax = track["Pmax"][0]
    Pint = track["Pint"][0]
    Pmin = track["Pmin"][0]
    J = compute_adaptive_gain(Pmax, Pint)
    K = compute_adaptive_gain(Pmax, Pmin)
    adjusted_pint = Pint + (J * Pmax)
    adjusted_pmin = Pmin + (K * Pmax)
    track["Pint"][0] = np.clip(adjusted_pint, 0, 255)
    track["Pmin"][0] = np.clip(adjusted_pmin, 0, 255)
    neu_img = image(track.values())
    return neu_img

# Helper function for adaptive stretching
def compute_adaptive_stretch(value, min_P, max_P, avg_point, is_lower):
    if is_lower:
        scale_factor = (255 - min_P) / (avg_point - min_P + 1e-10)
        stretched = (value - min_P) * scale_factor + min_P
        return np.clip(int(stretched), 0, 255)
    else:
        scale_factor = 255 / (max_P - avg_point + 1e-10)
        stretched = (value - avg_point) * scale_factor
        return np.clip(int(stretched), 0, 255)

# Stretching function with adaptive histogram
def Stretching(image):
    LSR_img = []
    USR_img = []
    height, width = image.shape[:2]

    for i in range(image.shape[2]):
        img_hist = image[:, :, i]
        max_P = np.max(img_hist)
        min_P = np.min(img_hist)
        mean_P = np.mean(img_hist)
        median_P = np.median(img_hist)
        avg_point = (mean_P + median_P) / 2

        LS_img = np.zeros((height, width))
        US_img = np.zeros((height, width))

        for i in range(height):
            for j in range(width):
                pixel = img_hist[i][j]
                if pixel < avg_point:
                    LS_img[i][j] = compute_adaptive_stretch(pixel, min_P, max_P, avg_point, True)
                    US_img[i][j] = 0
                else:
                    LS_img[i][j] = 255
                    US_img[i][j] = compute_adaptive_stretch(pixel, min_P, max_P, avg_point, False)

        LSR_img.append(LS_img)
        USR_img.append(US_img)

    LS = np.array(np.dstack(LSR_img), dtype=np.uint8)
    US = np.array(np.dstack(USR_img), dtype=np.uint8)
    return LS, US

# Helper function to combine channels
def combine_channel_data(ch1, ch2):
    combined = np.add(ch1 / 2, ch2 / 2)
    return np.clip(np.array(combined, dtype=np.uint8), 0, 255)

# Enhanced image function
def enhanced_image(img1, img2):
    b1, g1, r1 = cv.split(img1)
    b2, g2, r2 = cv.split(img2)
    height, width = img1.shape[:2]

    dual_img = np.zeros((height, width, 3), dtype=np.uint8)
    dual_img[:, :, 0] = combine_channel_data(b1, b2)
    dual_img[:, :, 1] = combine_channel_data(g1, g2)
    dual_img[:, :, 2] = combine_channel_data(r1, r2)

    return dual_img

# PSO-based image enhancement
def pso_image(img):
    group = superior_inferior_split(img)
    maxi = np.mean(group["Pmax"][0])
    inte = np.mean(group["Pint"][0])
    mini = np.mean(group["Pmin"][0])

    n = 100
    params = {"wmax": 0.95, "wmin": 0.35, "c1": 1.5, "c2": 2.5}
    max_iteration = 150
    x = np.array([inte, mini])

    def func(X, P_sup=maxi):
        term1 = np.square(P_sup - X[0])
        term2 = np.square(P_sup - X[1])
        return term1 + term2

    nVar = 2
    VarMin = 0
    VarMax = 255

    gbest = pso(func, max_iter=max_iteration, num_particles=n, dim=2, vmin=VarMin, vmax=VarMax, params=params)

    mean_colors = gbest['position']
    gamma1 = np.log(mean_colors[0] / 255 + 1e-10) / np.log(x[0] / 255 + 1e-10)
    gamma2 = np.log(mean_colors[1] / 255 + 1e-10) / np.log(x[1] / 255 + 1e-10)
    gamma = np.array([gamma1, gamma2])

    pint_data = group["Pint"][0] / 255
    pmin_data = group["Pmin"][0] / 255
    group["Pint"][0] = np.clip(np.array(255 * np.power(pint_data, gamma[0])), 0, 255)
    group["Pmin"][0] = np.clip(np.array(255 * np.power(pmin_data, gamma[1])), 0, 255)

    pso_res = image(group.values())
    return pso_res

# Helper function for bilateral filtering
def apply_bilateral_filter(img):
    return cv.bilateralFilter(img, d=5, sigmaColor=25, sigmaSpace=25)

# Helper function for Gaussian blur
def apply_gaussian_blur(img):
    return cv.GaussianBlur(img, (3, 3), sigmaX=0.8)  # Reduced sigma for subtler blur

# Unsharp masking with noise reduction
def unsharp_masking(img):
    # Step 1: Apply bilateral filter for noise reduction
    denoised_img = apply_bilateral_filter(img)
    
    # Step 2: Apply Gaussian blur for unsharp masking
    alpha = 0.15  # Reduced for less aggressive sharpening
    beta = 1 - alpha
    img_blur = apply_gaussian_blur(denoised_img)
    
    # Step 3: Combine images with weighted addition
    weighted_img = cv.addWeighted(denoised_img, alpha, img_blur, beta, 0.0)
    
    # Step 4: Clip and convert to uint8
    unsharp_img = np.clip(weighted_img, 0, 255)
    return unsharp_img.astype(np.uint8)

# Helper function for CLAHE
def apply_clahe(img):
    lab = cv.cvtColor(img, cv.COLOR_BGR2LAB)
    l, a, b = cv.split(lab)
    clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l.astype(np.uint8))
    lab = cv.merge((l, a, b))
    return cv.cvtColor(lab, cv.COLOR_LAB2BGR)

# NUCE pipeline
def NUCE(img):
    """
    NUCE pipeline for image enhancement.
    
    Args:
        img (numpy.ndarray): Input image in BGR format.
    
    Returns:
        numpy.ndarray: Enhanced image.
    """
    neu_img = neutralize_image(img)
    img1, img2 = Stretching(neu_img)
    dual_img = enhanced_image(img1, img2)
    pso_res = pso_image(dual_img)
    nuce_img = unsharp_masking(pso_res)
    final_img = apply_clahe(nuce_img)
    return final_img


def process_video_with_nuce(video_path, output_path, update_progress=lambda x: None):
    cap = cv.VideoCapture(video_path)
    total = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv.CAP_PROP_FPS)
    width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv.VideoWriter_fourcc(*'mp4v')
    out = cv.VideoWriter(output_path, fourcc, fps, (width, height))

    current = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        processed_frame = NUCE(frame)
        out.write(processed_frame)

        current += 1
        update_progress((current / total) * 100)

        # نوار پیشرفت ترمینالی ساده
        progress = int((current / total) * 50)
        print(f"\rپیشرفت: [{'█' * progress}{'░' * (50 - progress)}] {current}/{total}", end='')

    cap.release()
    out.release()
    print("\n✅ ویدیو با موفقیت پردازش شد.")

