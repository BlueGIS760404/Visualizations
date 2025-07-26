import os
from PIL import Image
import numpy as np

def combine_images(img_paths, large_index=0, orientation='portrait', save_path="combined_image.jpg"):
    DPI = 300
    A4_MM = (210, 297)
    A4_SIZE = (
        int(A4_MM[0] * DPI / 25.4),
        int(A4_MM[1] * DPI / 25.4)
    ) if orientation == 'portrait' else (
        int(A4_MM[1] * DPI / 25.4),
        int(A4_MM[0] * DPI / 25.4)
    )

    MARGIN = int(DPI * 0.8)  # Approximately 1.5 cm (0.508 cm + 1 cm)
    PADDING = int(DPI * 0.1)

    if len(img_paths) != 4:
        raise ValueError("Exactly 4 image paths required.")
    if not all(os.path.isfile(p) for p in img_paths):
        raise FileNotFoundError("Invalid image path(s) detected.")
    if not 0 <= large_index < 4:
        raise IndexError("large_index must be 0-3.")
    if orientation not in ['landscape', 'portrait']:
        raise ValueError("Orientation must be 'landscape' or 'portrait'.")

    try:
        resample_mode = Image.Resampling.LANCZOS
    except AttributeError:
        resample_mode = Image.LANCZOS

    images = [Image.open(p) for p in img_paths]
    large_img = images[large_index]
    small_imgs = [img for i, img in enumerate(images) if i != large_index]

    if orientation == 'portrait':
        # Vertical: Large on top, 3 small below
        total_small_width = sum(img.width for img in small_imgs)
        total_small_height = max(img.height for img in small_imgs)
        available_height = A4_SIZE[1] - 2 * MARGIN - PADDING
        available_width = A4_SIZE[0] - 2 * MARGIN

        # Estimate scale to fit vertically
        large_h = large_img.height
        small_h = max(img.height for img in small_imgs)
        total_h = 1.5 * large_h + small_h + PADDING
        scale = min(available_height / total_h, available_width / max(large_img.width, total_small_width / 3))
    else:
        # Horizontal: Large on left, 3 small stacked right
        total_small_height = sum(img.height for img in small_imgs)
        available_width = A4_SIZE[0] - 2 * MARGIN - PADDING
        available_height = A4_SIZE[1] - 2 * MARGIN

        large_w = large_img.width
        small_w = max(img.width for img in small_imgs)
        total_w = 1.5 * large_w + small_w + PADDING
        scale = min(available_width / total_w, available_height / max(large_img.height, total_small_height / 3))

    # Resize all images
    resized_images = []
    for i in range(4):
        factor = 1.5 * scale if i == large_index else scale
        new_size = (int(images[i].width * factor), int(images[i].height * factor))
        resized_images.append(images[i].resize(new_size, resample=resample_mode))

    canvas = Image.new("RGB", A4_SIZE, color=(255, 255, 255))

    if orientation == 'portrait':
        y = MARGIN
        large_resized = resized_images[large_index]
        x = (A4_SIZE[0] - large_resized.width) // 2
        canvas.paste(large_resized, (x, y))
        y += large_resized.height + PADDING

        smalls = [img for i, img in enumerate(resized_images) if i != large_index]
        total_small_width = sum(img.width for img in smalls) + 2 * PADDING
        x = (A4_SIZE[0] - total_small_width) // 2
        for img in smalls:
            canvas.paste(img, (x, y))
            x += img.width + PADDING

    else:
        x = MARGIN
        large_resized = resized_images[large_index]
        y = (A4_SIZE[1] - large_resized.height) // 2
        canvas.paste(large_resized, (x, y))
        x += large_resized.width + PADDING

        smalls = [img for i, img in enumerate(resized_images) if i != large_index]
        total_small_height = sum(img.height for img in smalls) + 2 * PADDING
        y = (A4_SIZE[1] - total_small_height) // 2
        for img in smalls:
            canvas.paste(img, (x, y))
            y += img.height + PADDING

    canvas.save(save_path, dpi=(DPI, DPI), quality=95, subsampling=0)
    print(f"✅ Collage saved to {save_path} with A4-safe layout ({A4_SIZE[0]}x{A4_SIZE[1]} px)")

if __name__ == "__main__":
    image_paths = [
        r"C:\Users\Reza\accessibility_map_roads.png",
        r"C:\Users\Reza\accessibility_map_metro.png",
        r"C:\Users\Reza\accessibility_map_bus.png",
        r"C:\Users\Reza\composite_accessibility_map.png"
    ]

    layout = "landscape"       # or "portrait"
    large_index = 3            # index of image to make larger
    output_path = "final_collage.jpg"

    try:
        combine_images(image_paths, large_index, layout, output_path)
    except Exception as e:
        print(f"❌ Error: {e}")
