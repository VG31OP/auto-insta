import os
import sys
import time
import argparse
import subprocess
from playwright.sync_api import sync_playwright

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

def render_viral_reel(html_path, audio_path=None, output_mp4="output_reel.mp4", step_delays=None):
    record_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_video_record")
    os.makedirs(record_dir, exist_ok=True)
    abs_html = os.path.abspath(html_path)

    print(f"[*] Rendering Reel from {abs_html}...")
    if audio_path:
        print(f"[*] Synchronizing voiceover: {audio_path}...")

    browser_exe = find_system_browser()

    if step_delays is None:
        step_delays = [3500, 6000, 6000, 6000, 4300]

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=browser_exe,
            headless=True
        )

        context = browser.new_context(
            viewport={"width": 1080, "height": 1920},
            record_video_dir=record_dir,
            record_video_size={"width": 1080, "height": 1920}
        )

        page = context.new_page()
        page.goto(f"file:///{abs_html}", wait_until="networkidle")

        for idx, delay in enumerate(step_delays):
            print(f"    [+] Recording Beat {idx+1}/{len(step_delays)} ({delay/1000}s)...")
            try:
                page.evaluate(f"window.setStep({idx})")
            except Exception:
                pass
            page.wait_for_timeout(delay)

        page.close()
        context.close()
        browser.close()

    webm_files = [os.path.join(record_dir, f) for f in os.listdir(record_dir) if f.endswith(".webm")]
    if not webm_files:
        print("[!] No recorded video found.")
        return None

    raw_webm = webm_files[-1]
    print(f"[*] Raw video captured: {raw_webm}")

    # Combine video + voiceover with FFmpeg
    os.makedirs(os.path.dirname(os.path.abspath(output_mp4)), exist_ok=True)
    print(f"[*] Merging video + audio into {output_mp4}...")
    
    if audio_path and os.path.exists(audio_path):
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-i", raw_webm,
            "-i", os.path.abspath(audio_path),
            "-c:v", "libx264",
            "-profile:v", "high",
            "-level", "4.2",
            "-pix_fmt", "yuv420p",
            "-r", "30",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            output_mp4
        ]
    else:
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-i", raw_webm,
            "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
            "-c:v", "libx264",
            "-profile:v", "high",
            "-level", "4.2",
            "-pix_fmt", "yuv420p",
            "-r", "30",
            "-c:a", "aac",
            "-b:a", "128k",
            "-shortest",
            output_mp4
        ]

    subprocess.run(ffmpeg_cmd, check=True)
    print(f"[OK] Full Voiceover Reel generated successfully: {output_mp4}!")

    for f in webm_files:
        try: os.remove(f)
        except: pass
    try: os.rmdir(record_dir)
    except: pass

    return os.path.abspath(output_mp4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render Kinetic Motion Graphics Reel Video")
    parser.add_argument("--html", default="content/week-1/reel_secret_websites.html", help="Path to HTML template")
    parser.add_argument("--audio", default=None, help="Path to voiceover MP3 audio (optional)")
    parser.add_argument("--output", default="content/week-1/rendered_reel.mp4", help="Output MP4 path")
    args = parser.parse_args()

    render_viral_reel(args.html, args.audio, args.output)
