import os
from PIL import Image, ImageChops

def combine_images_equal(img_paths, save_path="combined_image_5_landscape.jpg"):
    DPI = 300
    A4_MM = (210, 297)  # A4 paper in millimeters (height, width)
    A4_SIZE = (
        int(A4_MM[1] * DPI / 25.4),  # width (landscape)
        int(A4_MM[0] * DPI / 25.4)   # height
    )

    MARGIN = int(DPI * 0.5)           # Reduced margins (~1.27 cm)
    VERTICAL_PADDING = int(DPI * 0.2) # Vertical spacing between rows (~1 cm)
    HORIZONTAL_PADDING = int(DPI * 0.2)  # Spacing between images in same row (~0.5 cm)

    if len(img_paths) != 5:
        raise ValueError("Exactly 5 image paths are required.")
    if not all(os.path.isfile(p) for p in img_paths):
        raise FileNotFoundError("One or more image paths are invalid.")

    try:
        resample_mode = Image.Resampling.LANCZOS
    except AttributeError:
        resample_mode = Image.LANCZOS

    images = [Image.open(p) for p in img_paths]

    # Define grid layout: 2 top, 2 bottom, 1 center
    rows = 3
    cols_top = 2
    cols_bottom = 2

    # Available area
    available_width = A4_SIZE[0] - 2 * MARGIN
    available_height = A4_SIZE[1] - 2 * MARGIN

    # Divide available height for 3 rows (top, center, bottom)
    total_image_height = available_height * 0.8
    row_height = total_image_height / 3

    # Determine image size (same for all)
    width_top = (available_width - (cols_top - 1) * HORIZONTAL_PADDING) / cols_top
    width_bottom = (available_width - (cols_bottom - 1) * HORIZONTAL_PADDING) / cols_bottom
    img_width = min(width_top, width_bottom)
    img_height = row_height

    # Resize all images equally
    resized_images = []
    for img in images:
        img_ratio = img.width / img.height
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

    # Top row (2 images)
    top_imgs = resized_images[:2]
    total_width_top = sum(img.width for img in top_imgs) + HORIZONTAL_PADDING
    x = (A4_SIZE[0] - total_width_top) // 2
    for img in top_imgs:
        y_offset = (row_height - img.height) / 2
        canvas.paste(img, (int(x), int(y + y_offset)))
        x += img.width + HORIZONTAL_PADDING

    # Center image (5th image)
    center_img = resized_images[4]
    y += row_height + VERTICAL_PADDING
    x_center = (A4_SIZE[0] - center_img.width) // 2
    y_center_offset = (row_height - center_img.height) / 2
    canvas.paste(center_img, (int(x_center), int(y + y_center_offset)))

    # Bottom row (2 images)
    bottom_imgs = resized_images[2:4]
    y += row_height + VERTICAL_PADDING
    total_width_bottom = sum(img.width for img in bottom_imgs) + HORIZONTAL_PADDING
    x = (A4_SIZE[0] - total_width_bottom) // 2
    for img in bottom_imgs:
        y_offset = (row_height - img.height) / 2
        canvas.paste(img, (int(x), int(y + y_offset)))
        x += img.width + HORIZONTAL_PADDING

    # --- Auto-crop extra white borders ---
    bg = Image.new(canvas.mode, canvas.size, (255, 255, 255))
    diff = ImageChops.difference(canvas, bg)
    bbox = diff.getbbox()
    if bbox:
        canvas = canvas.crop(bbox)

    # Save cropped result
    canvas.save(save_path, dpi=(DPI, DPI), quality=95, subsampling=0)
    print(f"✅ 5-image collage (2x2+1 center layout) saved to {save_path} ({canvas.size[0]}x{canvas.size[1]} px)")

if __name__ == "__main__":
    image_paths = [
        r"E:\PhD\Publication\Machine Learning-Driven Modeling of Urban Growth Patterns and Future Projections in the Greater Tehran Region\figure\administrative_facilities_kde_plot.png",
        r"E:\PhD\Publication\Machine Learning-Driven Modeling of Urban Growth Patterns and Future Projections in the Greater Tehran Region\figure\commercial_facilities_kde_plot.png",
        r"E:\PhD\Publication\Machine Learning-Driven Modeling of Urban Growth Patterns and Future Projections in the Greater Tehran Region\figure\educational_facilities_kde_plot.png",
        r"E:\PhD\Publication\Machine Learning-Driven Modeling of Urban Growth Patterns and Future Projections in the Greater Tehran Region\figure\cultural_facilities_kde_plot.png",
        r"E:\PhD\Publication\Machine Learning-Driven Modeling of Urban Growth Patterns and Future Projections in the Greater Tehran Region\figure\health_facilities_kde_plot.png",
    ]

    output_path = "final_5image_landscape_collage_2x2_center.jpg"
    combine_images_equal(image_paths, output_path)
