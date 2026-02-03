#!/usr/bin/env python3
"""
Quick Content Generator
=======================
Generate ready-to-post content in one command.

Usage:
  python generate.py                    # Interactive mode
  python generate.py tiktok             # Generate 1 TikTok script
  python generate.py tiktok 5           # Generate 5 TikTok scripts
  python generate.py week               # Generate a full week of content
  python generate.py blog               # Generate a blog post
  python generate.py thread             # Generate a Twitter thread
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from src.content_engine.auto_generator import AutoContentGenerator


def print_tiktok(script: dict, num: int = None):
    """Pretty print a TikTok script"""
    header = f"📱 TIKTOK SCRIPT" + (f" #{num}" if num else "")
    print(f"\n{'='*60}")
    print(header)
    print(f"{'='*60}")
    print(f"Style: {script['style']} | Product: {script['product']} | Duration: {script['duration']}")
    print(f"{'-'*60}")
    print(script['script'])
    print(f"{'-'*60}")
    print(f"📝 CAPTION:\n{script['caption']}")
    print(f"\n🏷️ HASHTAGS:\n{' '.join(script['hashtags'])}")
    print(f"{'='*60}\n")


def print_thread(thread: dict):
    """Pretty print a Twitter thread"""
    print(f"\n{'='*60}")
    print(f"🐦 TWITTER THREAD: {thread['topic']}")
    print(f"{'='*60}")
    for i, tweet in enumerate(thread['tweets'], 1):
        print(f"\n[Tweet {i}/{thread['total_tweets']}]")
        print(tweet)
        print("-" * 40)
    print(f"{'='*60}\n")


def print_blog(post: dict):
    """Pretty print a blog post"""
    print(f"\n{'='*60}")
    print(f"📝 BLOG POST: {post['type'].upper()}")
    print(f"{'='*60}")
    print(f"Title: {post['title']}")
    print(f"Words: {post['word_count']}")
    print(f"Meta: {post['meta_description']}")
    print(f"Keywords: {', '.join(post['keywords'])}")
    print(f"{'-'*60}")
    print(post['content'])
    print(f"{'='*60}\n")


def interactive_mode(generator):
    """Interactive content generation"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║              AUTO CONTENT GENERATOR                              ║
║              Niche: AI Writing Tools                             ║
╠══════════════════════════════════════════════════════════════════╣
║  [1] Generate TikTok Script (single)                             ║
║  [2] Generate 5 TikTok Scripts                                   ║
║  [3] Generate Week of Content (7 TikToks + blog ideas)           ║
║  [4] Generate Twitter Thread                                     ║
║  [5] Generate Blog Post                                          ║
║  [6] Generate Everything (full content pack)                     ║
║                                                                  ║
║  [Q] Quit                                                        ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    while True:
        choice = input("\nSelect option: ").strip().lower()

        if choice == '1':
            script = generator.generate_tiktok_script()
            print_tiktok(script)

        elif choice == '2':
            print("\n🎬 Generating 5 TikTok scripts...")
            styles = ["hook", "tutorial", "storytime", "results", "controversy"]
            for i, style in enumerate(styles, 1):
                script = generator.generate_tiktok_script(style)
                print_tiktok(script, i)

        elif choice == '3':
            print("\n📅 Generating week of content...")
            batch = generator.generate_content_batch(7)
            for i, script in enumerate(batch['tiktoks'], 1):
                print_tiktok(script, i)
            print("\n📋 Blog post ideas:")
            for idea in batch['blog_ideas']:
                print(f"  • [{idea['type']}] {idea['title']}")
            filepath = generator.save_content(batch)
            print(f"\n💾 Saved to: {filepath}")

        elif choice == '4':
            thread = generator.generate_twitter_thread()
            print_thread(thread)

        elif choice == '5':
            print("\nBlog post type:")
            print("  1. Review")
            print("  2. Comparison")
            print("  3. Tutorial")
            print("  4. Listicle")
            ptype = input("Select (1-4): ").strip()
            types = {'1': 'review', '2': 'comparison', '3': 'tutorial', '4': 'listicle'}
            post = generator.generate_blog_post(types.get(ptype, 'review'))
            print_blog(post)

        elif choice == '6':
            print("\n🚀 Generating full content pack...")
            batch = generator.generate_content_batch(7)

            # TikToks
            for i, script in enumerate(batch['tiktoks'], 1):
                print_tiktok(script, i)

            # Twitter thread
            thread = generator.generate_twitter_thread()
            print_thread(thread)

            # Blog posts
            for ptype in ['review', 'tutorial']:
                post = generator.generate_blog_post(ptype)
                print_blog(post)

            filepath = generator.save_content(batch)
            print(f"\n💾 Saved to: {filepath}")

        elif choice in ('q', 'quit', 'exit'):
            print("\n👋 Happy creating!")
            break

        else:
            print("Invalid option")


def main():
    generator = AutoContentGenerator(niche="ai writing tools")

    if len(sys.argv) < 2:
        interactive_mode(generator)
        return

    cmd = sys.argv[1].lower()

    if cmd == 'tiktok':
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        styles = ["hook", "tutorial", "storytime", "comparison", "results", "controversy", "challenge"]
        for i in range(count):
            style = styles[i % len(styles)]
            script = generator.generate_tiktok_script(style)
            print_tiktok(script, i + 1 if count > 1 else None)

    elif cmd == 'week':
        print("📅 Generating week of content...")
        batch = generator.generate_content_batch(7)
        for i, script in enumerate(batch['tiktoks'], 1):
            print_tiktok(script, i)
        print("\n📋 Blog post ideas:")
        for idea in batch['blog_ideas']:
            print(f"  • [{idea['type']}] {idea['title']}")
        filepath = generator.save_content(batch)
        print(f"\n💾 Saved to: {filepath}")

    elif cmd == 'thread':
        thread = generator.generate_twitter_thread()
        print_thread(thread)

    elif cmd == 'blog':
        ptype = sys.argv[2] if len(sys.argv) > 2 else 'review'
        post = generator.generate_blog_post(ptype)
        print_blog(post)

    elif cmd == 'help':
        print(__doc__)

    else:
        print(f"Unknown command: {cmd}")
        print("Use: python generate.py help")


if __name__ == "__main__":
    main()
