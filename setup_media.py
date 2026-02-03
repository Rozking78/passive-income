#!/usr/bin/env python3
"""
Media Setup Script
==================
Downloads royalty-free music and sample videos for viral content creation.

Run this once after installation:
  python setup_media.py

For API access (optional, for more variety):
  1. Get free Pexels API key: https://www.pexels.com/api/
  2. Get free Pixabay API key: https://pixabay.com/api/docs/
  3. Add to your .env file or export:
     export PEXELS_API_KEY="your-key-here"
     export PIXABAY_API_KEY="your-key-here"
"""

import os
import urllib.request
import urllib.error
from pathlib import Path

# Directory structure
STOCK_DIR = Path("content/stock_media")
MUSIC_DIR = STOCK_DIR / "music"
VIDEO_DIR = STOCK_DIR / "videos"

# Royalty-free music URLs (Pixabay Music - no attribution required)
# These are direct download links for CC0 music
MUSIC_SAMPLES = [
    # Motivational/Uplifting tracks
    {
        "name": "inspiring_motivational.mp3",
        "url": "https://cdn.pixabay.com/download/audio/2022/10/25/audio_946b0939c8.mp3",
        "category": "motivational"
    },
    {
        "name": "uplifting_energy.mp3",
        "url": "https://cdn.pixabay.com/download/audio/2022/03/10/audio_c8c8a73467.mp3",
        "category": "motivational"
    },
    {
        "name": "epic_cinematic.mp3",
        "url": "https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0a13f69d2.mp3",
        "category": "dramatic"
    },
]

# Note: For background videos, users should:
# 1. Use the Pexels/Pixabay APIs (free keys)
# 2. Download manually from pexels.com or pixabay.com
# 3. Use the bundled solid color backgrounds (created below)


def download_file(url: str, output_path: Path, description: str = "") -> bool:
    """Download a file with progress indication"""
    try:
        print(f"   Downloading {description or output_path.name}...")

        # Add user agent to avoid 403
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)')

        with urllib.request.urlopen(req, timeout=30) as response:
            with open(output_path, 'wb') as f:
                f.write(response.read())

        print(f"   ✓ Downloaded: {output_path.name}")
        return True
    except urllib.error.HTTPError as e:
        print(f"   ✗ HTTP Error {e.code}: {description or output_path.name}")
        return False
    except urllib.error.URLError as e:
        print(f"   ✗ URL Error: {description or output_path.name} - {e.reason}")
        return False
    except Exception as e:
        print(f"   ✗ Error: {description or output_path.name} - {e}")
        return False


def create_gradient_backgrounds():
    """Create solid/gradient background videos using FFmpeg"""
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("   Pillow not installed, skipping background creation")
        return

    import subprocess

    backgrounds = [
        {"name": "dark_gradient", "colors": [(20, 20, 30), (40, 40, 60)]},
        {"name": "purple_gradient", "colors": [(30, 10, 50), (80, 30, 100)]},
        {"name": "blue_gradient", "colors": [(10, 30, 60), (30, 80, 120)]},
        {"name": "warm_gradient", "colors": [(50, 30, 20), (100, 60, 40)]},
    ]

    for bg in backgrounds:
        print(f"   Creating {bg['name']}...")
        img = Image.new("RGB", (1080, 1920))
        draw = ImageDraw.Draw(img)

        # Create vertical gradient
        for y in range(1920):
            ratio = y / 1920
            r = int(bg['colors'][0][0] * (1-ratio) + bg['colors'][1][0] * ratio)
            g = int(bg['colors'][0][1] * (1-ratio) + bg['colors'][1][1] * ratio)
            b = int(bg['colors'][0][2] * (1-ratio) + bg['colors'][1][2] * ratio)
            draw.line([(0, y), (1080, y)], fill=(r, g, b))

        img_path = VIDEO_DIR / f"{bg['name']}.png"
        img.save(img_path)

        # Convert to 10-second video with FFmpeg
        video_path = VIDEO_DIR / f"{bg['name']}.mp4"
        try:
            subprocess.run([
                "ffmpeg", "-y",
                "-loop", "1",
                "-i", str(img_path),
                "-c:v", "libx264",
                "-t", "10",
                "-pix_fmt", "yuv420p",
                "-vf", "scale=1080:1920",
                str(video_path)
            ], capture_output=True, check=True)
            print(f"   ✓ Created: {bg['name']}.mp4")
            img_path.unlink()  # Remove temp image
        except subprocess.CalledProcessError:
            print(f"   ✗ FFmpeg error creating {bg['name']}.mp4")
        except FileNotFoundError:
            print("   ✗ FFmpeg not found, skipping video creation")
            break


def setup_env_file():
    """Create .env template for API keys"""
    env_path = Path(".env")
    if not env_path.exists():
        env_content = """# API Keys for Stock Media (optional but recommended)
# Get free keys from:
# - Pexels: https://www.pexels.com/api/
# - Pixabay: https://pixabay.com/api/docs/

PEXELS_API_KEY=your-pexels-api-key-here
PIXABAY_API_KEY=your-pixabay-api-key-here
"""
        with open(env_path, 'w') as f:
            f.write(env_content)
        print("   ✓ Created .env template (add your API keys)")
    else:
        print("   ✓ .env already exists")


def main():
    print("=" * 60)
    print("VIRAL VIDEO MEDIA SETUP")
    print("=" * 60)

    # Create directories
    print("\n📁 Creating directories...")
    MUSIC_DIR.mkdir(parents=True, exist_ok=True)
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    print(f"   ✓ {MUSIC_DIR}")
    print(f"   ✓ {VIDEO_DIR}")

    # Download music samples
    print("\n🎵 Downloading royalty-free music...")
    success_count = 0
    for music in MUSIC_SAMPLES:
        output_path = MUSIC_DIR / music['name']
        if output_path.exists():
            print(f"   ✓ Already have: {music['name']}")
            success_count += 1
        else:
            if download_file(music['url'], output_path, music['name']):
                success_count += 1

    print(f"\n   Downloaded {success_count}/{len(MUSIC_SAMPLES)} music tracks")

    # Create gradient backgrounds
    print("\n🎨 Creating gradient backgrounds...")
    create_gradient_backgrounds()

    # Setup env file
    print("\n🔑 Setting up API configuration...")
    setup_env_file()

    # Summary
    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETE")
    print("=" * 60)
    print(f"""
Next steps:
1. (Optional) Add API keys to .env for more video variety:
   - Pexels: https://www.pexels.com/api/
   - Pixabay: https://pixabay.com/api/docs/

2. Test video creation:
   python automate.py run 1

3. Your videos will have:
   - Gradient backgrounds (always available)
   - Stock footage (if API keys configured)
   - Royalty-free music ({success_count} tracks ready)
   - Bold text overlays
   - Viral hooks and CTAs
""")


if __name__ == "__main__":
    main()
