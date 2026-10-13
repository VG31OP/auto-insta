import os
import sys
import time
import argparse
import subprocess
from playwright.sync_api import sync_playwright
from render_pro_audio import mix_pro_soundtrack

def find_system_browser():
    candidates = [
        ("Brave", r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"),
        ("Google Chrome", r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        ("Microsoft Edge", r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    ]
    for name, path in candidates:
        if os.path.exists(path):
            return path
    return None

def render_viral_reel(html_path, audio_path=None, output_mp4="output_reel.mp4", step_delays=None, fps=30):
    """
    Renders 10/10 studio-grade Motion Graphics Reel with GSAP physics,
    ambient glow shaders, multi-track audio layering (ducked BGM + SFX), and H.264 CRF 17 mastering.
    """
    record_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_video_record")
    os.makedirs(record_dir, exist_ok=True)
    abs_html = os.path.abspath(html_path)

    if step_delays is None:
        step_delays = [3400, 6000, 6000, 6000, 4600]

    total_duration_sec = sum(step_delays) / 1000.0

    # Calculate exact beat timestamps in seconds
    beat_timestamps = []
    current_t = 0.0
    for d in step_delays:
        beat_timestamps.append(round(current_t, 2))
        current_t += d / 1000.0

    print("=" * 65)
    print("  PRO MOTION REEL RENDER PIPELINE (10/10 Studio Quality)")
    print("=" * 65)
    print(f"[*] Template: {abs_html}")
    print(f"[*] Total Reel Duration: {total_duration_sec:.2f}s across {len(step_delays)} beats")
    print(f"[*] Beat Markers: {beat_timestamps}")

    # Step 1: Master Multi-Track Soundtrack if audio provided
    mastered_audio = None
    if audio_path and os.path.exists(audio_path):
        temp_master_audio = os.path.join(record_dir, "mastered_bus.aac")
        mastered_audio, _ = mix_pro_soundtrack(
            voiceover_path=audio_path,
            beat_timestamps=beat_timestamps,
            output_path=temp_master_audio,
            duration=total_duration_sec
        )

    # Step 2: Record High-Framerate Video in Headless Browser
    browser_exe = find_system_browser()
    print(f"[*] Launching hardware-accelerated Chromium ({browser_exe})...")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=browser_exe,
            headless=True,
            args=[
                "--enable-gpu-rasterization",
                "--enable-zero-copy",
                "--disable-gpu-vsync",
                "--ignore-gpu-blocklist",
                "--autoplay-policy=no-user-gesture-required",
                "--disable-blink-features=AutomationControlled"
            ]
        )

        context = browser.new_context(
            viewport={"width": 1080, "height": 1920},
            record_video_dir=record_dir,
            record_video_size={"width": 1080, "height": 1920}
        )

        page = context.new_page()
        page.goto(f"file:///{abs_html}", wait_until="networkidle")

        for idx, delay in enumerate(step_delays):
            delay_sec = delay / 1000.0
            print(f"    [+] Animating Beat {idx+1}/{len(step_delays)} (Timestamp {beat_timestamps[idx]}s, Hold {delay_sec}s)...")
            try:
                page.evaluate(f"window.setStep({idx}, {delay_sec})")
            except Exception as e:
                print(f"    [!] Warning calling setStep: {e}")
            page.wait_for_timeout(delay)

        page.close()
        context.close()
        browser.close()

    webm_files = [os.path.join(record_dir, f) for f in os.listdir(record_dir) if f.endswith(".webm")]
    if not webm_files:
        print("[!] Error: No recorded video stream found.")
        return None

    raw_webm = webm_files[-1]
    print(f"[*] Raw video stream captured: {raw_webm}")

    # Step 3: FFmpeg Studio Mastering Pass (CRF 17, 30fps butter-smooth, AAC 320k)
    os.makedirs(os.path.dirname(os.path.abspath(output_mp4)), exist_ok=True)
    print(f"[*] Encoding final 10/10 master MP4: {output_mp4}...")

    if mastered_audio and os.path.exists(mastered_audio):
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-i", raw_webm,
            "-i", mastered_audio,
            "-c:v", "libx264",
            "-crf", "17",
            "-preset", "slow",
            "-profile:v", "high",
            "-level", "4.2",
            "-pix_fmt", "yuv420p",
            "-r", str(fps),
            "-c:a", "aac",
            "-b:a", "320k",
            "-ar", "48000",
            "-movflags", "+faststart",
            "-shortest",
            output_mp4
        ]
    else:
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-i", raw_webm,
            "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
            "-c:v", "libx264",
            "-crf", "17",
            "-preset", "slow",
            "-profile:v", "high",
            "-level", "4.2",
            "-pix_fmt", "yuv420p",
            "-r", str(fps),
            "-c:a", "aac",
            "-b:a", "192k",
            "-movflags", "+faststart",
            "-shortest",
            output_mp4
        ]

    subprocess.run(ffmpeg_cmd, check=True)
    print(f"[SUCCESS] Studio Master Reel exported to: {output_mp4}")

    # Clean up temp recordings
    for f in os.listdir(record_dir):
        try: os.remove(os.path.join(record_dir, f))
        except: pass
    try: os.rmdir(record_dir)
    except: pass

    return os.path.abspath(output_mp4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render Studio Kinetic Motion Graphics Reel")
    parser.add_argument("--html", default="templates/motion_reel_pro.html", help="Path to HTML template")
    parser.add_argument("--audio", default=None, help="Path to voiceover MP3/WAV audio")
    parser.add_argument("--output", default="content/week-1/rendered_pro_reel.mp4", help="Output MP4 path")
    parser.add_argument("--fps", type=int, default=30, help="Framerate (30 or 60)")
    args = parser.parse_args()

    render_viral_reel(
        html_path=args.html,
        audio_path=args.audio,
        output_mp4=args.output,
        fps=args.fps
    )
