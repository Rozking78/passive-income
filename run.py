#!/usr/bin/env python3
"""
FULL AUTOMATION RUNNER
======================
One command to generate videos and post to TikTok automatically.

Setup (one time):
    python run.py setup

Daily automation:
    python run.py auto

Manual control:
    python run.py generate 5    # Generate 5 videos
    python run.py post          # Post next video from queue
    python run.py status        # Show status

Run continuously:
    python run.py daemon        # Runs 24/7, posts at optimal times
"""

import os
import sys
from pathlib import Path

# Set up environment
os.environ.setdefault("PEXELS_API_KEY", "jCoYtpG8sEh6kxXRY5VvIs3R7JM4BNA7KKTPWWx0aGH5I6LH42ZpZ53h")

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))


def show_banner():
    print("""
╔══════════════════════════════════════════════════════════════════╗
║           PASSIVE INCOME AUTOMATION SYSTEM v2.0                  ║
║                   Target: $10,000 / week                         ║
╠══════════════════════════════════════════════════════════════════╣
║  Commands:                                                       ║
║    setup     - First-time setup (login to TikTok)               ║
║    auto      - Run full automation cycle                         ║
║    generate  - Generate videos only                              ║
║    post      - Post next video to TikTok                        ║
║    status    - Show current status                               ║
║    daemon    - Run continuously (24/7 automation)               ║
╚══════════════════════════════════════════════════════════════════╝
    """)


def check_dependencies():
    """Check if all required packages are installed"""
    missing = []

    try:
        import selenium
    except ImportError:
        missing.append("selenium")

    try:
        from webdriver_manager.chrome import ChromeDriverManager
    except ImportError:
        missing.append("webdriver-manager")

    try:
        import edge_tts
    except ImportError:
        missing.append("edge-tts")

    try:
        from PIL import Image
    except ImportError:
        missing.append("Pillow")

    if missing:
        print("❌ Missing dependencies:")
        for pkg in missing:
            print(f"   - {pkg}")
        print(f"\nInstall with: pip install {' '.join(missing)}")
        return False

    return True


def setup():
    """First-time setup"""
    print("\n🔧 FIRST-TIME SETUP")
    print("=" * 60)

    # Check dependencies
    if not check_dependencies():
        print("\nPlease install missing dependencies first.")
        return

    # Step 1: TikTok login
    print("\n📱 Step 1: TikTok Login")
    print("-" * 40)
    print("This will open a browser for you to login to TikTok.")
    print("Your session will be saved for automatic posting.")

    response = input("\nReady to login? (y/n): ").strip().lower()
    if response == 'y':
        from src.video_engine.tiktok_uploader import TikTokUploader
        uploader = TikTokUploader()
        try:
            uploader.login(manual=True)
        finally:
            uploader.close()

    # Step 2: Affiliate links
    print("\n🔗 Step 2: Affiliate Links")
    print("-" * 40)

    config_path = Path("config/affiliates.json")
    if config_path.exists():
        print("Affiliate config found!")
    else:
        print("Enter your affiliate links (or press Enter to skip):\n")

        affiliates = {}

        jasper = input("Jasper affiliate link: ").strip()
        if jasper:
            affiliates["jasper"] = jasper

        copyai = input("Copy.ai affiliate link: ").strip()
        if copyai:
            affiliates["copyai"] = copyai

        writesonic = input("Writesonic affiliate link: ").strip()
        if writesonic:
            affiliates["writesonic"] = writesonic

        if affiliates:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            import json
            with open(config_path, "w") as f:
                json.dump(affiliates, f, indent=2)
            print(f"\n✓ Saved to {config_path}")

    # Step 3: Linktree
    print("\n🌳 Step 3: Link-in-Bio")
    print("-" * 40)
    linktree = input("Your Linktree/link-in-bio URL (for video CTAs): ").strip()
    if linktree:
        # Save to config
        config_path = Path("config/settings_custom.json")
        import json
        settings = {}
        if config_path.exists():
            with open(config_path) as f:
                settings = json.load(f)
        settings["linktree"] = linktree
        with open(config_path, "w") as f:
            json.dump(settings, f, indent=2)
        print(f"✓ Saved!")

    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Run: python run.py auto")
    print("  2. Videos will be generated and posted automatically")
    print("\nOr run daemon mode for 24/7 automation:")
    print("  python run.py daemon")


def run_auto(count: int = 3):
    """Run full automation cycle"""
    print("\n🚀 RUNNING FULL AUTOMATION")
    print("=" * 60)

    from src.video_engine.scheduler import ContentScheduler

    scheduler = ContentScheduler()
    scheduler.videos_per_day = count
    scheduler.run_cycle()


def generate(count: int = 3):
    """Generate videos only"""
    print(f"\n📹 GENERATING {count} VIDEOS")
    print("=" * 60)

    from automate import FullAutomation

    automation = FullAutomation(niche="ai writing tools")
    automation.run_cycle(num_videos=count, auto_post=False)


def post():
    """Post next video from queue"""
    print("\n📤 POSTING NEXT VIDEO")
    print("=" * 60)

    from src.video_engine.tiktok_uploader import TikTokUploader

    uploader = TikTokUploader()
    try:
        uploaded = uploader.upload_from_queue(limit=1)
        if uploaded:
            print("\n✅ Video posted successfully!")
        else:
            print("\n⚠️ No videos to post or upload failed")
    finally:
        uploader.close()


def status():
    """Show current status"""
    print("\n📊 SYSTEM STATUS")
    print("=" * 60)

    from src.video_engine.scheduler import ContentScheduler

    scheduler = ContentScheduler()
    scheduler.show_status()

    # Queue details
    queue_path = Path("content/tiktok_queue")
    if queue_path.exists():
        print("\n📁 Queue Contents:")
        import json
        for json_file in sorted(queue_path.glob("*.json"))[-5:]:
            with open(json_file) as f:
                meta = json.load(f)
            status = "✓ Posted" if meta.get("status") == "posted" else "⏳ Pending"
            print(f"   {json_file.stem}: {status}")


def daemon():
    """Run in daemon mode"""
    print("\n🤖 STARTING DAEMON MODE")
    print("=" * 60)
    print("This will run continuously and post at optimal times.")
    print("Press Ctrl+C to stop.\n")

    from src.video_engine.scheduler import ContentScheduler

    scheduler = ContentScheduler()
    scheduler.run_daemon()


def main():
    show_banner()

    if len(sys.argv) < 2:
        print("Usage: python run.py <command>")
        print("\nCommands: setup, auto, generate, post, status, daemon")
        return

    command = sys.argv[1].lower()

    if command == "setup":
        setup()
    elif command == "auto":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        run_auto(count)
    elif command == "generate":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        generate(count)
    elif command == "post":
        post()
    elif command == "status":
        status()
    elif command == "daemon":
        daemon()
    else:
        print(f"Unknown command: {command}")
        print("Commands: setup, auto, generate, post, status, daemon")


if __name__ == "__main__":
    main()
