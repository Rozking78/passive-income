"""
Auto Poster - Automatically post content to social media
=========================================================

Supports:
- TikTok (via unofficial method / manual assist)
- YouTube Shorts (via API)
- Twitter/X (via API)
- Instagram (via business API)

Note: Some platforms require manual setup or API keys.
"""

import os
import json
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import urllib.request
import urllib.parse


class ContentScheduler:
    """Schedule and manage content posting"""

    def __init__(self, db_path: str = "data/content_schedule.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS scheduled_posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_type TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    content_path TEXT,
                    caption TEXT,
                    hashtags TEXT,
                    scheduled_time TIMESTAMP,
                    posted_time TIMESTAMP,
                    status TEXT DEFAULT 'pending',
                    post_url TEXT,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS post_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id INTEGER,
                    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    views INTEGER DEFAULT 0,
                    likes INTEGER DEFAULT 0,
                    comments INTEGER DEFAULT 0,
                    shares INTEGER DEFAULT 0,
                    clicks INTEGER DEFAULT 0,
                    FOREIGN KEY (post_id) REFERENCES scheduled_posts(id)
                );

                CREATE INDEX IF NOT EXISTS idx_posts_status ON scheduled_posts(status);
                CREATE INDEX IF NOT EXISTS idx_posts_platform ON scheduled_posts(platform);
            """)

    def schedule_post(self, platform: str, content_path: str, caption: str,
                      hashtags: List[str] = None, scheduled_time: datetime = None) -> int:
        """Schedule a post for later"""

        if scheduled_time is None:
            scheduled_time = datetime.now()

        hashtag_str = " ".join(hashtags) if hashtags else ""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO scheduled_posts
                (content_type, platform, content_path, caption, hashtags, scheduled_time, status)
                VALUES (?, ?, ?, ?, ?, ?, 'pending')
            """, (
                "video" if content_path.endswith(('.mp4', '.mov')) else "text",
                platform,
                content_path,
                caption,
                hashtag_str,
                scheduled_time
            ))
            return cursor.lastrowid

    def get_pending_posts(self, platform: str = None) -> List[Dict]:
        """Get posts ready to be published"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            if platform:
                rows = conn.execute("""
                    SELECT * FROM scheduled_posts
                    WHERE status = 'pending'
                    AND platform = ?
                    AND scheduled_time <= ?
                    ORDER BY scheduled_time
                """, (platform, datetime.now())).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM scheduled_posts
                    WHERE status = 'pending'
                    AND scheduled_time <= ?
                    ORDER BY scheduled_time
                """, (datetime.now(),)).fetchall()

            return [dict(row) for row in rows]

    def mark_posted(self, post_id: int, post_url: str = None):
        """Mark a post as published"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE scheduled_posts
                SET status = 'posted', posted_time = ?, post_url = ?
                WHERE id = ?
            """, (datetime.now(), post_url, post_id))

    def mark_failed(self, post_id: int, error: str):
        """Mark a post as failed"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE scheduled_posts
                SET status = 'failed', error_message = ?
                WHERE id = ?
            """, (error, post_id))

    def record_analytics(self, post_id: int, views: int = 0, likes: int = 0,
                         comments: int = 0, shares: int = 0, clicks: int = 0):
        """Record analytics for a post"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO post_analytics
                (post_id, views, likes, comments, shares, clicks)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (post_id, views, likes, comments, shares, clicks))

    def get_analytics_summary(self, days: int = 30) -> Dict:
        """Get analytics summary"""
        cutoff = datetime.now() - timedelta(days=days)

        with sqlite3.connect(self.db_path) as conn:
            # Posts by platform
            posts_by_platform = dict(conn.execute("""
                SELECT platform, COUNT(*) FROM scheduled_posts
                WHERE posted_time >= ? AND status = 'posted'
                GROUP BY platform
            """, (cutoff,)).fetchall())

            # Total engagement
            totals = conn.execute("""
                SELECT
                    SUM(views) as total_views,
                    SUM(likes) as total_likes,
                    SUM(comments) as total_comments,
                    SUM(shares) as total_shares,
                    SUM(clicks) as total_clicks
                FROM post_analytics pa
                JOIN scheduled_posts sp ON pa.post_id = sp.id
                WHERE sp.posted_time >= ?
            """, (cutoff,)).fetchone()

            # Top performing posts
            top_posts = conn.execute("""
                SELECT sp.id, sp.platform, sp.caption,
                       MAX(pa.views) as views,
                       MAX(pa.likes) as likes
                FROM scheduled_posts sp
                JOIN post_analytics pa ON sp.id = pa.post_id
                WHERE sp.posted_time >= ?
                GROUP BY sp.id
                ORDER BY views DESC
                LIMIT 10
            """, (cutoff,)).fetchall()

            return {
                "period_days": days,
                "posts_by_platform": posts_by_platform,
                "total_views": totals[0] or 0,
                "total_likes": totals[1] or 0,
                "total_comments": totals[2] or 0,
                "total_shares": totals[3] or 0,
                "total_clicks": totals[4] or 0,
                "top_posts": [
                    {"id": p[0], "platform": p[1], "caption": p[2][:50], "views": p[3], "likes": p[4]}
                    for p in top_posts
                ]
            }


class YouTubePoster:
    """Post to YouTube Shorts via API"""

    def __init__(self, credentials_path: str = "config/youtube_credentials.json"):
        self.credentials_path = credentials_path
        self.api_available = False

        # Check for google API client
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            self.api_available = True
        except ImportError:
            print("YouTube API not available. Run: pip install google-api-python-client google-auth-oauthlib")

    def upload_short(self, video_path: str, title: str, description: str,
                     tags: List[str] = None) -> Optional[str]:
        """Upload a YouTube Short"""

        if not self.api_available:
            print("YouTube API not installed")
            return None

        if not os.path.exists(self.credentials_path):
            print(f"YouTube credentials not found at {self.credentials_path}")
            print("Set up OAuth credentials at console.cloud.google.com")
            return None

        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload

            # Load credentials
            with open(self.credentials_path) as f:
                creds_data = json.load(f)

            creds = Credentials.from_authorized_user_info(creds_data)

            # Build YouTube service
            youtube = build('youtube', 'v3', credentials=creds)

            # Upload video
            body = {
                'snippet': {
                    'title': title[:100],  # YouTube title limit
                    'description': description,
                    'tags': tags or [],
                    'categoryId': '22'  # People & Blogs
                },
                'status': {
                    'privacyStatus': 'public',
                    'selfDeclaredMadeForKids': False
                }
            }

            media = MediaFileUpload(video_path, mimetype='video/mp4', resumable=True)

            request = youtube.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media
            )

            response = request.execute()
            video_id = response['id']

            return f"https://youtube.com/shorts/{video_id}"

        except Exception as e:
            print(f"YouTube upload error: {e}")
            return None


class TwitterPoster:
    """Post to Twitter/X"""

    def __init__(self, api_key: str = None, api_secret: str = None,
                 access_token: str = None, access_secret: str = None):
        self.api_key = api_key or os.environ.get("TWITTER_API_KEY")
        self.api_secret = api_secret or os.environ.get("TWITTER_API_SECRET")
        self.access_token = access_token or os.environ.get("TWITTER_ACCESS_TOKEN")
        self.access_secret = access_secret or os.environ.get("TWITTER_ACCESS_SECRET")

        self.api_available = all([
            self.api_key, self.api_secret,
            self.access_token, self.access_secret
        ])

        if not self.api_available:
            print("Twitter API credentials not set. Set environment variables:")
            print("  TWITTER_API_KEY, TWITTER_API_SECRET")
            print("  TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET")

    def post_tweet(self, text: str) -> Optional[str]:
        """Post a tweet"""

        if not self.api_available:
            return None

        try:
            import tweepy

            auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
            auth.set_access_token(self.access_token, self.access_secret)
            api = tweepy.API(auth)

            tweet = api.update_status(text)
            return f"https://twitter.com/i/status/{tweet.id}"

        except ImportError:
            print("Tweepy not installed. Run: pip install tweepy")
            return None
        except Exception as e:
            print(f"Twitter error: {e}")
            return None

    def post_thread(self, tweets: List[str]) -> List[str]:
        """Post a Twitter thread"""

        if not self.api_available:
            return []

        try:
            import tweepy

            auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
            auth.set_access_token(self.access_token, self.access_secret)
            api = tweepy.API(auth)

            urls = []
            reply_to = None

            for tweet_text in tweets:
                if reply_to:
                    tweet = api.update_status(
                        tweet_text,
                        in_reply_to_status_id=reply_to,
                        auto_populate_reply_metadata=True
                    )
                else:
                    tweet = api.update_status(tweet_text)

                reply_to = tweet.id
                urls.append(f"https://twitter.com/i/status/{tweet.id}")

            return urls

        except ImportError:
            print("Tweepy not installed. Run: pip install tweepy")
            return []
        except Exception as e:
            print(f"Twitter thread error: {e}")
            return []


class TikTokPoster:
    """
    TikTok posting helper.
    Note: TikTok doesn't have a public posting API.
    This provides manual posting assistance.
    """

    def __init__(self):
        self.queue_dir = Path("content/tiktok_queue")
        self.queue_dir.mkdir(parents=True, exist_ok=True)

    def queue_video(self, video_path: str, caption: str, hashtags: List[str] = None) -> str:
        """Queue a video for TikTok posting"""

        # Copy video to queue
        import shutil
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        queue_video = self.queue_dir / f"tiktok_{timestamp}.mp4"
        shutil.copy(video_path, queue_video)

        # Create metadata file
        metadata = {
            "video": str(queue_video),
            "caption": caption,
            "hashtags": hashtags or [],
            "full_caption": f"{caption}\n\n{' '.join(hashtags or [])}",
            "created": datetime.now().isoformat(),
            "status": "queued"
        }

        meta_path = self.queue_dir / f"tiktok_{timestamp}.json"
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=2)

        return str(meta_path)

    def get_queue(self) -> List[Dict]:
        """Get all queued TikTok videos"""

        queue = []
        for meta_file in self.queue_dir.glob("*.json"):
            with open(meta_file) as f:
                data = json.load(f)
                data["meta_file"] = str(meta_file)
                queue.append(data)

        return sorted(queue, key=lambda x: x.get("created", ""))

    def mark_posted(self, meta_path: str, post_url: str = None):
        """Mark a queued video as posted"""

        with open(meta_path) as f:
            data = json.load(f)

        data["status"] = "posted"
        data["posted_at"] = datetime.now().isoformat()
        data["post_url"] = post_url

        with open(meta_path, "w") as f:
            json.dump(data, f, indent=2)

    def show_posting_instructions(self):
        """Show manual posting instructions"""

        print("""
