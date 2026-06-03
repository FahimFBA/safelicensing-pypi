"""
SafeLicensing Streamlit web application.

Provides a browser-based interface for detecting and encrypting license plates
in images and videos. Launched via the ``safelicensing`` CLI command or
directly with ``streamlit run app.py``.
"""

import streamlit as st

st.set_page_config(
    page_title="SafeLicensing - License Plate Encryption",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

import io
import os
import time
from pathlib import Path

import cv2
import numpy as np
import requests
from PIL import Image
from moviepy.editor import ImageSequenceClip, VideoFileClip

from safelicensing.detection import detect_license_plates
from safelicensing.encryption import encrypt_image
from safelicensing.video import process_video, create_video_from_frames

BUNDLED_MODEL_PATH: str = str(Path(__file__).parent / "best.pt")


def download_file(url: str, timeout: int = 15) -> bytes:
    """
    Fetch a remote file over HTTP and return its raw bytes.

    :param url: The URL of the resource to download.
    :param timeout: Request timeout in seconds. Default is 15.
    :return: Raw bytes of the downloaded file.
    :raises requests.HTTPError: If the server returns a non-2xx status code.
    :raises requests.Timeout: If the request exceeds ``timeout`` seconds.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )
    }
    response = requests.get(url, headers=headers, timeout=timeout, stream=True)
    response.raise_for_status()
    return response.content


@st.cache_resource(show_spinner=False)
def load_cached_model(weights_path: str):
    """
    Load and cache a YOLOv8 model for the lifetime of the Streamlit session.

    Streamlit's ``cache_resource`` ensures the model is only loaded once per
    server process, even when multiple users interact with the app.

    :param weights_path: Absolute path to the ``.pt`` weights file.
    :return: Loaded YOLO model instance.
    :raises FileNotFoundError: If ``weights_path`` does not exist.
    """
    from safelicensing.detection import load_model
    return load_model(weights_path)


def inject_styles() -> None:
    """
    Inject custom CSS into the Streamlit app for consistent branding.

    :return: None.
    """
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=DM+Sans:wght@400;500;700&display=swap');

        :root {
            --bg: var(--background-color, #0e1117);
            --surface: var(--secondary-background-color, #262730);
            --text: var(--text-color, #fafafa);
            --muted: rgba(160, 165, 180, 0.9);
            --accent: #0ea5a4;
            --accent-2: #2563eb;
            --danger: #dc4965;
            --stroke: rgba(127, 127, 127, 0.22);
            --panel: var(--surface);
            --panel-strong: var(--surface);
            --header-bg: transparent;
            --hero-glow: radial-gradient(circle, rgba(37, 99, 235, 0.18), transparent 60%);
            --eyebrow-bg: rgba(14, 165, 164, 0.12);
            --eyebrow-text: var(--text);
            --input-bg: var(--surface);
            --button-text: #04111f;
        }

        .stApp {
            background-color: var(--bg);
            background-image:
                radial-gradient(circle at top left, rgba(14, 165, 164, 0.12), transparent 24%),
                radial-gradient(circle at top right, rgba(37, 99, 235, 0.14), transparent 26%);
            color: var(--text);
            font-family: "DM Sans", sans-serif;
        }

        [data-testid="stHeader"] { background: var(--header-bg); }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1220px;
        }

        h1, h2, h3 {
            font-family: "Space Grotesk", sans-serif;
            letter-spacing: -0.03em;
            color: var(--text);
        }

        .hero-shell {
            position: relative;
            overflow: hidden;
            padding: 2rem 2rem 1.75rem;
            border-radius: 28px;
            border: 1px solid var(--stroke);
            background:
                linear-gradient(135deg, var(--surface), var(--bg)),
                linear-gradient(120deg, rgba(14, 165, 164, 0.08), rgba(37, 99, 235, 0.08));
            box-shadow: 0 28px 80px rgba(0, 0, 0, 0.28);
            margin-bottom: 1.25rem;
        }

        .hero-shell::after {
            content: "";
            position: absolute;
            inset: auto -8% -35% auto;
            width: 340px;
            height: 340px;
            border-radius: 999px;
            background: var(--hero-glow);
            pointer-events: none;
        }

        .eyebrow {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.45rem 0.85rem;
            border-radius: 999px;
            background: var(--eyebrow-bg);
            color: var(--accent);
            font-size: 0.82rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        .hero-title {
            margin: 0.9rem 0 0.6rem;
            font-size: clamp(2.2rem, 4vw, 3.6rem);
            line-height: 1.05;
        }

        .hero-copy {
            max-width: 760px;
            color: var(--muted);
            font-size: 1rem;
            line-height: 1.7;
            margin-bottom: 1.4rem;
        }

        .hero-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.85rem;
        }

        .glass-card {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid var(--stroke);
            border-radius: 18px;
            padding: 0.9rem 1rem;
        }

        .stat-label {
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-size: 0.72rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }

        .stat-value {
            font-family: "Space Grotesk", sans-serif;
            font-size: 1rem;
            font-weight: 700;
            color: var(--text);
        }

        .section-card, .meta-card {
            background: var(--panel);
            border: 1px solid var(--stroke);
            border-radius: 20px;
            padding: 1.25rem;
            margin-bottom: 1rem;
            box-shadow: 0 12px 36px rgba(0, 0, 0, 0.14);
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: var(--panel);
            border: 1px solid var(--stroke) !important;
            border-radius: 20px;
            padding: 1.25rem;
            box-shadow: 0 12px 36px rgba(0, 0, 0, 0.14);
            display: flex;
            flex-direction: column;
        }

        .control-head { margin-bottom: 1rem; }

        .section-kicker {
            color: var(--accent);
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-size: 0.74rem;
            font-weight: 700;
            margin-bottom: 0.3rem;
        }

        .section-title {
            font-family: "Space Grotesk", sans-serif;
            font-size: 1.25rem;
            font-weight: 700;
            line-height: 1.2;
            margin-bottom: 0.45rem;
        }

        .section-copy {
            color: var(--muted);
            margin-bottom: 0;
            line-height: 1.6;
            font-size: 0.95rem;
        }

        .results-head {
            margin: 1.25rem 0 0.75rem;
            font-family: "Space Grotesk", sans-serif;
            font-size: 1.4rem;
            font-weight: 700;
        }

        .meta-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 1rem;
            margin-bottom: 1.25rem;
        }

        .meta-title {
            font-family: "Space Grotesk", sans-serif;
            font-size: 1.1rem;
            font-weight: 700;
            line-height: 1.25;
            margin-bottom: 0.5rem;
        }

        .meta-copy {
            color: var(--muted);
            line-height: 1.7;
            margin: 0;
            font-size: 0.95rem;
        }

        .meta-copy a, .credit-link {
            color: var(--accent-2) !important;
            text-decoration: none;
            font-weight: 600;
        }

        .credit-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.6rem 1rem;
            margin-top: 0.75rem;
        }

        .stTextInput label, .stRadio label, .stSlider label,
        .stFileUploader label, .stMarkdown, .stCaption, .stAlert {
            color: var(--text) !important;
        }

        .stTextInput label, .stRadio label, .stSlider label,
        .stFileUploader label { font-weight: 600; }

        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div,
        [data-testid="stFileUploaderDropzone"] {
            background: var(--input-bg) !important;
            border: 1px solid var(--stroke) !important;
        }

        .stTextInput input, .stNumberInput input, textarea {
            color: var(--text) !important;
        }

        .stButton > button, .stDownloadButton > button {
            border-radius: 14px;
            border: 1px solid rgba(37, 99, 235, 0.24);
            background: linear-gradient(135deg, #2dd4bf, #60a5fa);
            color: var(--button-text);
            font-family: "Space Grotesk", sans-serif;
            font-weight: 700;
            padding: 0.75rem 1.25rem;
            box-shadow: 0 8px 24px rgba(37, 99, 235, 0.18);
            transition: box-shadow 0.15s ease, border-color 0.15s ease;
        }

        .stButton > button:hover, .stDownloadButton > button:hover {
            border-color: rgba(37, 99, 235, 0.45);
            box-shadow: 0 12px 32px rgba(37, 99, 235, 0.28);
            color: var(--button-text);
        }

        div[data-testid="stImage"] img, div[data-testid="stVideo"] video {
            border-radius: 16px;
            border: 1px solid var(--stroke);
            overflow: hidden;
        }

        div[data-testid="stMetric"] {
            background: var(--panel-strong);
            border: 1px solid var(--stroke);
            border-radius: 16px;
            padding: 0.8rem 1rem;
        }

        div[data-testid="stExpander"] {
            border: 1px solid var(--stroke) !important;
            border-radius: 16px !important;
            background: var(--panel);
            margin-bottom: 1rem;
        }

        @media (max-width: 900px) {
            .hero-grid { grid-template-columns: 1fr; }
            .meta-grid { grid-template-columns: 1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    """
    Render the hero section with title, description, and feature stats.

    :return: None.
    """
    st.markdown(
        """
        <section class="hero-shell">
            <div class="eyebrow">Privacy-first plate protection</div>
            <h1 class="hero-title">SafeLicensing Space</h1>
            <p class="hero-copy">
                Detect license plates in images and videos, then encrypt only sensitive regions with
                chaotic-map masking. Built for fast redaction previews, clean exports, and modern operator flow.
            </p>
            <div class="hero-grid">
                <div class="glass-card">
                    <div class="stat-label">Vision Core</div>
                    <div class="stat-value">YOLOv8 detection pipeline</div>
                </div>
                <div class="glass-card">
                    <div class="stat-label">Protection Layer</div>
                    <div class="stat-value">Dual-pass chaotic encryption</div>
                </div>
                <div class="glass-card">
                    <div class="stat-label">Supported Media</div>
                    <div class="stat-value">Image and video workflows</div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_research_meta() -> None:
    """
    Render the research paper reference and author credits section.

    :return: None.
    """
    st.markdown(
        """
        <section class="meta-grid">
            <div class="meta-card">
                <div class="section-kicker">Conference Paper</div>
                <div class="meta-title">Research foundation behind this workflow</div>
                <p class="meta-copy">
                    Vehicle Number Plate Detection and Encryption in Digital Images Using YOLOv8
                    and Chaotic-Based Encryption Scheme.
                    <a href="https://ieeexplore.ieee.org/abstract/document/10534375/" target="_blank">
                        View on IEEE Xplore
                    </a>
                </p>
            </div>
            <div class="meta-card">
                <div class="section-kicker">Credits</div>
                <div class="meta-title">Project authors</div>
                <div class="credit-row">
                    <a class="credit-link" href="https://www.fahimbinamin.com" target="_blank">Md. Fahim Bin Amin</a>
                    <a class="credit-link" href="https://www.isratjahankhan.com" target="_blank">Israt Jahan Khan</a>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def handle_image_processing(model, key_seed: float) -> None:
    """
    Render image upload/URL controls and run detection + encryption on submit.

    :param model: Loaded YOLO model instance.
    :param key_seed: Encryption seed selected by the user via the sidebar slider.
    :return: None.
    """
    image_url = st.text_input("Image URL")
    uploaded_file = st.file_uploader("Upload image", type=["jpg", "jpeg", "png"])

    detect_clicked = st.button("Detect & Encrypt", use_container_width=True)
    st.caption("Supports URL fetch or direct upload.")

    if not detect_clicked:
        return

    pil_image = None

    if image_url and not uploaded_file:
        try:
            content = download_file(image_url)
            pil_image = Image.open(io.BytesIO(content)).convert("RGB")
        except Exception as exc:
            st.error(f"Failed to load image from URL: {exc}")
            return
    elif uploaded_file:
        try:
            pil_image = Image.open(uploaded_file).convert("RGB")
        except Exception as exc:
            st.error(f"Failed to open uploaded image: {exc}")
            return
    else:
        st.warning("Please provide a URL or upload an image.")
        return

    start_time = time.time()

    with st.spinner("Detecting license plates..."):
        image_with_boxes, bboxes = detect_license_plates(model, pil_image.copy())

    if not bboxes:
        st.warning("No license plates detected.")
        return

    with st.spinner("Encrypting license plates..."):
        encrypted_np = np.array(pil_image, dtype=np.uint8)
        img_height, img_width = encrypted_np.shape[:2]

        for (x1, y1, x2, y2) in bboxes:
            x1 = max(x1, 0)
            y1 = max(y1, 0)
            x2 = min(x2, img_width)
            y2 = min(y2, img_height)
            plate_region = encrypted_np[y1:y2, x1:x2]
            if plate_region.size == 0:
                st.warning(f"Plate region ({x1},{y1},{x2},{y2}) is empty — skipped.")
                continue
            encrypted_np[y1:y2, x1:x2] = encrypt_image(plate_region, key_seed)

        encrypted_image = Image.fromarray(encrypted_np)

    elapsed_time = time.time() - start_time
    st.markdown('<div class="results-head">Result Overview</div>', unsafe_allow_html=True)

    metric_cols = st.columns(3)
    metric_cols[0].metric("Media Type", "Image")
    metric_cols[1].metric("Plates Found", len(bboxes))
    metric_cols[2].metric("Runtime", f"{elapsed_time:.2f}s")

    preview_cols = st.columns(3, gap="large")
    preview_cols[0].image(pil_image, caption="Original", use_column_width=True)
    preview_cols[1].image(image_with_boxes, caption="Detected", use_column_width=True)
    preview_cols[2].image(encrypted_image, caption="Encrypted", use_column_width=True)

    buf = io.BytesIO()
    encrypted_image.save(buf, format="PNG")
    buf.seek(0)
    st.download_button(
        label="Download Encrypted Image",
        data=buf,
        file_name="encrypted_plate.png",
        mime="image/png",
    )


def handle_video_processing(model, key_seed: float) -> None:
    """
    Render video upload/URL controls and run per-frame detection + encryption on submit.

    :param model: Loaded YOLO model instance.
    :param key_seed: Encryption seed selected by the user via the sidebar slider.
    :return: None.
    """
    video_url = st.text_input("Video URL")
    uploaded_file = st.file_uploader("Upload video", type=["mp4", "avi", "mov"])

    detect_clicked = st.button("Detect & Encrypt", use_container_width=True)
    st.caption("Supports URL fetch or direct upload.")

    if not detect_clicked:
        return

    video_path = "temp_input_video.mp4"

    if video_url and not uploaded_file:
        try:
            content = download_file(video_url, timeout=60)
            with open(video_path, "wb") as fh:
                fh.write(content)
        except Exception as exc:
            st.error(f"Failed to load video from URL: {exc}")
            return
    elif uploaded_file:
        with open(video_path, "wb") as fh:
            fh.write(uploaded_file.getvalue())
    else:
        st.warning("Please provide a URL or upload a video file.")
        return

    try:
        cap = cv2.VideoCapture(video_path)
        total_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()

        if total_frame_count > 1500:
            st.warning(
                "Video is long (>1500 frames). Processing may take a while "
                "and could fail due to memory limits."
            )

        with st.spinner("Processing video..."):
            progress_bar = st.progress(0)
            start_time = time.time()

            processed_frames, fps, size = process_video(
                video_path,
                model,
                key_seed,
                progress_callback=lambda p: progress_bar.progress(p),
            )
            output_video_path = "encrypted_output_video.mp4"
            create_video_from_frames(
                processed_frames, fps, output_video_path, audio_path=video_path
            )
            elapsed_time = time.time() - start_time
            progress_bar.empty()

        st.markdown('<div class="results-head">Result Overview</div>', unsafe_allow_html=True)
        metric_cols = st.columns(4)
        metric_cols[0].metric("Media Type", "Video")
        metric_cols[1].metric("Frames", total_frame_count)
        metric_cols[2].metric("FPS", f"{fps:.2f}")
        metric_cols[3].metric("Runtime", f"{elapsed_time:.2f}s")

        st.video(output_video_path)

        with open(output_video_path, "rb") as fh:
            st.download_button(
                label="Download Encrypted Video",
                data=fh,
                file_name="encrypted_video.mp4",
                mime="video/mp4",
            )
    finally:
        for temp_file in (video_path, "encrypted_output_video.mp4"):
            if os.path.exists(temp_file):
                os.remove(temp_file)


def main() -> None:
    """
    Main Streamlit application entry point.

    Renders the full UI including hero section, research metadata, model
    settings, media controls, and result display.

    :return: None.
    """
    inject_styles()
    render_hero()
    render_research_meta()

    default_model_path = BUNDLED_MODEL_PATH

    with st.expander("Model Settings", expanded=False):
        model_path = st.text_input("YOLOv8 Weights (.pt)", value=default_model_path)

    if not os.path.isfile(model_path):
        st.warning(f"Model file '{model_path}' not found. Please provide a valid path.")
        st.stop()

    with st.spinner("Loading YOLOv8 model..."):
        model = load_cached_model(model_path)

    left_col, right_col = st.columns(2, gap="large")

    with left_col:
        with st.container(border=True):
            st.markdown(
                """
                <div class="control-head">
                    <div class="section-kicker">Mission Flow</div>
                    <div class="section-title">Load media, detect plate, encrypt region</div>
                    <p class="section-copy">
                        Choose image or video input, then run targeted protection. Original content
                        stays intact outside detected plate bounds.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            input_type = st.radio("Media Type", ["Image", "Video"], horizontal=True)

    with right_col:
        with st.container(border=True):
            st.markdown(
                """
                <div class="control-head">
                    <div class="section-kicker">Encryption Dial</div>
                    <div class="section-title">Chaotic key control</div>
                    <p class="section-copy">
                        Smaller seed changes create different chaotic sequences for plate masking.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            key_seed = st.slider(
                "Encryption Key Seed", 0.001, 0.999, 0.5, step=0.001
            )

    if input_type == "Image":
        handle_image_processing(model, key_seed)
    else:
        handle_video_processing(model, key_seed)


if __name__ == "__main__":
    main()
