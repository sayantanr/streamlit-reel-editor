# 🎬 Streamlit Reel Editor Pro
A powerful, single-page application (SPA) built with Streamlit and MoviePy for creating high-quality social media reels from images and audio. Optimized for performance on standard workstations (16GB RAM).
## 🚀 Quick Start
1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run Application**:
    ```bash
    streamlit run app.py
    ```
3.  **Use**: Open `http://localhost:8501` in your browser.
## ✨ 50+ Amazing Features
### 🎨 Global Project Settings
1.  **Multiple Aspect Ratios**:
    - 9:16 (TikTok/Reels/Shorts)
    - 16:9 (YouTube Standard)
    - 1:1 (Instagram Feed)
    - 4:5 (Portrait)
2.  **Frame Rate Control**: 24, 30, or 60 FPS.
3.  **Background Customization**: Choose any hex color for non-filling images.
4.  **Image Fitting Engine**:
    - **Contain**: Fit image fully with background bars.
    - **Cover**: Crop image to fill screen.
    - **Stretch**: Force fit (aspect ratio ignored).
### 🖼️ Advanced Image Editor (Per Slide)
Each image in your timeline gets its own dedicated editor:
**Transforms:**
5.  **Reordering**: Drag and drop (via upload order) or remove specific frames.
6.  **Duration Control**: Set precise duration (0.5s to 10s) per slide.
7.  **Rotation**: 0°, 90°, 180°, 270°.
**Professional Filters & Color Grading:**
8.  **Brightness**: Adjust light levels.
9.  **Contrast**: Increase or decrease dynamic range.
10. **Saturation**: Boost colors or go muted.
11. **Sharpness**: Enhance edge details.
12. **Gamma**: Non-linear luminance adjustment.
13. **Blur**: Gaussian blur for aesthetic effects.
14. **Grayscale**: Classic B&W look.
15. **Sepia**: Vintage aesthetic.
16. **Invert**: Negative effect.
17. **Emboss**: 3D shadow effect.
18. **Contour**: Outline styling.
19. **Detail**: Enhance fine details.
20. **Edge Enhance**: Strengthen structural lines.
**Text Overlays:**
21. **Custom Text**: Add captions or titles per slide.
22. **Font Resizing**: Dynamic scaling (10px - 200px).
23. **Color Picker**: Full RGB spectrum for text color.
24. **Alignment**:
    - Top
    - Center
    - Bottom
### 🎵 Audio Studio
25. **Upload Support**: MP3 and WAV files.
26. **Volume Mixing**: Adjust background music levels (0% - 200%).
27. **Auto-Looping**: Automatically repeat short clips to match video length.
28. **Smart Trimming**: Auto-fits audio to video duration.
### ⚙️ Performance & Architecture
29. **SPA Design**: Everything happens in one seamless view; no page reloads.
30. **Optimized Video Engine**:
    - Sequential processing to keep RAM usage low.
    - Intermediate caching for faster previews.
31. **Ultrafast Rendering**: Uses H.264 `ultrafast` preset for rapid exports.
32. **Crash Resilience**: Independent frame processing.
### 📤 Export
33. **Instant Preview**: View results directly in the browser.
34. **One-Click Download**: Get your `.mp4` file immediately.
35. **Cross-Platform**: Works on Windows, Mac, and Linux.
## 📁 Project Structure
- `app.py`: Main application interface and state management.
- `video_processor.py`: Core logic for video rendering and composition (MoviePy).
- `utils.py`: High-performance image processing functions (Pillow).
- `requirements.txt`: Dependency lockfile.
