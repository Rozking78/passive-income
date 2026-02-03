#!/usr/bin/env python3
"""
Passive Income Automation System
================================
Automated affiliate marketing system targeting $10k/week

Components:
- Niche Finder: Research profitable niches
- Content Engine: Generate content templates
- Link Tracker: Track clicks & conversions
- Analytics: Monitor progress to goal

Usage:
  python main.py              # Interactive menu
  python main.py research     # Run niche research
  python main.py content      # Generate content ideas
  python main.py stats        # Show dashboard stats
  python main.py links        # Manage affiliate links
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.dirname(__file__))

from src.niche_finder.finder import NicheFinder
from src.content_engine.generator import ContentGenerator
from src.link_tracker.tracker import LinkTracker


class PassiveIncomeSystem:
    """Main system controller"""

    def __init__(self):
        self.niche_finder = NicheFinder()
        self.content_generator = ContentGenerator()
        self.link_tracker = LinkTracker()

        self.weekly_target = 10000
        self.monthly_target = 40000

    def show_banner(self):
        """Display system banner"""
        print("""
╔══════════════════════════════════════════════════════════════════╗
║                  PASSIVE INCOME AUTOMATION SYSTEM                 ║
║                     Target: $10,000 / week                        ║
╠══════════════════════════════════════════════════════════════════╣
║  [1] Research Niches     [4] View Links                          ║
║  [2] Generate Content    [5] Record Click                        ║
║  [3] Dashboard Stats     [6] Record Sale                         ║
║                          [7] Add New Link                        ║
║  [Q] Quit                [H] Help                                ║
╚══════════════════════════════════════════════════════════════════╝
        """)

    def show_dashboard(self):
        """Show main dashboard with stats"""
        stats = self.link_tracker.get_dashboard_stats()
        projection = self.link_tracker.project_monthly_revenue()

        print("\n" + "=" * 60)
        print("📊 DASHBOARD - Last 30 Days")
        print("=" * 60)

        # Progress bar
        progress = min(projection['weekly_progress_pct'], 100)
        bar_length = 40
        filled = int(bar_length * progress / 100)
        bar = "█" * filled + "░" * (bar_length - filled)

        print(f"\n🎯 WEEKLY GOAL: ${self.weekly_target:,}")
        print(f"   [{bar}] {progress:.1f}%")
        print(f"   Current pace: ${projection['daily_average_7d'] * 7:,.2f}/week")

        print(f"\n📈 METRICS:")
        print(f"   Total Clicks:      {stats['total_clicks']:,}")
        print(f"   Total Conversions: {stats['total_conversions']:,}")
        print(f"   Conversion Rate:   {stats['conversion_rate']}%")
        print(f"   Total Revenue:     ${stats['total_revenue']:,.2f}")
        print(f"   Recurring Revenue: ${stats['recurring_revenue']:,.2f}")

        if stats['top_links']:
            print(f"\n🏆 TOP PERFORMERS:")
            for i, link in enumerate(stats['top_links'][:5], 1):
                print(f"   {i}. {link['product']}: {link['clicks']} clicks, "
                      f"{link['conversions']} sales, ${link['revenue']:.2f}")

        if stats['clicks_by_platform']:
            print(f"\n📱 CLICKS BY PLATFORM:")
            for platform, count in stats['clicks_by_platform'].items():
                print(f"   {platform}: {count}")

        print("\n" + "=" * 60)

    def research_niches(self):
        """Interactive niche research"""
        print("\n" + "=" * 60)
        print("🔍 NICHE RESEARCH")
        print("=" * 60)

        niche = input("\nEnter niche to research (or 'list' for suggestions): ").strip()

        if niche.lower() == 'list':
            from config.settings import NICHE_CATEGORIES
            print("\n📋 Suggested niches:")
            for i, n in enumerate(NICHE_CATEGORIES, 1):
                print(f"   {i}. {n}")
            niche = input("\nEnter niche to research: ").strip()

        if not niche:
            return

        print(f"\n🔄 Analyzing '{niche}'...")

        # Analyze niche
        analysis = self.niche_finder.analyze_niche_potential(niche)
        print(f"\n📊 Potential Score: {analysis['score']}/100")
        print(f"📌 {analysis['recommendation']}")

        # Content ideas
        print(f"\n💡 CONTENT IDEAS:")
        for idea in self.niche_finder.find_content_gaps(niche):
            print(f"   • {idea}")

        # Matching programs
        programs = self.niche_finder.get_affiliate_match(niche)
        if programs:
            print(f"\n💰 MATCHING AFFILIATE PROGRAMS:")
            for prog in programs:
                print(f"   • {prog['name']}: {prog['commission']} ({prog['cookie']})")

    def generate_content(self):
        """Interactive content generation"""
        print("\n" + "=" * 60)
        print("✍️  CONTENT GENERATOR")
        print("=" * 60)

        product = input("\nEnter product name: ").strip()
        if not product:
            return

        print(f"\nContent type:")
        print("  1. Video hooks/titles")
        print("  2. TikTok scripts")
        print("  3. Blog outline")
        print("  4. Email sequence")
        print("  5. Social media posts")
        print("  6. All of the above")

        choice = input("\nSelect (1-6): ").strip()

        if choice in ('1', '6'):
            print(f"\n📹 VIDEO HOOKS for '{product}':")
            for hook in self.content_generator.generate_hooks(product, product)[:10]:
                print(f"   • {hook}")

        if choice in ('2', '6'):
            print(f"\n📱 TIKTOK SCRIPTS for '{product}':")
            for script in self.content_generator.generate_tiktok_scripts(product):
                print(f"\n   [{script['format']} - {script['duration']}]")
                print(f"   {script['script']}")

        if choice in ('3', '6'):
            outline = self.content_generator.generate_blog_outline(product, "review")
            print(f"\n📝 BLOG OUTLINE for '{product}':")
            print(f"   Title: {outline['title']}")
            print(f"   Meta: {outline['meta_description']}")
            print("\n   Structure:")
            for section in outline['outline']:
                print(f"   {section}")

        if choice in ('4', '6'):
            print(f"\n📧 EMAIL SEQUENCE for '{product}':")
            for email in self.content_generator.generate_email_sequence(product):
                print(f"\n   Day {email['day']}: {email['subject']}")
                print(f"   Purpose: {email['purpose']}")

        if choice in ('5', '6'):
            print(f"\n🐦 SOCIAL POSTS for '{product}':")
            for post in self.content_generator.generate_social_posts(product, "twitter"):
                print(f"\n   {post}")

    def manage_links(self):
        """View and manage affiliate links"""
        print("\n" + "=" * 60)
        print("🔗 AFFILIATE LINKS")
        print("=" * 60)

        links = self.link_tracker.get_links()

        if not links:
            print("\n   No links tracked yet. Add your first link!")
        else:
            print(f"\n{'#':<3} {'Product':<20} {'Code':<10} {'Clicks':<8} {'Sales':<8} {'Revenue':<10}")
            print("-" * 65)
            for i, link in enumerate(links, 1):
                print(f"{i:<3} {link['product_name'][:20]:<20} {link['short_code']:<10} "
                      f"{link['total_clicks']:<8} {link['total_conversions']:<8} ${link['total_revenue']:<10.2f}")

    def add_link(self):
        """Add a new affiliate link"""
        print("\n" + "=" * 60)
        print("➕ ADD NEW LINK")
        print("=" * 60)

        url = input("\nAffiliate URL: ").strip()
        if not url:
            return

        product = input("Product name: ").strip()
        program = input("Affiliate program name: ").strip()
        commission = input("Commission (e.g., '30% recurring'): ").strip()

        result = self.link_tracker.add_link(url, product, program, commission)

        print(f"\n✅ Link added!")
        print(f"   Product: {result['product_name']}")
        print(f"   Tracking code: {result['short_code']}")
        print(f"   Use this code to track clicks from different sources")

    def record_click(self):
        """Manually record a click"""
        code = input("\nEnter link code: ").strip()
        if not code:
            return

        platform = input("Platform (youtube/tiktok/blog/email/twitter): ").strip()
        campaign = input("Campaign name (optional): ").strip()

        if self.link_tracker.record_click(code, platform=platform, campaign=campaign):
            print("✅ Click recorded!")
        else:
            print("❌ Link not found")

    def record_sale(self):
        """Record a sale/conversion"""
        code = input("\nEnter link code: ").strip()
        if not code:
            return

        try:
            amount = float(input("Commission amount ($): ").strip())
        except ValueError:
            print("Invalid amount")
            return

        recurring = input("Is this recurring? (y/n): ").strip().lower() == 'y'
        notes = input("Notes (optional): ").strip()

        if self.link_tracker.record_conversion(code, amount, recurring, notes):
            print(f"✅ Sale recorded! ${amount:.2f}" + (" (recurring)" if recurring else ""))
        else:
            print("❌ Link not found")

    def show_help(self):
        """Show help information"""
        print("""
