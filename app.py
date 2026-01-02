import streamlit as st
import os
import shutil
from PIL import Image
import tempfile
from video_processor import render_video
from utils import hex_to_rgb

# Page Config
st.set_page_config(
    page_title="Reel Editor Pro",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- State Management ---
if 'project' not in st.session_state:
    st.session_state.project = {
        'images': [], # List of dicts: {path, id, filters: {}, duration: 3, text_overlay: {}}
        'audio': {},  # {path, volume, start, end, loop}
        'settings': {
            'resolution': (1080, 1920), # Default 9:16
            'fps': 30,
            'bg_color': '#000000',
            'fit_method': 'contain'
        }
    }

if 'temp_global_dir' not in st.session_state:
    st.session_state.temp_global_dir = tempfile.mkdtemp()

# Cleanup on exit (not perfect in Streamlit but good practice)
# We won't implement complex cleanup hooks here to keep it simple.

def save_uploaded_file(uploaded_file):
    try:
        path = os.path.join(st.session_state.temp_global_dir, uploaded_file.name)
        with open(path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return path
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return None

# --- UI Components ---
def sidebar_settings():
    st.sidebar.title("⚙️ Global Settings")
    
    # Resolution
    res_options = {
        "9:16 (Reel/TikTok)": (1080, 1920),
        "16:9 (YouTube)": (1920, 1080),
        "1:1 (Square)": (1080, 1080),
        "4:5 (Portrait)": (1080, 1350)
    }
    res_name = st.sidebar.selectbox("Aspect Ratio", list(res_options.keys()))
    st.session_state.project['settings']['resolution'] = res_options[res_name]
    
    # FPS
    st.session_state.project['settings']['fps'] = st.sidebar.select_slider(
        "Frame Rate (FPS)", options=[24, 30, 60], value=30
    )
    
    # Background
    st.session_state.project['settings']['bg_color'] = st.sidebar.color_picker(
        "Background Color", st.session_state.project['settings']['bg_color']
    )
    
    # Fit Method
    st.session_state.project['settings']['fit_method'] = st.sidebar.radio(
        "Image Fit", ['contain', 'cover', 'stretch'],
        help="'Contain' adds padding. 'Cover' crops the image. 'Stretch' distorts it."
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info(f"Memory Usage: Optimized for 16GB RAM\nCurrent Images: {len(st.session_state.project['images'])}")

def image_editor_ui(idx, img_data):
    """Controls for a single image"""
    
    # Thumbnail and basic info
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image(img_data['path'], width=100)
    with col2:
        st.markdown(f"**Image {idx + 1}**: `{os.path.basename(img_data['path'])}`")
        
        # Duration
        img_data['duration'] = st.slider(
            f"Duration (sec) ##{idx}", 0.5, 10.0, float(img_data.get('duration', 3.0)), 0.5,
            key=f"dur_{idx}"
        )
    
    # Tabs for Editing
    tab_filters, tab_text, tab_transform = st.tabs(["🎨 Filters", "📝 Text", "📐 Transform"])
    
    with tab_filters:
        c1, c2, c3 = st.columns(3)
        with c1:
            img_data['filters']['brightness'] = st.slider("Brightness", 0.0, 2.0, 1.0, 0.1, key=f"bright_{idx}")
            img_data['filters']['contrast'] = st.slider("Contrast", 0.0, 2.0, 1.0, 0.1, key=f"cont_{idx}")
            img_data['filters']['blur'] = st.slider("Blur", 0.0, 10.0, 0.0, 0.5, key=f"blur_{idx}")
        with c2:
            img_data['filters']['saturation'] = st.slider("Saturation", 0.0, 2.0, 1.0, 0.1, key=f"sat_{idx}")
            img_data['filters']['sharpness'] = st.slider("Sharpness", 0.0, 2.0, 1.0, 0.1, key=f"sharp_{idx}")
            img_data['filters']['gamma'] = st.slider("Gamma", 0.1, 4.0, 1.0, 0.1, key=f"gamma_{idx}")

        with c3:
            st.markdown("**Effects**")
            cols_eff = st.columns(2)
            if cols_eff[0].checkbox("Grayscale", key=f"gray_{idx}"): img_data['filters']['grayscale'] = True
            else: img_data['filters']['grayscale'] = False
            
            if cols_eff[1].checkbox("Sepia", key=f"sepia_{idx}"): img_data['filters']['sepia'] = True
            else: img_data['filters']['sepia'] = False
            
            if cols_eff[0].checkbox("Invert", key=f"inv_{idx}"): img_data['filters']['invert'] = True
            else: img_data['filters']['invert'] = False

            if cols_eff[1].checkbox("Emboss", key=f"emb_{idx}"): img_data['filters']['emboss'] = True
            else: img_data['filters']['emboss'] = False
            
            if cols_eff[0].checkbox("Contour", key=f"cnt_{idx}"): img_data['filters']['contour'] = True
            else: img_data['filters']['contour'] = False
            
            if cols_eff[1].checkbox("Detail", key=f"det_{idx}"): img_data['filters']['detail'] = True
            else: img_data['filters']['detail'] = False
            
            if cols_eff[0].checkbox("Edge Enhance", key=f"edge_{idx}"): img_data['filters']['edge_enhance'] = True
            else: img_data['filters']['edge_enhance'] = False

    with tab_text:
        t_en = st.checkbox("Enable Overlay", key=f"ten_{idx}")
        if t_en:
            img_data['text_overlay']['text'] = st.text_input("Text", key=f"txt_{idx}")
            c_txt1, c_txt2 = st.columns(2)
            with c_txt1:
                img_data['text_overlay']['fontsize'] = st.number_input("Size", 10, 200, 50, key=f"tsz_{idx}")
                img_data['text_overlay']['color'] = st.color_picker("Color", "#FFFFFF", key=f"tcol_{idx}")
            with c_txt2:
                img_data['text_overlay']['align'] = st.selectbox("Position", ["center", "top", "bottom"], key=f"tpos_{idx}")
        else:
            img_data['text_overlay'] = {}

    with tab_transform:
        rot = st.selectbox("Rotate", [0, 90, 180, 270], key=f"rot_{idx}")
        img_data['filters']['rotate'] = rot

def main():
    st.title("🎬 Streamlit Reel Editor")
    
    sidebar_settings()
    
    tab_editor, tab_audio, tab_export = st.tabs(["🖼️ Timeline Editor", "🎵 Audio", "📤 Export & Preview"])
    
    # --- Tab 1: Timeline ---
    with tab_editor:
        uploaded_files = st.file_uploader("Add Images", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
        if uploaded_files:
            for uf in uploaded_files:
                # check if already added to avoid duplicates on rerun
                # (Simple check by filename match in this session)
                is_new = True
                for img in st.session_state.project['images']:
                    if os.path.basename(img['path']) == uf.name:
                        is_new = False
                        break
                
                if is_new:
                    path = save_uploaded_file(uf)
                    if path:
                        st.session_state.project['images'].append({
                            'path': path,
                            'filters': {},
                            'duration': 3.0,
                            'text_overlay': {}
                        })
            # Clear uploader logic is tricky in Streamlit, usually we just ignore
            
        st.subheader("Timeline")
        
        if not st.session_state.project['images']:
            st.info("Upload images to start editing.")
        else:
            # Reorder controls
            
            for i, img_data in enumerate(st.session_state.project['images']):
                with st.expander(f"Frame {i+1}: {os.path.basename(img_data['path'])}", expanded=False):
                    image_editor_ui(i, img_data)
                    if st.button(f"Remove Frame {i+1}", key=f"rem_{i}"):
                        st.session_state.project['images'].pop(i)
                        st.rerun()

    # --- Tab 2: Audio ---
    with tab_audio:
        st.header("Audio Settings")
        audio_file = st.file_uploader("Upload Background Music", type=['mp3', 'wav'])
        if audio_file:
            path = save_uploaded_file(audio_file)
            st.session_state.project['audio']['path'] = path
            st.success(f"Loaded: {audio_file.name}")
        
        if st.session_state.project['audio'].get('path'):
            st.audio(st.session_state.project['audio']['path'])
            c1, c2 = st.columns(2)
            with c1:
                st.session_state.project['audio']['volume'] = st.slider("Volume", 0.0, 2.0, 1.0)
            with c2:
                st.session_state.project['audio']['loop'] = st.checkbox("Loop Audio", value=True)

    # --- Tab 3: Export ---
    with tab_export:
        st.header("Render Reel")
        
        if st.button("🚀 Render Video"):
            if not st.session_state.project['images']:
                st.error("Add images first!")
            else:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    status_text.text("Rendering... This may take a moment.")
                    
                    output_file = os.path.join(st.session_state.temp_global_dir, "output_reel.mp4")
                    
                    def update_progress(p):
                        progress_bar.progress(p)
                    
                    result_path = render_video(st.session_state.project, output_file, update_progress)
                    
                    progress_bar.progress(1.0)
                    status_text.success("Rendering Complete!")
                    
                    st.video(result_path)
                    
                    with open(result_path, "rb") as f:
                        st.download_button(
                            "⬇️ Download Reel",
                            f,
                            "my_reel.mp4",
                            "video/mp4"
                        )
                except Exception as e:
                    status_text.error(f"Rendering failed: {str(e)}")
                    st.exception(e)

if __name__ == "__main__":
    main()
