# Auto-Insta: Autonomous Instagram Creator Engine 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![Playwright](https://img.shields.io/badge/Browser-Playwright-2EAD33.svg?logo=playwright&logoColor=white)](https://playwright.dev)
[![FFmpeg](https://img.shields.io/badge/Video-FFmpeg-007808.svg?logo=ffmpeg&logoColor=white)](https://ffmpeg.org)

An open-source autonomous agent engine that plans, writes, renders, narrates, and publishes high-performing short-form video **Reels** and swipe **Carousels** to Instagram with zero paid API dependencies.

---

## Key Capabilities

- 🎬 **Kinetic Motion Graphics (1080x1920)**: Generates 60fps vertical videos with kinetic typography, glowing cyberpunk glassmorphic cards, and dynamic beat cards using headless browser rendering.
- 🎙️ **Realistic Neural Voiceover**: Free, high-retention text-to-speech narration powered by Microsoft Edge Neural TTS (`en-US-ChristopherNeural`, `en-US-GuyNeural`, etc.) with zero API keys or monthly costs.
- 🖼️ **Safe-Zone Cover Generator**: Automatically creates 1080x1920 custom cover images designed to crop into 1:1 profile grid tiles and 9:16 Reels feeds.
- 🤖 **Headless Instagram Publishing**: Persistent Chromium/Brave session automation for uploading Reels, configuring 9:16 aspect ratios, attaching custom covers, and formatting captions.
- 💬 **Automated Engagement Lead Magnets**: Instantly posts author engagement comments to trigger DM lead generation funnels (`TOOL`, `BLUEPRINT`, `PHONE`, `FREE-AI`).
- 🧠 **13 Built-in Agent Skills**: Includes specialized AI skills for hook scoring across 26 proven formulas, beat-sheet timing, caption linting, and humanizing text to remove AI slop.

---

## Architecture Overview

```
auto-insta/
├── content/                     # Active content plans, templates, and rendered media
│   └── week-1/
│       ├── reel_secret_websites.html    # 1080x1920 kinetic Reel animation
│       ├── schedule.md                  # Weekly editorial calendar
│       └── dm-funnel.md                 # Automated DM keyword fulfillment scripts
├── skills/                      # 13 agent skills for content optimization
│   ├── ig-reel/                 # Hook scoring & beat-sheet calculation
│   ├── ig-caption/              # Caption linting & feed preview
│   ├── ig-human/                # AI slop detector & vocabulary humanizer
│   ├── ig-carousel/             # Swipe post generation
│   ├── ig-profile/              # 12-part 100-point profile scoring rubric
│   └── ...
├── templates/
│   └── voice.md                 # Default creator voice template
├── login_insta.py               # Interactive one-time browser session initializer
├── render_viral_reel.py         # Headless video renderer (HTML -> WebM -> MP4 + Audio)
├── render_carousel.py           # Multi-slide 1080x1350 carousel PNG generator
├── publish_reel.py              # Automated Reel publisher with cover & comment hooks
├── post_to_instagram.py         # Automated Multi-slide Carousel publisher
├── voice.md                     # Active creator brand & tone profile
└── .env.example                 # Environment configuration template
```

---

## Quick Start

### 1. Prerequisites
- **Python 3.10+**
- **FFmpeg** installed and accessible in your system `PATH`:
  - *Windows*: `winget install Gyan.FFmpeg`
  - *macOS*: `brew install ffmpeg`
  - *Linux*: `sudo apt install ffmpeg`

### 2. Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/VG31OP/auto-insta.git
cd auto-insta
pip install playwright edge-tts
playwright install chromium
```

### 3. Initialize Instagram Session (One-Time)

Launch the authenticated browser session window:

```bash
python login_insta.py --handle your_creator_handle
```

1. Log into your Instagram account in the browser window.
2. Complete 2FA / verification if prompted.
3. Check **Save Info**. Once logged in, your session is saved locally in `.browser_profile/` (excluded from git tracking).

---

## Workflow Guide

### Step 1: Configure Your Brand (`voice.md`)
Edit [`voice.md`](voice.md) to define your niche, target audience, tone of voice, forbidden AI slop words, and keyword call-to-actions.

### Step 2: Synthesize Realistic Neural Voiceover
Use `edge-tts` to generate crisp creator-paced narration:

```bash
edge-tts --voice en-US-ChristopherNeural --rate=+15% \
  --text "3 secret websites that feel illegal to know in 2026..." \
  --write-media content/week-1/voiceover.mp3
```

### Step 3: Render Kinetic Reel Video
Compile the HTML5 motion template and audio track into a broadcast-ready H.264 / AAC vertical video:

```bash
python render_viral_reel.py \
  --html content/week-1/reel_secret_websites.html \
  --audio content/week-1/voiceover.mp3 \
  --output content/week-1/final_reel.mp4
```

### Step 4: Publish Reel Live to Instagram
Upload the video, attach a custom 1080x1920 cover image, write the caption, and post the first engagement comment:

```bash
python publish_reel.py \
  --video content/week-1/final_reel.mp4 \
  --cover content/week-1/cover.jpg \
  --caption "3 secret websites that feel illegal to know in 2026. Comment TOOL for links!" \
  --first-comment "Which of these 3 was your favorite? Comment TOOL and I'll DM you the links! 🚀" \
  --handle your_creator_handle
```

### Step 5: Render & Publish Carousels
Generate 1080x1350 portrait slide PNGs and publish them as a swipe carousel:

```bash
# Render slides
python render_carousel.py content/week-1/carousel-01.html content/week-1/carousel-01_slides

# Publish to Instagram feed
python post_to_instagram.py \
  --slides-dir content/week-1/carousel-01_slides \
  --handle your_creator_handle \
  --auto-share
```

---

## Built-In AI Agent Skills

| Skill | Command | Description |
| :--- | :--- | :--- |
| **Reel Generator** | `/ig-reel` | Scores hooks across 26 formulas, outputs timed script beat sheets. |
| **Viral Research** | `/ig-viral` | Ranks niche content by multiple over account median. |
| **Humanizer** | `/ig-human` | Strips em dashes, invisible watermarks, and 150+ AI slop phrases. |
| **Caption Linter** | `/ig-caption`| Previews feed character cutoff (125 chars) and checks hashtag counts. |
| **Profile Audit** | `/ig-profile`| Scores profile out of 100 on a 12-point conversion rubric. |
| **Carousel Studio**| `/ig-carousel`| Generates 1080x1350 swipe layouts and hook covers. |
| **DM Funnels** | `/ig-dm` | Generates 2-step keyword auto-responder sequences. |
| **Weekly Planner** | `/ig-plan` | Schedules content mix, timings, and daily 15-minute engagement routines. |

---

## Security & Privacy

> [!IMPORTANT]
> **No Credentials Stored in Git**: Your Instagram passwords and authentication cookies are stored exclusively in the local `.browser_profile/` folder, which is strictly ignored in [`.gitignore`](.gitignore). Never commit cookies or session tokens.

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an Issue for new motion templates, voice presets, or platform automations.

---

## License

Released under the [MIT License](LICENSE). Take it, customize it, and build your digital media presence.
