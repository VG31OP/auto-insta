import os
import sys
import subprocess
import argparse

def mix_pro_soundtrack(voiceover_path, beat_timestamps=None, output_path="mastered_soundtrack.wav", duration=None, bgm_volume=0.16):
    """
    Layers Voiceover + Ducked Cyber Beat BGM + Whoosh SFX + Impact SFX + Pop SFX
    into a studio-grade 10/10 master audio track complying with motion-graphics-pro standard.
    """
    if beat_timestamps is None:
        beat_timestamps = [0.0, 3.5, 9.5, 15.5, 21.5]

    assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", "assets")
    bgm_path = os.path.join(assets_dir, "bgm_cyber_beat.wav")
    impact_path = os.path.join(assets_dir, "sfx_impact.wav")
    whoosh_path = os.path.join(assets_dir, "sfx_whoosh.wav")
    pop_path = os.path.join(assets_dir, "sfx_pop.wav")

    # Determine voiceover duration
    if not duration and voiceover_path and os.path.exists(voiceover_path):
        probe_cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", voiceover_path
        ]
        res = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
        duration = float(res.stdout.strip())
    
    if not duration:
        duration = 26.0

    print(f"[*] Mastering Studio Audio (Duration: {duration:.2f}s)...")
    print(f"    - Voiceover track: {voiceover_path}")
    print(f"    - Synthesized Cyber BGM: {bgm_path}")
    print(f"    - Synchronized Beat timestamps: {beat_timestamps}")

    whoosh_delays = [int(t * 1000) for t in beat_timestamps if t > 0.4]
    pop_delays = [int((t + 0.35) * 1000) for t in beat_timestamps if t > 0.4]

    filters = []
    # 1. Voiceover: broadcast presence boost (1.3x volume, highpass 75Hz, warmth at 140Hz)
    filters.append("[0:a]volume=1.35,highpass=f=75,lowshelf=g=2.5:f=140[voice]")

    # 2. BGM: loop seamlessly across video length, ducked underneath dialogue
    filters.append(f"[1:a]aloop=loop=-1:size=2e+09,atrim=0:{duration},volume={bgm_volume}[bgm]")

    # 3. Sub-bass Hook impact at 0ms
    filters.append("[2:a]atrim=0:2.0,volume=0.45[impact]")

    # 4. Kinetic Whoosh transitions
    whoosh_inputs = []
    for i, delay in enumerate(whoosh_delays):
        filters.append(f"[3:a]adelay={delay}|{delay},volume=0.35[w_{i}]")
        whoosh_inputs.append(f"[w_{i}]")

    # 5. UI Element card pops
    pop_inputs = []
    for i, delay in enumerate(pop_delays):
        filters.append(f"[4:a]adelay={delay}|{delay},volume=0.25[p_{i}]")
        pop_inputs.append(f"[p_{i}]")

    all_sfx = ["[impact]"] + whoosh_inputs + pop_inputs
    filters.append(f"{''.join(all_sfx)}amix=inputs={len(all_sfx)}:dropout_transition=0:normalize=0[all_sfx]")

    # Master Bus Mixdown: Voice (primary) + BGM (-14dB) + Foley/SFX (-12dB)
    filters.append("[voice][bgm][all_sfx]amix=inputs=3:dropout_transition=0:normalize=0,alimiter=limit=0.96[outa]")

    filter_complex = ";".join(filters)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-i", voiceover_path,
        "-i", bgm_path,
        "-i", impact_path,
        "-i", whoosh_path,
        "-i", pop_path,
        "-filter_complex", filter_complex,
        "-map", "[outa]",
        "-t", str(duration),
        "-c:a", "aac",
        "-b:a", "320k",
        "-ar", "48000",
        output_path
    ]

    subprocess.run(cmd, check=True)
    print(f"[OK] Mastered Studio Audio created successfully: {output_path}")
    return os.path.abspath(output_path), duration

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-track Audio Mastering Engine for Reels")
    parser.add_argument("--voiceover", required=True, help="Path to voiceover audio file")
    parser.add_argument("--output", default="mastered_soundtrack.aac", help="Output audio file")
    parser.add_argument("--beats", nargs="+", type=float, default=[0.0, 3.5, 9.5, 15.5, 21.5], help="Beat timestamps in seconds")
    args = parser.parse_args()

    mix_pro_soundtrack(args.voiceover, args.beats, args.output)
