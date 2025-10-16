import os
from PIL import Image

def combine_images_equal(img_paths, save_path="combined_image_5_landscape.jpg"):
    DPI = 300
    A4_MM = (210, 297)  # A4 paper in millimeters (height, width)
    A4_SIZE = (
        int(A4_MM[1] * DPI / 25.4),  # width (landscape)
        int(A4_MM[0] * DPI / 25.4)   # height
    )

    MARGIN = int(DPI * 0.6)   # ~1.5 cm margins
    PADDING = int(DPI * 0.2)  # spacing between images (~0.5 cm)

    if len(img_paths) != 5:
        raise ValueError("Exactly 5 image paths are required.")
    if not all(os.path.isfile(p) for p in img_paths):
        raise FileNotFoundError("One or more image paths are invalid.")

    try:
        resample_mode = Image.Resampling.LANCZOS
    except AttributeError:
        resample_mode = Image.LANCZOS

    images = [Image.open(p) for p in img_paths]

    # Define grid layout (2 rows: 2 on top, 3 on bottom)
    rows = 2
    cols_top = 2
    cols_bottom = 3

    # Available area
    available_width = A4_SIZE[0] - 2 * MARGIN
    available_height = A4_SIZE[1] - 2 * MARGIN

    # Divide available height between two rows (equal row heights)
    row_height = (available_height - PADDING) / rows

    # Determine image size (same for all)
    # We'll make width of top images slightly larger because there are fewer columns
    # Compute smallest scale to ensure fit
    width_top = (available_width - (cols_top - 1) * PADDING) / cols_top
    width_bottom = (available_width - (cols_bottom - 1) * PADDING) / cols_bottom
    img_width = min(width_top, width_bottom)
    img_height = row_height

    # Resize all images equally
    resized_images = []
    for img in images:
        img_ratio = img.width / img.height
        # Adjust size preserving aspect ratio
        if img_ratio > img_width / img_height:
            new_width = int(img_width)
            new_height = int(img_width / img_ratio)
        else:
            new_height = int(img_height)
            new_width = int(img_height * img_ratio)
        resized_images.append(img.resize((new_width, new_height), resample=resample_mode))

    # Create white canvas
    canvas = Image.new("RGB", A4_SIZE, color=(255, 255, 255))

    # --- Place images ---
    y = MARGIN
    x_start = MARGIN

    # Top row (2 images)
    top_imgs = resized_images[:2]
    total_width_top = sum(img.width for img in top_imgs) + PADDING
    x = (A4_SIZE[0] - total_width_top) // 2
    for img in top_imgs:
        y_offset = (row_height - img.height) / 2
        canvas.paste(img, (int(x), int(y + y_offset)))
        x += img.width + PADDING

    # Bottom row (3 images)
    bottom_imgs = resized_images[2:]
    y += row_height + PADDING
    total_width_bottom = sum(img.width for img in bottom_imgs) + 2 * PADDING
    x = (A4_SIZE[0] - total_width_bottom) // 2
    for img in bottom_imgs:
        y_offset = (row_height - img.height) / 2
        canvas.paste(img, (int(x), int(y + y_offset)))
        x += img.width + PADDING

    # Save
    canvas.save(save_path, dpi=(DPI, DPI), quality=95, subsampling=0)
    print(f"✅ 5-image collage saved to {save_path} ({A4_SIZE[0]}x{A4_SIZE[1]} px)")

if __name__ == "__main__":
    image_paths = [
        r"C:\Users\Reza\img1.png",
        r"C:\Users\Reza\img2.png",
        r"C:\Users\Reza\img3.png",
        r"C:\Users\Reza\img4.png",
        r"C:\Users\Reza\img5.png"
    ]

    output_path = "final_5image_landscape_collage.jpg"
    combine_images_equal(image_paths, output_path)
