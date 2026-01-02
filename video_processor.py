import tempfile
import os
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip, vfx
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from utils import apply_image_filters, resize_image_for_video, hex_to_rgb

def create_text_image(text, fontsize, color, font='arial.ttf', image_size=(100, 100), align='center'):
    """Creates a transparent image with text using Pillow (avoids ImageMagick dependency)."""
    # Create a dummy image to calculate text size
    dummy_img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
    draw = ImageDraw.Draw(dummy_img)
    
    try:
        font_obj = ImageFont.truetype(font, fontsize)
    except IOError:
        font_obj = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font_obj)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Create the actual image
    img = Image.new('RGBA', image_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Calculate position
    x = (image_size[0] - text_width) / 2 # Center horizontally
    
    if align == 'top':
        y = image_size[1] * 0.1 # 10% from top
    elif align == 'bottom':
        y = image_size[1] * 0.8 # 20% from bottom
    else: # center
        y = (image_size[1] - text_height) / 2
    
    draw.text((x, y), text, font=font_obj, fill=color)
    return img

def create_clip_from_data(image_data, global_settings, temp_dir):
    """
    Creates a MoviePy clip from a single image data dict.
    image_data: dict containing 'path', 'filters', 'duration', 'text_overlay'
    """
    image_path = image_data['path']
    filters = image_data.get('filters', {})
    duration = image_data.get('duration', 3)
    text_overlay = image_data.get('text_overlay', {})
    
    # Load and process image
    pil_img = Image.open(image_path).convert('RGB')
    pil_img = apply_image_filters(pil_img, filters)
    
    # Resize
    target_res = global_settings.get('resolution', (1080, 1920))
    bg_color = hex_to_rgb(global_settings.get('bg_color', '#000000'))
    fit_method = global_settings.get('fit_method', 'contain')
    
    pil_img = resize_image_for_video(pil_img, target_res, fit_method, bg_color)
    
    # Create temp file for the processed image to ensure MoviePy compatibility
    # (MoviePy sometimes struggles with direct PIL objects in complex compositions)
    temp_img_path = os.path.join(temp_dir, f"processed_{os.path.basename(image_path)}")
    pil_img.save(temp_img_path)
    
    clip = ImageClip(temp_img_path).set_duration(duration)
    
    # Apply Text Overlay
    if text_overlay and text_overlay.get('text'):
        txt_img = create_text_image(
            text_overlay['text'],
            text_overlay.get('fontsize', 50),
            text_overlay.get('color', 'white'),
            image_size=target_res,
            align=text_overlay.get('align', 'center')
        )
        txt_clip = ImageClip(np.array(txt_img)).set_duration(duration)
        clip = CompositeVideoClip([clip, txt_clip])

    # Apply Transitions (simulated by simple effects for now, complex crossfades done in concat)
    # Note: Crossfade transitions usually handled at checking time
    
    return clip

def render_video(project_data, output_path, progress_callback=None):
    """
    Main function to render video.
    project_data: dict containing 'images', 'audio', 'settings'
    """
    settings = project_data.get('settings', {})
    images = project_data.get('images', [])
    audio_config = project_data.get('audio', {})
    
    if not images:
        return "No images to render"

    clips = []
    
    with tempfile.TemporaryDirectory() as temp_dir:
        for idx, img_data in enumerate(images):
            clip = create_clip_from_data(img_data, settings, temp_dir)
            
            # Apply transition into this clip if specified (e.g., crossfadein)
            # This is simplified; robust transition systems usually involve overlapping clips.
            # here we just append.
            clips.append(clip)
            
            if progress_callback:
                progress_callback((idx + 1) / len(images) * 0.5) # 50% for clip creation
        
        final_clip = concatenate_videoclips(clips, method="compose")
        
        # Add Audio
        if audio_config.get('path'):
            audio = AudioFileClip(audio_config['path'])
            
            # Trim audio
            start = audio_config.get('start_time', 0)
            end = audio_config.get('end_time')
            if end:
                audio = audio.subclip(start, end)
            else:
                audio = audio.subclip(start) # to end
            
            # Loop audio if video is longer
            if audio.duration < final_clip.duration and audio_config.get('loop'):
                audio = audio.fx(vfx.audio_loop, duration=final_clip.duration)
            
            # Adjust volume
            audio = audio.volumex(audio_config.get('volume', 1.0))
            
            # Set audio
            final_clip = final_clip.set_audio(audio)
            # If audio is shorter than video and no loop, set_audio cuts the video? 
            # No, set_audio just sets it. But we should check duration.
            if audio.duration > final_clip.duration:
                 final_clip = final_clip.set_audio(audio.subclip(0, final_clip.duration))

        # Write file
        fps = settings.get('fps', 30)
        # Using ultrafast preset for speed as requested
        final_clip.write_videofile(
            output_path, 
            fps=fps, 
            codec='libx264', 
            audio_codec='aac',
            preset='ultrafast',
            threads=4
        )
        
    return output_path

