import os
import sys
import time
import argparse
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

DEFAULT_PROFILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".browser_profile")

def publish_reel(video_path, cover_path=None, caption_text="", first_comment=None, handle="your_account", profile_dir=DEFAULT_PROFILE_DIR, headless=True):
    print("=" * 60)
    print(f"  Publishing Reel with Voiceover & Cover to @{handle}")
    print("=" * 60)
    print(f"[*] Target video file: {video_path}")
    if cover_path:
        print(f"[*] Custom cover image: {cover_path}")

    browser_exe = find_system_browser()

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            executable_path=browser_exe,
            headless=headless,
            viewport={"width": 1280, "height": 900},
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = context.pages[0] if context.pages else context.new_page()

        print("[*] Navigating to Instagram...")
        page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

        # Dismiss notification prompt if present
        not_now = page.locator('button:has-text("Not Now")')
        if not_now.count() > 0:
            not_now.first.click()
            page.wait_for_timeout(1000)

        # 1. Click Create (+)
        print("[*] Clicking Create button...")
        page.locator('svg[aria-label="New post"]').first.click()

        # 2. Click Post in submenu
        print("[*] Selecting 'Post' in menu...")
        page.wait_for_selector('svg[aria-label="Post"]', timeout=5000)
        page.locator('svg[aria-label="Post"]').locator('xpath=..').click()
        page.wait_for_timeout(2000)

        # 3. Attach MP4 video
        print("[*] Uploading MP4 video...")
        file_input = page.locator('input[type="file"]').first
        file_input.set_input_files([os.path.abspath(video_path)])
        page.wait_for_timeout(6000)

        # Dismiss "Video posts are now shared as reels" notice if present
        ok_btn = page.locator('button:has-text("OK"), div[role="button"]:has-text("OK")')
        if ok_btn.count() > 0:
            ok_btn.first.click()
            page.wait_for_timeout(1000)

        # 4. Aspect Ratio (9:16)
        try:
            crop_btn = page.locator('button:has(svg[aria-label="Select crop"])')
            if crop_btn.count() > 0:
                print("[*] Setting aspect ratio to 9:16...")
                crop_btn.first.click()
                page.wait_for_timeout(1000)
                portrait_option = page.locator('button:has-text("9:16"), div[role="button"]:has-text("9:16")')
                if portrait_option.count() > 0:
                    portrait_option.first.click()
                    page.wait_for_timeout(1000)
        except Exception:
            pass

        # 5. Click Next (Cover / Trim screen)
        print("[*] Advancing to cover screen...")
        next_btn = page.locator('div[role="button"]:has-text("Next"), button:has-text("Next")').first
        next_btn.click()
        page.wait_for_timeout(3000)

        # Attach custom cover if specified
        if cover_path and os.path.exists(cover_path):
            print(f"[*] Attaching custom cover photo: {cover_path}...")
            img_inputs = page.locator('input[accept*="image"]')
            if img_inputs.count() > 0:
                img_inputs.first.set_input_files([os.path.abspath(cover_path)])
                page.wait_for_timeout(3000)
            else:
                select_comp = page.locator('button:has-text("Select from computer"), div[role="button"]:has-text("Select from computer")')
                if select_comp.count() > 0:
                    with page.expect_file_chooser() as fc:
                        select_comp.first.click()
                    fc.value.set_files(os.path.abspath(cover_path))
                    page.wait_for_timeout(3000)

        # 6. Click Next (Caption screen)
        print("[*] Advancing to caption screen...")
        next_btn = page.locator('div[role="button"]:has-text("Next"), button:has-text("Next")').first
        next_btn.click()
        page.wait_for_timeout(3000)

        # 7. Type Caption
        print("[*] Writing caption...")
        caption_box = page.locator('div[role="textbox"]').first
        caption_box.click()
        caption_box.fill(caption_text)
        page.wait_for_timeout(2000)

        # 8. Click Share
        print("[*] Clicking Share button to publish Reel live...")
        share_btn = page.locator('div[role="dialog"] div[role="button"]').filter(has_text="Share").last
        share_btn.click()

        print("[*] Processing Reel upload on Instagram servers (35s)...")
        page.wait_for_timeout(35000)

        # Optional first comment
        if first_comment:
            print("[*] Navigating to profile to post author's first comment...")
            page.goto(f"https://www.instagram.com/{handle}/", wait_until="domcontentloaded")
            page.wait_for_selector('header section', timeout=15000)
            page.wait_for_timeout(3000)

            posts = page.locator('a[href*="/reel/"], a[href*="/p/"]')
            if posts.count() > 0:
                posts.first.click()
                page.wait_for_timeout(3000)
                comment_box = page.locator('textarea[aria-label*="comment" i], div[role="textbox"]').first
                if comment_box.count() > 0:
                    comment_box.click()
                    comment_box.fill(first_comment)
                    page.wait_for_timeout(1000)
                    post_btn = page.locator('div[role="button"]:has-text("Post"), button:has-text("Post")').first
                    if post_btn.count() > 0:
                        post_btn.click()
                        print("[OK] First comment posted!")
                        page.wait_for_timeout(3000)

        print(f"[OK] Viral Voiceover Reel published successfully to @{handle}!")
        context.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated Instagram Reel Publisher")
    parser.add_argument("--video", required=True, help="Path to MP4 video file")
    parser.add_argument("--cover", default=None, help="Path to custom cover image file (optional)")
    parser.add_argument("--caption", default="Check out these secret AI tools and digital workflows. Comment TOOL for direct links!", help="Caption text")
    parser.add_argument("--first-comment", default=None, help="Pinned author first comment (optional)")
    parser.add_argument("--handle", default="your_account", help="Your Instagram handle")
    parser.add_argument("--profile-dir", default=DEFAULT_PROFILE_DIR, help="Path to browser profile directory")
    parser.add_argument("--visible", action="store_true", help="Run with visible browser window")
    args = parser.parse_args()

    publish_reel(
        video_path=args.video,
        cover_path=args.cover,
        caption_text=args.caption,
        first_comment=args.first_comment,
        handle=args.handle,
        profile_dir=args.profile_dir,
        headless=not args.visible
    )
