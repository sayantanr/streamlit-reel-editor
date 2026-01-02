from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import numpy as np

def hex_to_rgb(hex_color):
    """Converts hex color string to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def apply_image_filters(image, filters):
    """
    Applies a dictionary of filters to a PIL Image.
    filters dict keys:
        - brightness (float, default 1.0)
        - contrast (float, default 1.0)
        - saturation (float, default 1.0)
        - sharpness (float, default 1.0)
        - grayscale (bool)
        - sepia (bool)
        - invert (bool)
        - blur (float, radius)
        - emboss (bool)
        - rotate (int)
    """
    img = image.copy()

    # Transformations
    if filters.get('rotate'):
        img = img.rotate(-filters['rotate'], expand=True) # Negative for clockwise

    # Color Enhancements
    if filters.get('brightness', 1.0) != 1.0:
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(filters['brightness'])
    
    if filters.get('contrast', 1.0) != 1.0:
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(filters['contrast'])

    if filters.get('saturation', 1.0) != 1.0:
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(filters['saturation'])

    if filters.get('sharpness', 1.0) != 1.0:
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(filters['sharpness'])

    # Effects
    if filters.get('grayscale'):
        img = ImageOps.grayscale(img).convert("RGB") # Keep as RGB for consistency
    
    if filters.get('invert'):
        if img.mode == 'RGBA':
            r,g,b,a = img.split()
            rgb_image = Image.merge('RGB', (r,g,b))
            inverted_image = ImageOps.invert(rgb_image)
            r2,g2,b2 = inverted_image.split()
            img = Image.merge('RGBA', (r2,g2,b2,a))
        else:
            img = ImageOps.invert(img)

    if filters.get('sepia'):
        sepia_filter = np.array([
            [0.393, 0.769, 0.189],
            [0.349, 0.686, 0.168],
            [0.272, 0.534, 0.131]
        ])
        img_np = np.array(img)
        sepia_img = img_np.dot(sepia_filter.T)
        sepia_img /= 255.0
        sepia_img = np.clip(sepia_img, 0, 1) * 255
        img = Image.fromarray(sepia_img.astype('uint8'))

    if filters.get('blur', 0) > 0:
        img = img.filter(ImageFilter.GaussianBlur(radius=filters['blur']))

    if filters.get('emboss'):
        img = img.filter(ImageFilter.EMBOSS)
    
    if filters.get('contour'):
        img = img.filter(ImageFilter.CONTOUR)

    if filters.get('detail'):
        img = img.filter(ImageFilter.DETAIL)
    
    if filters.get('edge_enhance'):
        img = img.filter(ImageFilter.EDGE_ENHANCE)
        
    if filters.get('posterize'):
        # Posterize requires integer bits 1-8
        bits = filters.get('posterize_bits', 4)
        img = ImageOps.posterize(img, bits)
        
    if filters.get('solarize'):
        threshold = filters.get('solarize_threshold', 128)
        img = ImageOps.solarize(img, threshold)

    return img

def resize_image_for_video(image, target_size, fit_method='contain', bg_color=(0,0,0)):
    """
    Resizes image to target_size (width, height).
    fit_method: 'contain' (add padding), 'cover' (crop), 'stretch'
    """
    img = image.copy()
    target_w, target_h = target_size
    img_w, img_h = img.size
    
    if fit_method == 'stretch':
        return img.resize(target_size, Image.LANCZOS)
    
    # Calculate aspect ratios
    target_aspect = target_w / target_h
    img_aspect = img_w / img_h

    if fit_method == 'cover':
        if img_aspect > target_aspect: # Image is wider than target
            new_h = target_h
            new_w = int(new_h * img_aspect)
        else: # Image is taller than target
            new_w = target_w
            new_h = int(new_w / img_aspect)
        
        img = img.resize((new_w, new_h), Image.LANCZOS)
        
        # Center crop
        left = (new_w - target_w) / 2
        top = (new_h - target_h) / 2
        right = (new_w + target_w) / 2
        bottom = (new_h + target_h) / 2
        img = img.crop((left, top, right, bottom))
        return img

    elif fit_method == 'contain':
        if img_aspect > target_aspect: # Image is wider
            new_w = target_w
            new_h = int(new_w / img_aspect)
        else: # Image is taller
            new_h = target_h
            new_w = int(new_h * img_aspect)
            
        img = img.resize((new_w, new_h), Image.LANCZOS)
        
        # Create background
        bg = Image.new('RGB', target_size, bg_color)
        offset = ((target_w - new_w) // 2, (target_h - new_h) // 2)
        bg.paste(img, offset)
        return bg

    return img
