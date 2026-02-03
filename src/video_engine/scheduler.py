"""
Content Scheduler
=================
Schedules and runs automated content generation and posting.

Usage:
    # Run once
    python -m src.video_engine.scheduler run

    # Run continuously (daemon mode)
    python -m src.video_engine.scheduler daemon

    # Setup cron job
    python -m src.video_engine.scheduler install
"""

import os
import sys
import json
import time
import schedule
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class ContentScheduler:
    """Manages automated content generation and posting"""

    def __init__(self, config_path: str = "config/schedule.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

        # Posting schedule (optimal TikTok times)
        self.post_times = self.config.get("post_times", ["06:00", "12:00", "18:00", "21:00"])
        self.videos_per_day = self.config.get("videos_per_day", 3)

        # Track what we've done today
        self.today_log_path = Path("data/daily_log.json")
        self.today_log = self._load_today_log()

    def _load_config(self) -> dict:
        """Load scheduler config"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return json.load(f)
        return {}

    def _save_config(self):
        """Save scheduler config"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(self.config, f, indent=2)

    def _load_today_log(self) -> dict:
        """Load today's activity log"""
        today = datetime.now().strftime("%Y-%m-%d")

        if self.today_log_path.exists():
            with open(self.today_log_path) as f:
                log = json.load(f)
                if log.get("date") == today:
                    return log

        return {"date": today, "generated": 0, "posted": 0, "videos": []}

    def _save_today_log(self):
        """Save today's activity log"""
        self.today_log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.today_log_path, "w") as f:
            json.dump(self.today_log, f, indent=2)

    def generate_content(self, count: int = None) -> List[str]:
        """Generate videos for today"""
        count = count or self.videos_per_day

        # Check if we've already generated enough today
        if self.today_log["generated"] >= count:
            print(f"Already generated {self.today_log['generated']} videos today")
            return []

        remaining = count - self.today_log["generated"]
        print(f"\n📹 Generating {remaining} videos...")

        try:
            from automate import FullAutomation
            automation = FullAutomation(niche="ai writing tools")

            # Generate videos
            videos = automation.run_cycle(num_videos=remaining, auto_post=False)

            # Update log
            for video in videos:
                if video.get("path"):
                    self.today_log["videos"].append({
                        "path": video["path"],
                        "generated_at": datetime.now().isoformat(),
                        "posted": False
                    })
                    self.today_log["generated"] += 1

            self._save_today_log()

            return [v["path"] for v in videos if v.get("path")]

        except Exception as e:
            print(f"Generation error: {e}")
            return []

    def post_next_video(self) -> bool:
        """Post the next video from queue"""
        print(f"\n📤 Attempting to post next video...")

        try:
            from src.video_engine.tiktok_uploader import TikTokUploader

            uploader = TikTokUploader()
            uploaded = uploader.upload_from_queue(limit=1)

            if uploaded > 0:
                self.today_log["posted"] += 1
                self._save_today_log()
                print(f"✓ Posted! Total today: {self.today_log['posted']}")
                return True
            else:
                print("No videos to post or upload failed")
                return False

        except Exception as e:
            print(f"Posting error: {e}")
            return False
        finally:
            try:
                uploader.close()
            except:
                pass

    def run_cycle(self):
        """Run a full generation + posting cycle"""
        print("\n" + "=" * 60)
        print(f"🔄 AUTOMATION CYCLE - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 60)

        # Step 1: Generate if needed
        if self.today_log["generated"] < self.videos_per_day:
            self.generate_content()

        # Step 2: Post next video
        if self.today_log["posted"] < self.videos_per_day:
            self.post_next_video()

        # Step 3: Show status
        self.show_status()

    def show_status(self):
        """Show current status"""
        print(f"\n📊 TODAY'S STATUS ({self.today_log['date']})")
        print(f"   Videos generated: {self.today_log['generated']}/{self.videos_per_day}")
        print(f"   Videos posted: {self.today_log['posted']}/{self.videos_per_day}")

        # Queue status
        queue_path = Path("content/tiktok_queue")
        if queue_path.exists():
            pending = 0
            for json_file in queue_path.glob("*.json"):
                with open(json_file) as f:
                    meta = json.load(f)
                    if meta.get("status") != "posted":
                        pending += 1
            print(f"   Videos in queue: {pending}")

    def setup_schedule(self):
        """Setup the posting schedule"""
        print("\n⏰ Setting up posting schedule...")

        for post_time in self.post_times:
            schedule.every().day.at(post_time).do(self.run_cycle)
            print(f"   Scheduled: {post_time}")

        # Also generate content at midnight
        schedule.every().day.at("00:05").do(self.generate_content)
        print(f"   Content generation: 00:05")

    def run_daemon(self):
        """Run continuously in daemon mode"""
        print("\n🤖 STARTING AUTOMATION DAEMON")
        print("=" * 60)
        print(f"Posting times: {', '.join(self.post_times)}")
        print(f"Videos per day: {self.videos_per_day}")
        print("\nPress Ctrl+C to stop\n")

        self.setup_schedule()

        # Run immediately on start
        self.run_cycle()

        # Then follow schedule
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def install_cron(self):
        """Install as a cron job (macOS/Linux)"""
        import subprocess

        script_path = Path(__file__).absolute()
        python_path = sys.executable

        # Create a launcher script
        launcher = Path("run_automation.sh")
        launcher.write_text(f"""#!/bin/bash
cd {Path.cwd()}
export PEXELS_API_KEY="{os.environ.get('PEXELS_API_KEY', '')}"
{python_path} -c "
import sys
sys.path.insert(0, '.')
from src.video_engine.scheduler import ContentScheduler
scheduler = ContentScheduler()
scheduler.run_cycle()
"
""")
        launcher.chmod(0o755)

        print("\n📅 CRON SETUP")
        print("=" * 60)
        print("\nAdd these lines to your crontab (run: crontab -e):\n")

        for post_time in self.post_times:
            hour, minute = post_time.split(":")
            print(f"{minute} {hour} * * * {launcher.absolute()}")

        print(f"\n# Or run every 4 hours:")
        print(f"0 */4 * * * {launcher.absolute()}")

        print(f"\n\nLauncher script created: {launcher.absolute()}")


def main():
    """Entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Content Scheduler")
    parser.add_argument("command", choices=["run", "daemon", "install", "status", "generate", "post"],
                        help="Command to run")
    parser.add_argument("--count", type=int, default=3, help="Number of videos")

    args = parser.parse_args()

    scheduler = ContentScheduler()

    if args.command == "run":
        scheduler.run_cycle()
    elif args.command == "daemon":
        scheduler.run_daemon()
    elif args.command == "install":
        scheduler.install_cron()
    elif args.command == "status":
        scheduler.show_status()
    elif args.command == "generate":
        scheduler.generate_content(args.count)
    elif args.command == "post":
        scheduler.post_next_video()


if __name__ == "__main__":
    main()
