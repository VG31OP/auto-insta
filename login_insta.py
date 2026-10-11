import os
import sys
import time
import argparse
from playwright.sync_api import sync_playwright

DEFAULT_PROFILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".browser_profile")

def find_system_browser():
    candidates = [
        ("Brave", r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"),
        ("Google Chrome", r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        ("Microsoft Edge", r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    ]
    for name, path in candidates:
        if os.path.exists(path):
            return name, path
    return "Default Chromium", None

def main():
    parser = argparse.ArgumentParser(description="Instagram Session Initializer")
    parser.add_argument("--handle", default="your_account", help="Your Instagram handle")
    parser.add_argument("--profile-dir", default=DEFAULT_PROFILE_DIR, help="Path to persistent browser profile")
    args = parser.parse_args()

    browser_name, browser_exe = find_system_browser()

    print("=" * 60)
    print(f"  Instagram Session Initializer - @{args.handle} ({browser_name})")
    print("=" * 60)
    print(f"\n[1/3] Launching {browser_name} window...")

    os.makedirs(args.profile_dir, exist_ok=True)

    with sync_playwright() as p:
        launch_kwargs = {
            "user_data_dir": args.profile_dir,
            "headless": False,
            "viewport": {"width": 1280, "height": 850},
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--start-maximized"
            ]
        }
        if browser_exe:
            launch_kwargs["executable_path"] = browser_exe

        context = p.chromium.launch_persistent_context(**launch_kwargs)
        page = context.pages[0] if context.pages else context.new_page()

        print("[2/3] Opening https://www.instagram.com/ ...")
        page.goto("https://www.instagram.com/", wait_until="domcontentloaded")

        print("\n" + "*" * 60)
        print("  ACTION REQUIRED IN BROWSER WINDOW:")
        print(f"  1. Log in to your Instagram account (@{args.handle}).")
        print("  2. Complete 2FA / verification if prompted.")
        print("  3. Check 'Save Info' so Instagram remembers this session.")
        print("*" * 60 + "\n")
        print("Waiting for login detection... (Press Ctrl+C if you need to cancel)")

        logged_in = False
        for _ in range(180):  # Wait up to 3 minutes
            time.sleep(2)
            try:
                if (page.locator('svg[aria-label="Home"]').count() > 0 or
                    page.locator('svg[aria-label="Direct"]').count() > 0 or
                    page.locator('svg[aria-label="New post"]').count() > 0 or
                    "instagram.com/accounts/onetap" in page.url or
                    (page.locator('nav').count() > 0 and "login" not in page.url)):
                    logged_in = True
                    break
            except Exception:
                pass

        if logged_in:
            print("\n[3/3] Login detected successfully! Saving session...")
            time.sleep(3)
            print(f"Session saved permanently to {args.profile_dir}!")
            print("Done! You can close the browser.")
        else:
            print(f"\nIf you logged in, your session is saved in {args.profile_dir}.")

        context.close()

if __name__ == "__main__":
    main()
