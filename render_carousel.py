import os
from playwright.sync_api import sync_playwright

CHROME_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
if not os.path.exists(CHROME_PATH):
    CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

def render_slides(html_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    abs_html_path = os.path.abspath(html_path)

    print(f"[*] Rendering slides from: {html_path}")
    print(f"[*] Output directory: {output_dir}")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME_PATH if os.path.exists(CHROME_PATH) else None,
            headless=True
        )
        page = browser.new_page(viewport={"width": 1080, "height": 1350, "device_scale_factor": 1})
        page.goto(f"file:///{abs_html_path}", wait_until="networkidle")

        slides = page.locator("section.slide")
        count = slides.count()
        print(f"[*] Found {count} slides.")

        for i in range(count):
            slide = slides.nth(i)
            output_file = os.path.join(output_dir, f"slide_{i+1:02d}.png")
            slide.screenshot(path=output_file)
            print(f"    [+] Saved Slide {i+1}/{count} -> {output_file}")

        browser.close()
        print("[OK] All slides rendered successfully at 1080x1350!")

if __name__ == "__main__":
    import sys
    html_file = sys.argv[1] if len(sys.argv) > 1 else "content/week-1/carousel-01.html"
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "content/week-1/carousel-01_slides"
    render_slides(html_file, out_dir)
