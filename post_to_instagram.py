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

def publish_carousel(image_paths, caption_text, handle="your_account", profile_dir=DEFAULT_PROFILE_DIR, headless=True, auto_share=False):
    print("=" * 60)
    print(f"  Instagram Automated Carousel Publisher - @{handle}")
    print("=" * 60)
    print(f"[*] Total slides to upload: {len(image_paths)}")
    print(f"[*] Headless mode: {headless}")
    print(f"[*] Auto-share: {auto_share}")

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
        page.goto("https://www.instagram.com/", wait_until="networkidle")

        # Dismiss notification prompt if present
        not_now = page.locator('button:has-text("Not Now")')
        if not_now.count() > 0:
            print("[*] Dismissed 'Not Now' prompt.")
            not_now.first.click()
            page.wait_for_timeout(1000)

        # 1. Click '+' Create
        print("[*] Clicking Create button...")
        page.locator('svg[aria-label="New post"]').first.click()

        # 2. Wait for submenu and click 'Post'
        print("[*] Selecting 'Post' from create menu...")
        page.wait_for_selector('svg[aria-label="Post"]', timeout=5000)
        page.locator('svg[aria-label="Post"]').locator('xpath=..').click()
        page.wait_for_timeout(2000)

        # 3. Upload file(s)
        print("[*] Attaching slide images to file input...")
        abs_paths = [os.path.abspath(p) for p in image_paths]
        file_input = page.locator('input[type="file"]').first
        file_input.set_input_files(abs_paths)
        page.wait_for_timeout(4000)

        # 4. Aspect ratio selection (4:5 portrait)
        try:
            crop_btn = page.locator('button:has(svg[aria-label="Select crop"])')
            if crop_btn.count() > 0:
                print("[*] Setting aspect ratio to Portrait (4:5)...")
                crop_btn.first.click()
                page.wait_for_timeout(1000)
                portrait_option = page.locator('button:has-text("4:5"), div[role="button"]:has-text("4:5")')
                if portrait_option.count() > 0:
                    portrait_option.first.click()
                    page.wait_for_timeout(1000)
        except Exception as e:
            print(f"[-] Crop adjustment note: {e}")

        # 5. Click Next (Filters)
        print("[*] Proceeding past filter screen...")
        next_btn = page.locator('div[role="button"]:has-text("Next"), button:has-text("Next")').first
        next_btn.click()
        page.wait_for_timeout(2500)

        # 6. Click Next (Caption screen)
        print("[*] Proceeding to caption screen...")
        next_btn = page.locator('div[role="button"]:has-text("Next"), button:has-text("Next")').first
        next_btn.click()
        page.wait_for_timeout(2500)

        # 7. Type Caption into textbox
        print("[*] Writing caption...")
        caption_box = page.locator('div[role="textbox"]').first
        caption_box.click()
        caption_box.fill(caption_text)
        page.wait_for_timeout(2000)

        # 8. Share or Dry Run
        if auto_share:
            print("[*] Clicking 'Share' to publish live...")
            share_btn = page.locator('div[role="dialog"] div[role="button"]').filter(has_text="Share").last
            share_btn.click()
            print("[*] Uploading to Instagram servers...")
            page.wait_for_timeout(25000)
            print(f"[OK] Post shared successfully to @{handle}!")
        else:
            print("\n" + "=" * 60)
            print("  DRY-RUN COMPLETE: Carousel successfully prepared and staged!")
            print(f"  Run with --auto-share to publish live to @{handle}.")
            print("=" * 60)

        context.close()
        return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Instagram Carousel Auto Publisher")
    parser.add_argument("--slides-dir", default=os.path.join("content", "week-1", "carousel-01_slides"), help="Directory containing slide PNGs")
    parser.add_argument("--caption-file", default=None, help="Path to caption text file")
    parser.add_argument("--handle", default="your_account", help="Your Instagram handle")
    parser.add_argument("--profile-dir", default=DEFAULT_PROFILE_DIR, help="Path to browser profile directory")
    parser.add_argument("--auto-share", action="store_true", help="Publish directly to feed")
    parser.add_argument("--visible", action="store_true", help="Show browser window during upload")
    args = parser.parse_args()

    if os.path.exists(args.slides_dir):
        slides = [os.path.join(args.slides_dir, f) for f in sorted(os.listdir(args.slides_dir)) if f.endswith(".png")]
    else:
        slides = []

    if args.caption_file and os.path.exists(args.caption_file):
        with open(args.caption_file, "r", encoding="utf-8") as f:
            caption = f.read()
    else:
        caption = """5 game-changing productivity workflows that save 10+ hours every week.

Comment GUIDE below and I'll send you the complete step-by-step setup!

#productivity #techhacks #aitools #workflows"""

    if not slides:
        print(f"[-] No slides found in {args.slides_dir}. Please render slides first.")
        sys.exit(1)

    publish_carousel(
        image_paths=slides,
        caption_text=caption,
        handle=args.handle,
        profile_dir=args.profile_dir,
        headless=not args.visible,
        auto_share=args.auto_share
    )
