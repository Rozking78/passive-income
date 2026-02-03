#!/usr/bin/env python3
"""
FULL AUTOMATION SYSTEM
======================
One command to generate, create, and post content automatically.

This system:
1. Generates content using AI-powered templates
2. Creates videos automatically
3. Queues for posting (auto-posts where API available)
4. Learns what works and improves over time

Usage:
  python automate.py              # Interactive mode
  python automate.py run          # Run full automation cycle
  python automate.py generate 5   # Generate 5 videos
  python automate.py status       # Show system status
  python automate.py learn        # Show what's working

Requirements:
  pip install moviepy gTTS Pillow
  brew install ffmpeg  (macOS)
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from src.content_engine.auto_generator import AutoContentGenerator
from src.video_engine.video_creator import SimpleVideoCreator, VideoCreator, MOVIEPY_AVAILABLE
from src.video_engine.viral_video_creator import ViralVideoCreator, MotivationalContentGenerator
from src.video_engine.auto_poster import AutoPoster, ContentScheduler, TikTokPoster
from src.video_engine.adaptive_engine import AdaptiveEngine
from src.link_tracker.tracker import LinkTracker


class FullAutomation:
    """Complete automation system"""

    def __init__(self, niche: str = "ai writing tools", use_viral_mode: bool = True):
        self.niche = niche
        self.use_viral_mode = use_viral_mode

        # Initialize all components
        self.content_gen = AutoContentGenerator(niche=niche)
        self.video_creator = SimpleVideoCreator()
        self.viral_creator = ViralVideoCreator()
        self.motivational = MotivationalContentGenerator()
        self.poster = AutoPoster()
        self.scheduler = ContentScheduler()
        self.adaptive = AdaptiveEngine()
        self.link_tracker = LinkTracker()

        # Check capabilities
        self.can_create_video = self.video_creator.check_ffmpeg()

        print(f"🤖 Automation System Initialized")
        print(f"   Niche: {niche}")
        print(f"   Video creation: {'✓' if self.can_create_video else '✗ Install FFmpeg'}")
        print(f"   Viral mode: {'✓ ON' if use_viral_mode else '✗ OFF'}")

    def run_cycle(self, num_videos: int = 3, auto_post: bool = True):
        """
        Run a complete automation cycle:
        1. Get recommendations from adaptive engine
        2. Generate content based on recommendations
        3. Create videos
        4. Queue/post to platforms
        5. Record for learning
        """

        print("\n" + "=" * 60)
        print("🚀 RUNNING AUTOMATION CYCLE")
        print("=" * 60)

        # Step 1: Get AI recommendations
        print("\n📊 Step 1: Getting AI recommendations...")
        recommendations = self.adaptive.get_recommendations()

        preferred_hook = recommendations.get("hook_style", "hook")
        preferred_product = recommendations.get("product", "Jasper")
        preferred_time = recommendations.get("post_time", 12)

        print(f"   Recommended hook: {preferred_hook}")
        print(f"   Recommended product: {preferred_product}")
        print(f"   Recommended time: {preferred_time}:00")

        # Step 2: Generate content
        print(f"\n✍️  Step 2: Generating {num_videos} content pieces...")
        scripts = []

        for i in range(num_videos):
            # Mix of recommended and exploratory content
            if i < num_videos - 1:
                # Use recommended style
                script = self.content_gen.generate_tiktok_script(preferred_hook)
            else:
                # Explore a new style
                script = self.content_gen.generate_tiktok_script("random")

            scripts.append(script)
            print(f"   ✓ Script {i+1}: {script['style']} style for {script['product']}")

        # Step 3: Create videos
        print(f"\n🎬 Step 3: Creating videos...")
        videos = []

        if self.can_create_video:
            for i, script in enumerate(scripts):
                # Extract key text for video
                texts = [
                    script['hook'],
                    script['product'],
                    script.get('cta', 'Link in bio')
                ]

                # Add some content from script
                main_script = script.get('script', '')
                import re
                quotes = re.findall(r'"([^"]*)"', main_script)
                if quotes:
                    texts = [script['hook']] + quotes[:3] + [script.get('cta', 'Link in bio')]

                output_name = f"auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}.mp4"

                # Use viral mode for enhanced videos with backgrounds
                if self.use_viral_mode:
                    # Generate motivational script
                    viral_texts = self.motivational.generate_viral_script(
                        product=script['product'],
                        benefit="saving hours every week"
                    )
                    # Mix original content with viral hooks
                    final_texts = [texts[0]] + viral_texts[1:-1] + [texts[-1]]

                    video_path = self.viral_creator.create_viral_video(
                        texts=final_texts,
                        style="bold_white",
                        add_hook=False,
                        add_voiceover=True,
                        voice_style="motivational",
                        min_cuts=1,  # At least 1 cut (2 clips) - pain → transformation
                        use_psychology_videos=True,  # Psychology-aligned video selection
                        output_name=output_name
                    )
                else:
                    video_path = self.video_creator.create_slideshow_video(
                        texts,
                        output_name=output_name
                    )

                if video_path:
                    videos.append({
                        "path": video_path,
                        "script": script,
                        "content_id": f"auto_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}"
                    })
                    print(f"   ✓ Video {i+1}: {video_path}")
                else:
                    print(f"   ✗ Video {i+1}: Creation failed")
        else:
            print("   ⚠ Video creation skipped (FFmpeg not available)")
            print("   Install with: brew install ffmpeg")

            # Still save scripts for manual use
            for i, script in enumerate(scripts):
                videos.append({
                    "path": None,
                    "script": script,
                    "content_id": f"script_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}"
                })

        # Step 4: Queue for posting
        print(f"\n📱 Step 4: Queuing for posting...")

        for video in videos:
            script = video['script']
            caption = script.get('caption', script.get('hook', ''))
            hashtags = script.get('hashtags', [])

            if video['path']:
                # Queue for TikTok
                meta_path = self.poster.tiktok.queue_video(
                    video['path'],
                    caption,
                    hashtags
                )
                print(f"   ✓ Queued for TikTok: {Path(video['path']).name}")

                # Schedule post record
                self.scheduler.schedule_post(
                    platform="tiktok",
                    content_path=video['path'],
                    caption=caption,
                    hashtags=hashtags
                )
            else:
                # Save script only
                script_path = Path("content/scripts") / f"{video['content_id']}.json"
                script_path.parent.mkdir(parents=True, exist_ok=True)
                with open(script_path, 'w') as f:
                    json.dump(script, f, indent=2)
                print(f"   ✓ Script saved: {script_path}")

            # Record for learning
            self.adaptive.record_content(
                content_id=video['content_id'],
                platform="tiktok",
                content_type="video",
                hook_style=script['style'],
                topic=self.niche,
                product=script['product']
            )

        # Step 5: Summary
        print(f"\n✅ CYCLE COMPLETE")
        print(f"   Generated: {len(scripts)} scripts")
        print(f"   Videos created: {len([v for v in videos if v['path']])}")
        print(f"   Queued for posting: {len(videos)}")

        # Show next steps
        queue = self.poster.tiktok.get_queue()
        pending = [q for q in queue if q.get('status') == 'queued']

        print(f"\n📋 NEXT STEPS:")
        print(f"   1. Go to content/tiktok_queue/")
        print(f"   2. Upload {len(pending)} videos to TikTok")
        print(f"   3. Use captions from the .json files")
        print(f"   4. Run 'python automate.py learn' after posting")

        return videos

    def show_status(self):
        """Show full system status"""

        print("\n" + "=" * 60)
        print("📊 SYSTEM STATUS")
        print("=" * 60)

        # Component status
        print("\n🔧 COMPONENTS:")
        print(f"   Content Generator: ✓ Ready")
        print(f"   Video Creator: {'✓ Ready' if self.can_create_video else '✗ Need FFmpeg'}")
        print(f"   Auto Poster: ✓ Ready (TikTok via queue)")
        print(f"   Adaptive Engine: ✓ Learning")

        # Content queue
        queue = self.poster.tiktok.get_queue()
        pending = [q for q in queue if q.get('status') == 'queued']
        posted = [q for q in queue if q.get('status') == 'posted']

        print(f"\n📱 TIKTOK QUEUE:")
        print(f"   Pending: {len(pending)} videos")
        print(f"   Posted: {len(posted)} videos")

        if pending:
            print(f"\n   Ready to post:")
            for p in pending[:5]:
                print(f"   • {Path(p['video']).name}")

        # Learning stats
        report = self.adaptive.get_performance_report(30)

        print(f"\n📈 PERFORMANCE (30 days):")
        print(f"   Total Posts: {report['totals']['posts']}")
        print(f"   Total Views: {report['totals']['views']:,}")
        print(f"   Total Clicks: {report['totals']['clicks']:,}")
        print(f"   Total Revenue: ${report['totals']['revenue']:.2f}")

        # Recommendations
        recs = report['recommendations']
        print(f"\n💡 AI RECOMMENDATIONS:")
        print(f"   Best hook: {recs.get('hook_style', 'N/A')}")
        print(f"   Best topic: {recs.get('topic', 'N/A')}")
        print(f"   Best product: {recs.get('product', 'N/A')}")
        print(f"   Best time: {recs.get('post_time', 'N/A')}:00")

        # Link tracking
        link_stats = self.link_tracker.get_dashboard_stats(30)
        print(f"\n🔗 AFFILIATE LINKS:")
        print(f"   Clicks: {link_stats['total_clicks']}")
        print(f"   Conversions: {link_stats['total_conversions']}")
        print(f"   Revenue: ${link_stats['total_revenue']:.2f}")

    def show_learning(self):
        """Show what the system has learned"""

        print("\n" + "=" * 60)
        print("🧠 ADAPTIVE LEARNING INSIGHTS")
        print("=" * 60)

        patterns = self.adaptive.analyze_patterns()

        # Best hooks
        print("\n🎣 BEST PERFORMING HOOKS:")
        if patterns['hooks']:
            for i, h in enumerate(patterns['hooks'][:5], 1):
                bar = "█" * int(h['avg_score'] / 100)
                print(f"   {i}. {h['style']:<15} {bar} ({h['avg_score']:.0f})")
        else:
            print("   No data yet - run more cycles!")

        # Best products
        print("\n💰 BEST CONVERTING PRODUCTS:")
        if patterns['products']:
            for i, p in enumerate(patterns['products'][:5], 1):
                print(f"   {i}. {p['product']:<15} ${p['revenue']:.2f} revenue, {p['clicks']} clicks")
        else:
            print("   No data yet - run more cycles!")

        # Best times
        print("\n⏰ BEST POSTING TIMES:")
        if patterns['best_times']:
            for t in patterns['best_times'][:5]:
                print(f"   {t['hour']:02d}:00 - score {t['avg_score']:.0f}")
        else:
            print("   No data yet - run more cycles!")

        # Recommendations
        recs = self.adaptive.get_recommendations()
        print("\n🎯 NEXT CONTENT RECOMMENDATION:")
        print(f"   Hook Style: {recs.get('hook_style', 'Try tutorial')}")
        print(f"   Product: {recs.get('product', 'Jasper')}")
        print(f"   Post at: {recs.get('post_time', 12)}:00")

        print("\n   Reasoning:")
        for r in recs.get('reasoning', ['Not enough data yet']):
            print(f"   • {r}")

    def update_metrics(self, content_id: str, views: int = None, likes: int = None,
                       clicks: int = None, conversions: int = None, revenue: float = None):
        """Update metrics for a piece of content"""

        self.adaptive.update_metrics(
            content_id=content_id,
            views=views,
            likes=likes,
            clicks=clicks,
            conversions=conversions,
            revenue=revenue
        )

        print(f"✓ Updated metrics for {content_id}")

        # Auto-update strategy
        self.adaptive.update_strategy()

    def interactive_mode(self):
        """Run in interactive mode"""

        print("""
