import os
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

def generate_layout_options(images, large_index, available_width, available_height, padding):
    """Generate multiple layout options for the images."""
    layouts = []
    
    # Option 1: Large on top, 3 small below (2x2 grid with merged top)
    total_height = images[large_index].size[1] + max(img.size[1] for i, img in enumerate(images) if i != large_index) + 3 * padding
    total_width = max(images[large_index].size[0], sum(img.size[0] for i, img in enumerate(images) if i != large_index) + 2 * padding)
    if total_width <= available_width and total_height <= available_height:
        layouts.append({
            'name': 'Large top with 3 small below',
            'type': 'grid',
            'large_pos': 'top',
            'score': (available_width * available_height) - (total_width * total_height)
        })
    
    # Option 2: Large on left, 3 small on right (2x2 grid with merged left)
    total_width = images[large_index].size[0] + max(img.size[0] for i, img in enumerate(images) if i != large_index) + 3 * padding
    total_height = max(images[large_index].size[1], sum(img.size[1] for i, img in enumerate(images) if i != large_index) + 2 * padding)
    if total_width <= available_width and total_height <= available_height:
        layouts.append({
            'name': 'Large left with 3 small right',
            'type': 'grid',
            'large_pos': 'left',
            'score': (available_width * available_height) - (total_width * total_height)
        })
    
    # Option 3: Classic 2x2 grid with one larger image
    cell_width = (available_width - padding) / 2  # Changed to single padding between cells
    cell_height = (available_height - padding) / 2
    if all(img.size[0] <= cell_width and img.size[1] <= cell_height for img in images):
        layouts.append({
            'name': 'Classic 2x2 grid',
            'type': 'grid',
            'large_pos': 'any',
            'score': (available_width * available_height) - (available_width * available_height)  # full usage
        })
    
    # Sort layouts by how well they use space (higher score is better)
    layouts.sort(key=lambda x: x['score'], reverse=True)
    
    return layouts

def display_layout_options(layouts, images, large_index):
    """Display visual previews of layout options."""
    print("\nAvailable Layout Options:")
    for i, layout in enumerate(layouts, 1):
        print(f"{i}. {layout['name']} (Space efficiency: {layout['score']/(A4_SIZE[0]*A4_SIZE[1]):.1%})")
        
        # Create a simple visualization
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.set_title(layout['name'])
        ax.axis('off')
        
        # Simulate layout
        if layout['type'] == 'grid':
            if layout['large_pos'] == 'top':
                # Large top, 3 small bottom
                pass
            elif layout['large_pos'] == 'left':
                # Large left, 3 small right
                pass
            else:
                # Classic 2x2
                pass
        
        plt.show()
    
    selection = int(input("Enter the number of your preferred layout: ")) - 1
    return layouts[selection]