📚 HELP - How to use this system
================================

1. RESEARCH NICHES
   Find profitable niches with high affiliate commissions.
   The system analyzes Reddit activity and suggests content angles.

2. GENERATE CONTENT
   Get ready-to-use content templates:
   - Video hooks and titles
   - TikTok/Reels scripts
   - Blog post outlines
   - Email sequences
   - Social media posts

3. TRACK LINKS
   Add your affiliate links with tracking codes.
   Record clicks from different platforms.
   Log sales to track your progress.

4. MONITOR PROGRESS
   See your dashboard with:
   - Weekly revenue progress
   - Top performing links
   - Platform breakdown
   - Conversion rates

WORKFLOW:
1. Research → Pick a niche
2. Sign up → Join affiliate programs
3. Create → Make content with templates
4. Track → Add links and monitor
5. Optimize → Focus on what works
6. Scale → Increase content output

TARGET: $10,000/week = $1,429/day = $42,857/month
        """)

    def run(self):
        """Main loop"""
        while True:
            self.show_banner()
            choice = input("Select option: ").strip().lower()

            if choice == '1':
                self.research_niches()
            elif choice == '2':
                self.generate_content()
            elif choice == '3':
                self.show_dashboard()
            elif choice == '4':
                self.manage_links()
            elif choice == '5':
                self.record_click()
            elif choice == '6':
                self.record_sale()
            elif choice == '7':
                self.add_link()
            elif choice in ('h', 'help'):
                self.show_help()
            elif choice in ('q', 'quit', 'exit'):
                print("\n👋 Good luck on your passive income journey!")
                break
            else:
                print("\n❌ Invalid option")

            input("\nPress Enter to continue...")


def main():
    """Entry point"""
    system = PassiveIncomeSystem()

    # Handle command line arguments
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == 'research':
            system.research_niches()
        elif cmd == 'content':
            system.generate_content()
        elif cmd == 'stats':
            system.show_dashboard()
        elif cmd == 'links':
            system.manage_links()
        elif cmd == 'help':
            system.show_help()
        else:
            print(f"Unknown command: {cmd}")
            print("Usage: python main.py [research|content|stats|links|help]")
    else:
        system.run()


if __name__ == "__main__":
    main()