╔══════════════════════════════════════════════════════════════════╗
║              FULL AUTOMATION SYSTEM                              ║
║              Target: $10,000 / week                              ║
╠══════════════════════════════════════════════════════════════════╣
║  [1] Run Automation Cycle (generate + create + queue)            ║
║  [2] Generate Content Only (scripts)                             ║
║  [3] Create Videos from Queue                                    ║
║  [4] Show System Status                                          ║
║  [5] Show Learning Insights                                      ║
║  [6] Update Metrics (after posting)                              ║
║  [7] Show TikTok Posting Guide                                   ║
║                                                                  ║
║  [Q] Quit                                                        ║
╚══════════════════════════════════════════════════════════════════╝
        """)

        while True:
            choice = input("\nSelect option: ").strip().lower()

            if choice == '1':
                try:
                    count = int(input("How many videos to generate? [3]: ").strip() or "3")
                except ValueError:
                    count = 3
                self.run_cycle(num_videos=count)

            elif choice == '2':
                try:
                    count = int(input("How many scripts? [5]: ").strip() or "5")
                except ValueError:
                    count = 5

                print(f"\n📝 Generating {count} scripts...")
                for i in range(count):
                    script = self.content_gen.generate_tiktok_script()
                    print(f"\n--- Script {i+1} ({script['style']}) ---")
                    print(f"Product: {script['product']}")
                    print(f"Hook: {script['hook']}")
                    print(f"Caption: {script['caption']}")

            elif choice == '3':
                queue = self.poster.tiktok.get_queue()
                pending = [q for q in queue if q.get('status') == 'queued']
                print(f"\n📱 {len(pending)} videos in TikTok queue")
                for p in pending:
                    print(f"  • {Path(p['video']).name}")

            elif choice == '4':
                self.show_status()

            elif choice == '5':
                self.show_learning()

            elif choice == '6':
                content_id = input("Content ID: ").strip()
                if content_id:
                    try:
                        views = int(input("Views: ").strip() or "0")
                        likes = int(input("Likes: ").strip() or "0")
                        clicks = int(input("Bio clicks: ").strip() or "0")
                        conversions = int(input("Conversions: ").strip() or "0")
                        revenue = float(input("Revenue $: ").strip() or "0")

                        self.update_metrics(content_id, views, likes, clicks, conversions, revenue)
                    except ValueError:
                        print("Invalid input")

            elif choice == '7':
                self.poster.tiktok.show_posting_instructions()

            elif choice in ('q', 'quit', 'exit'):
                print("\n🤖 Automation system offline. Good luck!")
                break

            else:
                print("Invalid option")


def main():
    """Entry point"""

    automation = FullAutomation(niche="ai writing tools")

    if len(sys.argv) < 2:
        automation.interactive_mode()
        return

    cmd = sys.argv[1].lower()

    if cmd == 'run':
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        automation.run_cycle(num_videos=count)

    elif cmd == 'generate':
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        for i in range(count):
            script = automation.content_gen.generate_tiktok_script()
            print(f"\n--- Script {i+1} ---")
            print(script['script'])
            print(f"\nCaption: {script['caption']}")
            print(f"Hashtags: {' '.join(script['hashtags'])}")

    elif cmd == 'status':
        automation.show_status()

    elif cmd == 'learn':
        automation.show_learning()

    elif cmd == 'help':
        print(__doc__)

    else:
        print(f"Unknown command: {cmd}")
        print("Use: python automate.py help")


if __name__ == "__main__":
    main()