╔══════════════════════════════════════════════════════════════════╗
║                    TIKTOK POSTING GUIDE                          ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  TikTok doesn't allow automated posting via API.                 ║
║  Here's how to post your queued videos:                          ║
║                                                                  ║
║  OPTION 1: Mobile App                                            ║
║  1. Transfer videos to your phone (AirDrop, Google Drive, etc)   ║
║  2. Open TikTok app                                              ║
║  3. Tap + to create                                              ║
║  4. Select "Upload" and choose video                             ║
║  5. Copy caption from the .json file                             ║
║  6. Post!                                                        ║
║                                                                  ║
║  OPTION 2: TikTok Desktop (tiktok.com)                          ║
║  1. Go to tiktok.com/upload                                      ║
║  2. Drag and drop video file                                     ║
║  3. Copy caption from the .json file                             ║
║  4. Schedule or post immediately                                 ║
║                                                                  ║
║  OPTION 3: Third-party tools                                     ║
║  - Later.com (has TikTok scheduling)                             ║
║  - Hootsuite (business plans)                                    ║
║  - Buffer (limited TikTok support)                               ║
║                                                                  ║
║  Your queued videos are in: content/tiktok_queue/                ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
        """)


class AutoPoster:
    """Main auto-posting controller"""

    def __init__(self):
        self.scheduler = ContentScheduler()
        self.youtube = YouTubePoster()
        self.twitter = TwitterPoster()
        self.tiktok = TikTokPoster()

    def post_to_all(self, video_path: str, caption: str, hashtags: List[str] = None):
        """Post content to all available platforms"""

        results = {}

        # YouTube Shorts
        if self.youtube.api_available:
            print("📹 Posting to YouTube Shorts...")
            url = self.youtube.upload_short(
                video_path,
                title=caption[:100],
                description=f"{caption}\n\n{' '.join(hashtags or [])}",
                tags=hashtags
            )
            results["youtube"] = url
            if url:
                print(f"  ✓ Posted: {url}")
            else:
                print("  ✗ Failed")

        # Twitter (text post with link)
        if self.twitter.api_available:
            print("🐦 Posting to Twitter...")
            tweet_text = f"{caption[:250]}\n\n{' '.join((hashtags or [])[:3])}"
            url = self.twitter.post_tweet(tweet_text)
            results["twitter"] = url
            if url:
                print(f"  ✓ Posted: {url}")
            else:
                print("  ✗ Failed")

        # TikTok (queue for manual posting)
        print("📱 Queueing for TikTok...")
        meta_path = self.tiktok.queue_video(video_path, caption, hashtags)
        results["tiktok"] = {"status": "queued", "meta": meta_path}
        print(f"  ✓ Queued: {meta_path}")

        return results

    def show_status(self):
        """Show posting status"""

        print("\n" + "=" * 60)
        print("AUTO-POSTER STATUS")
        print("=" * 60)

        # Platform availability
        print("\n📡 PLATFORM STATUS:")
        print(f"  YouTube API: {'✓ Connected' if self.youtube.api_available else '✗ Not configured'}")
        print(f"  Twitter API: {'✓ Connected' if self.twitter.api_available else '✗ Not configured'}")
        print(f"  TikTok: Manual posting (queued)")

        # TikTok queue
        queue = self.tiktok.get_queue()
        pending = [q for q in queue if q.get("status") == "queued"]
        print(f"\n📱 TIKTOK QUEUE: {len(pending)} videos pending")

        if pending:
            for item in pending[:5]:
                print(f"  • {Path(item['video']).name}")
                print(f"    Caption: {item['caption'][:50]}...")

        # Scheduled posts
        pending_posts = self.scheduler.get_pending_posts()
        print(f"\n📅 SCHEDULED: {len(pending_posts)} posts pending")

        # Analytics
        analytics = self.scheduler.get_analytics_summary(30)
        print(f"\n📊 LAST 30 DAYS:")
        print(f"  Total Views: {analytics['total_views']:,}")
        print(f"  Total Likes: {analytics['total_likes']:,}")
        print(f"  Total Clicks: {analytics['total_clicks']:,}")


def main():
    """Demo the auto-poster"""

    print("=" * 60)
    print("AUTO-POSTER - Social Media Automation")
    print("=" * 60)

    poster = AutoPoster()
    poster.show_status()

    # Show TikTok instructions
    poster.tiktok.show_posting_instructions()


if __name__ == "__main__":
    main()
