import os
import sys
import time
import json
import argparse
from datetime import datetime
from publish_reel import publish_reel
from post_to_instagram import publish_carousel

SCHEDULE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "content", "week-1", "schedule_queue.json")

DEFAULT_QUEUE = [
    {
        "id": "post_01",
        "day": "Day 1 (Mon)",
        "scheduled_time": "19:30",
        "format": "reel",
        "title": "3 Secret Websites in 2026",
        "video": "content/week-1/reel_secret_websites.mp4",
        "cover": "content/week-1/cover.jpg",
        "caption": "3 secret websites that feel completely illegal to know in 2026.\n\nStop paying for expensive subscriptions. Here are three free tools that solve 90% of your digital chores:\n\n1. TinyWow (tinywow.com) - 200+ free tools to edit PDFs, convert files, and remove backgrounds.\n2. Claude Artifacts (claude.ai) - Turn plain English ideas into full working web apps.\n3. Tome AI (tome.app) - Generate entire presentations, slide decks, and wireframes.\n\nComment TOOL and our bot will send you direct access links right now.\n\n#aitools #productivity #freeai",
        "first_comment": "Which of these 3 tools are you using first? Comment TOOL and I'll DM you direct access links! 🚀",
        "handle": "vrj.ai",
        "status": "published"
    },
    {
        "id": "post_02",
        "day": "Day 2 (Tue)",
        "scheduled_time": "08:30",
        "format": "carousel",
        "title": "5 Smartphone Settings to Turn Off",
        "slides_dir": "content/week-1/carousel-01_slides",
        "caption": "5 smartphone settings draining your battery and tracking your location right now.\n\nSwipe through to see the exact toggles for iOS and Android.\n\nComment PHONE for our full 1-click privacy checklist.\n\n#techhacks #smartphonetricks #privacy",
        "first_comment": "How many of these 5 settings were still turned ON on your phone? Comment PHONE for the direct checklist! 📱",
        "handle": "vrj.ai",
        "status": "pending"
    },
    {
        "id": "post_03",
        "day": "Day 3 (Wed)",
        "scheduled_time": "19:45",
        "format": "reel",
        "title": "Faceless $200/Day AI Blueprint",
        "video": "content/week-1/reel_blueprint.mp4",
        "cover": "content/week-1/cover_blueprint.jpg",
        "caption": "How people make $200/day using free AI tools without showing their face.\n\nHere is the exact 3-step engine:\n1. Claude for high-value Notion prompt templates\n2. Gamma for presentation designs\n3. Gumroad for automated 24/7 fulfillment\n\nComment BLUEPRINT and I'll send you the free template starter pack!\n\n#sidehustle #aitools #makemoneyonline",
        "first_comment": "Ready to launch your first digital product? Comment BLUEPRINT below! 🚀",
        "handle": "vrj.ai",
        "status": "pending"
    },
    {
        "id": "post_04",
        "day": "Day 4 (Thu)",
        "scheduled_time": "13:15",
        "format": "reel",
        "title": "Stop Paying $20/Month for ChatGPT",
        "video": "content/week-1/reel_chatgpt_alts.mp4",
        "cover": "content/week-1/cover_chatgpt_alts.jpg",
        "caption": "Stop paying $20 every month for ChatGPT Plus.\n\nHere are 3 free AI models that are faster, smarter, and completely free in 2026:\n1. DeepSeek R1 for advanced math and logic reasoning\n2. Claude 3.5 Sonnet Artifacts for web development\n3. Perplexity for real-time cited web research\n\nComment FREE-AI and I'll DM you the direct comparison breakdown.\n\n#chatgpt #ai #deepseek",
        "first_comment": "Which AI model are you using most this week? Comment FREE-AI for prompt templates! 💡",
        "handle": "vrj.ai",
        "status": "pending"
    }
]

def load_queue():
    if not os.path.exists(SCHEDULE_FILE):
        save_queue(DEFAULT_QUEUE)
        return DEFAULT_QUEUE
    try:
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_QUEUE

def save_queue(queue):
    os.makedirs(os.path.dirname(os.path.abspath(SCHEDULE_FILE)), exist_ok=True)
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2)

def list_schedule():
    queue = load_queue()
    print("=" * 80)
    print("  INSTAGRAM AUTONOMOUS CONTENT SCHEDULE QUEUE")
    print("=" * 80)
    print(f"{'ID':<10} {'Day':<14} {'Best Time':<10} {'Format':<10} {'Status':<14} {'Title'}")
    print("-" * 80)
    for item in queue:
        status_tag = f"[{item['status'].upper()}]"
        print(f"{item['id']:<10} {item.get('day',''):<14} {item['scheduled_time']:<10} {item['format']:<10} {status_tag:<14} {item['title']}")
    print("=" * 80)

def trigger_item(item):
    print(f"\n[*] Executing Scheduled Post: [{item['id']}] {item['title']}...")
    try:
        if item["format"] == "reel":
            publish_reel(
                video_path=item["video"],
                cover_path=item.get("cover"),
                caption_text=item.get("caption", ""),
                first_comment=item.get("first_comment"),
                handle=item.get("handle", "vrj.ai"),
                headless=True
            )
        elif item["format"] == "carousel":
            slides_dir = os.path.abspath(item["slides_dir"])
            image_paths = [os.path.join(slides_dir, f) for f in sorted(os.listdir(slides_dir)) if f.endswith((".png", ".jpg"))]
            publish_carousel(
                image_paths=image_paths,
                caption_text=item.get("caption", ""),
                handle=item.get("handle", "vrj.ai"),
                headless=True,
                auto_share=True
            )
        item["status"] = "published"
        item["published_at"] = datetime.now().isoformat()
        print(f"[SUCCESS] Post [{item['id']}] successfully published at best time!")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to publish post [{item['id']}]: {e}")
        item["status"] = "failed"
        item["error"] = str(e)
        return False

def run_due_posts(force_id=None):
    queue = load_queue()
    now_time = datetime.now().strftime("%H:%M")
    modified = False

    for item in queue:
        if force_id and item["id"] == force_id:
            trigger_item(item)
            modified = True
            break
        elif not force_id and item["status"] == "pending":
            # Match current time window (within 5 minutes)
            if item["scheduled_time"] == now_time:
                trigger_item(item)
                modified = True

    if modified:
        save_queue(queue)

def run_daemon():
    print("[*] Starting Instagram Autonomous Scheduler Daemon...")
    print("[*] Polling queue every 60 seconds against peak algorithmic time windows...")
    while True:
        try:
            run_due_posts()
        except Exception as e:
            print(f"[!] Daemon error: {e}")
        time.sleep(60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Instagram Autonomous Post Scheduler")
    parser.add_argument("--list", action="store_true", help="List scheduled posts and times")
    parser.add_argument("--daemon", action="store_true", help="Run background scheduler daemon")
    parser.add_argument("--trigger", type=str, help="Manually trigger a specific post ID immediately")
    args = parser.parse_args()

    if args.trigger:
        run_due_posts(force_id=args.trigger)
    elif args.daemon:
        run_daemon()
    else:
        list_schedule()