def combine_images(img_paths, large_index=0, orientation='portrait', save_path="combined_image.jpg"):
    """
    Combines 4 images into an A4 collage where one is larger than others,
    with multiple layout options to choose from.
    """
    
    # === Constants ===
    global A4_SIZE
    DPI = 300
    A4_MM = (210, 297)  # A4 dimensions in mm
    A4_SIZE = (int(A4_MM[0] * DPI / 25.4), int(A4_MM[1] * DPI / 25.4)) if orientation == 'portrait' else \
              (int(A4_MM[1] * DPI / 25.4), int(A4_MM[0] * DPI / 25.4))
    PAGE_MARGIN = int(DPI * 0.2)  # 5mm margin
    IMAGE_PADDING = int(DPI * 0.1)  # 2.5mm padding
    
    # === Validate inputs ===
    if len(img_paths) != 4:
        raise ValueError("Exactly 4 image paths required.")
    if not all(os.path.isfile(p) for p in img_paths):
        raise FileNotFoundError("Invalid image path(s) detected.")
    if not 0 <= large_index < 4:
        raise IndexError("large_index must be 0-3.")
    if orientation not in ['landscape', 'portrait']:
        raise ValueError("Orientation must be 'landscape' or 'portrait'.")

    # === Load images ===
    try:
        images = [Image.open(p) for p in img_paths]
    except Exception as e:
        raise IOError(f"Error opening images: {e}")

    # === Calculate available space ===
    available_width = A4_SIZE[0] - 2 * PAGE_MARGIN
    available_height = A4_SIZE[1] - 2 * PAGE_MARGIN
    
    # === Calculate scale factors to fit available space ===
    def calculate_scale_factors(large_scale=1.5):
        # First calculate for the large image
        large_img = images[large_index]
        large_aspect = large_img.size[0] / large_img.size[1]
        
        # Then for small images
        small_imgs = [img for i, img in enumerate(images) if i != large_index]
        small_aspects = [img.size[0] / img.size[1] for img in small_imgs]
        
        # Try different scale factors to find the best fit
        best_scale = 1.0
        best_layout = None
        
        for scale in np.linspace(0.1, 2.0, 20):
            # Scale large image
            large_w = large_img.size[0] * scale * large_scale
            large_h = large_img.size[1] * scale * large_scale
            
            # Scale small images
            small_w = [img.size[0] * scale for img in small_imgs]
            small_h = [img.size[1] * scale for img in small_imgs]
            
            # Check if this scale fits in any layout
            layouts = generate_layout_options([
                Image.new('RGB', (int(large_w), int(large_h))) if i == large_index else 
                Image.new('RGB', (int(small_w[i if i < large_index else i-1]), 
                          int(small_h[i if i < large_index else i-1])))
                for i in range(4)
            ], large_index, available_width, available_height, IMAGE_PADDING)
            
            if layouts and (best_layout is None or layouts[0]['score'] > best_layout['score']):
                best_scale = scale
                best_layout = layouts[0]
        
        return best_scale, best_layout
    
    best_scale, best_layout = calculate_scale_factors()
    
    if not best_layout:
        # If no layout fits, reduce the large image scale factor gradually
        for scale_factor in [1.4, 1.3, 1.2, 1.1]:
            best_scale, best_layout = calculate_scale_factors(scale_factor)
            if best_layout:
                print(f"Adjusted large image scale to {scale_factor}x to fit A4")
                break
    
    if not best_layout:
        raise ValueError("Could not find a suitable layout for these images on A4.")
    
    # === Resize images ===
    try:
        resample_mode = Image.Resampling.LANCZOS
    except AttributeError:
        resample_mode = Image.LANCZOS
    
    resized_images = []
    for i in range(4):
        if i == large_index:
            new_size = (int(images[i].size[0] * best_scale * 1.5), 
                       int(images[i].size[1] * best_scale * 1.5))
        else:
            new_size = (int(images[i].size[0] * best_scale), 
                       int(images[i].size[1] * best_scale))
        resized_images.append(images[i].resize(new_size, resample=resample_mode))
    
    # === Show layout options and let user choose ===
    print("\nGenerated layout options based on your images:")
    selected_layout = display_layout_options(
        generate_layout_options(resized_images, large_index, available_width, available_height, IMAGE_PADDING),
        resized_images,
        large_index
    )
    
    # === Create final image ===
    final_img = Image.new("RGB", A4_SIZE, color=(255, 255, 255))
    
    if selected_layout['name'] == 'Large top with 3 small below':
        # Position large image at top center
        x = (A4_SIZE[0] - resized_images[large_index].size[0]) // 2
        y = PAGE_MARGIN
        final_img.paste(resized_images[large_index], (x, y))
        
        # Position small images below
        smalls = [img for i, img in enumerate(resized_images) if i != large_index]
        total_small_width = sum(img.size[0] for img in smalls) + (len(smalls)-1)*IMAGE_PADDING
        x_start = (A4_SIZE[0] - total_small_width) // 2
        y = PAGE_MARGIN + resized_images[large_index].size[1] + IMAGE_PADDING
        
        for img in smalls:
            final_img.paste(img, (x_start, y))
            x_start += img.size[0] + IMAGE_PADDING
            
    elif selected_layout['name'] == 'Large left with 3 small right':
        # Position large image at left center
        x = PAGE_MARGIN
        y = (A4_SIZE[1] - resized_images[large_index].size[1]) // 2
        final_img.paste(resized_images[large_index], (x, y))
        
        # Position small images to the right
        smalls = [img for i, img in enumerate(resized_images) if i != large_index]
        total_small_height = sum(img.size[1] for img in smalls) + (len(smalls)-1)*IMAGE_PADDING
        y_start = (A4_SIZE[1] - total_small_height) // 2
        x = PAGE_MARGIN + resized_images[large_index].size[0] + IMAGE_PADDING
        
        for img in smalls:
            final_img.paste(img, (x, y_start))
            y_start += img.size[1] + IMAGE_PADDING
            
    else:  # Classic 2x2 grid
        # Calculate cell dimensions
        cell_width = (available_width - IMAGE_PADDING) / 2
        cell_height = (available_height - IMAGE_PADDING) / 2
        
        # Position images in grid
        positions = [
            (PAGE_MARGIN, PAGE_MARGIN),  # top-left
            (PAGE_MARGIN + cell_width + IMAGE_PADDING, PAGE_MARGIN),  # top-right
            (PAGE_MARGIN, PAGE_MARGIN + cell_height + IMAGE_PADDING),  # bottom-left
            (PAGE_MARGIN + cell_width + IMAGE_PADDING, PAGE_MARGIN + cell_height + IMAGE_PADDING)  # bottom-right
        ]
        
        # Place large image first
        final_img.paste(resized_images[large_index], positions[0])
        
        # Place remaining images
        pos_index = 1
        for i in range(4):
            if i != large_index:
                final_img.paste(resized_images[i], positions[pos_index])
                pos_index += 1
    
    # === Save final image with quality settings ===
    final_img.save(save_path, quality=95, dpi=(DPI, DPI), subsampling=0)
    
    # Verify output dimensions
    output_img = Image.open(save_path)
    if output_img.size != A4_SIZE:
        print(f"Adjusting output to exact A4 dimensions...")
        final_img = final_img.resize(A4_SIZE, resample=resample_mode)
        final_img.save(save_path, quality=100, dpi=(DPI, DPI), subsampling=0)
    
    print(f"\n✅ Perfect A4 collage saved to '{save_path}'")
    print(f"Dimensions: {A4_SIZE[0]}x{A4_SIZE[1]} pixels at {DPI} DPI")

if __name__ == "__main__":
    image_paths = [
        r"C:\Users\Reza\accessibility_map_roads.png",
        r"C:\Users\Reza\accessibility_map_metro.png",
        r"C:\Users\Reza\accessibility_map_bus.png",
        r"C:\Users\Reza\composite_accessibility_map.png"
    ]

    layout = "landscape"       # or "portrait"
    large_index = 3           # index of image to make larger
    output_path = "final_collage.jpg"

    try:
        combine_images(image_paths, large_index, layout, output_path)
    except Exception as e:
        print(f"❌ Error: {e}")
