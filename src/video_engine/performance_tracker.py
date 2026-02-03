"""
Performance Tracker
===================
Monitors TikTok performance and feeds data back into the adaptive engine.

Tracks:
- Views, likes, comments, shares per video
- Profile visits and link clicks
- Which hooks/products/times perform best
- Auto-adjusts content strategy based on results

Usage:
    tracker = PerformanceTracker()
    tracker.scrape_tiktok_stats()  # Get latest stats
    tracker.analyze_and_adapt()     # Update strategy
"""

import os
import json
import time
import pickle
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False


@dataclass
class VideoPerformance:
    """Performance data for a single video"""
    video_id: str
    url: str
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    play_time: float = 0.0  # Average watch time
    posted_at: str = ""
    scraped_at: str = ""

    # Metadata from our system
    content_id: str = ""
    hook_style: str = ""
    product: str = ""

    @property
    def engagement_rate(self) -> float:
        """Calculate engagement rate"""
        if self.views == 0:
            return 0
        return ((self.likes + self.comments + self.shares) / self.views) * 100

    @property
    def viral_score(self) -> float:
        """Calculate viral potential score (0-100)"""
        if self.views == 0:
            return 0

        # Weighted scoring
        score = 0
        score += min(self.views / 1000, 30)  # Up to 30 points for views
        score += min(self.engagement_rate * 5, 30)  # Up to 30 points for engagement
        score += min(self.shares * 2, 20)  # Up to 20 points for shares
        score += min(self.saves, 20)  # Up to 20 points for saves

        return min(score, 100)


class PerformanceTracker:
    """Tracks and analyzes content performance"""

    def __init__(self, db_path: str = "data/performance.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.cookies_path = Path("data/tiktok_cookies.pkl")
        self.driver = None

        self._init_db()

    def _init_db(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Video performance table
        c.execute("""
            CREATE TABLE IF NOT EXISTS video_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT UNIQUE,
                url TEXT,
                views INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                saves INTEGER DEFAULT 0,
                play_time REAL DEFAULT 0,
                engagement_rate REAL DEFAULT 0,
                viral_score REAL DEFAULT 0,
                content_id TEXT,
                hook_style TEXT,
                product TEXT,
                posted_at TEXT,
                scraped_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Performance history (track changes over time)
        c.execute("""
            CREATE TABLE IF NOT EXISTS performance_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT,
                views INTEGER,
                likes INTEGER,
                comments INTEGER,
                shares INTEGER,
                scraped_at TEXT,
                FOREIGN KEY (video_id) REFERENCES video_performance(video_id)
            )
        """)

        # Strategy adjustments log
        c.execute("""
            CREATE TABLE IF NOT EXISTS strategy_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                adjustment_type TEXT,
                old_value TEXT,
                new_value TEXT,
                reason TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Link click tracking
        c.execute("""
            CREATE TABLE IF NOT EXISTS link_clicks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                campaign TEXT,
                clicks INTEGER DEFAULT 0,
                date TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def _init_driver(self, headless: bool = True):
        """Initialize Chrome driver"""
        if not SELENIUM_AVAILABLE:
            raise RuntimeError("Selenium not installed")

        options = Options()

        if headless:
            options.add_argument("--headless=new")

        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")

        # Use saved profile
        user_data_dir = Path("data/chrome_profile")
        if user_data_dir.exists():
            options.add_argument(f"--user-data-dir={user_data_dir.absolute()}")

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

    def scrape_tiktok_stats(self, username: str = None) -> List[VideoPerformance]:
        """
        Scrape performance stats from TikTok.

        Args:
            username: TikTok username (without @)

        Returns:
            List of VideoPerformance objects
        """
        if not SELENIUM_AVAILABLE:
            print("❌ Selenium required for scraping")
            return []

        print("\n📊 Scraping TikTok Performance...")

        try:
            self._init_driver(headless=True)

            # Load cookies
            if self.cookies_path.exists():
                self.driver.get("https://www.tiktok.com")
                time.sleep(2)

                with open(self.cookies_path, "rb") as f:
                    cookies = pickle.load(f)
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except:
                        pass

            # Go to analytics or profile
            # TikTok analytics requires business account
            # We'll scrape from the public profile

            if username:
                profile_url = f"https://www.tiktok.com/@{username}"
            else:
                # Try to get own profile
                self.driver.get("https://www.tiktok.com")
                time.sleep(3)

                # Click on profile
                try:
                    profile_link = self.driver.find_element(By.CSS_SELECTOR, "a[href*='/@']")
                    profile_url = profile_link.get_attribute("href")
                except:
                    print("   Could not find profile link")
                    return []

            self.driver.get(profile_url)
            time.sleep(3)

            # Scroll to load videos
            for _ in range(3):
                self.driver.execute_script("window.scrollBy(0, 1000)")
                time.sleep(1)

            # Find video elements
            videos = []
            video_elements = self.driver.find_elements(By.CSS_SELECTOR, "div[data-e2e='user-post-item']")

            print(f"   Found {len(video_elements)} videos")

            for elem in video_elements[:20]:  # Limit to recent 20
                try:
                    # Get video link
                    link = elem.find_element(By.TAG_NAME, "a")
                    video_url = link.get_attribute("href")
                    video_id = video_url.split("/")[-1] if video_url else ""

                    # Get view count
                    views_text = elem.find_element(By.CSS_SELECTOR, "strong").text
                    views = self._parse_count(views_text)

                    perf = VideoPerformance(
                        video_id=video_id,
                        url=video_url,
                        views=views,
                        scraped_at=datetime.now().isoformat()
                    )

                    videos.append(perf)

                except Exception as e:
                    continue

            # Get detailed stats for each video
            for perf in videos[:10]:  # Detailed stats for top 10
                try:
                    self.driver.get(perf.url)
                    time.sleep(2)

                    # Try to get likes, comments, shares
                    stats = self.driver.find_elements(By.CSS_SELECTOR, "strong[data-e2e]")
                    for stat in stats:
                        data_type = stat.get_attribute("data-e2e")
                        value = self._parse_count(stat.text)

                        if "like" in data_type:
                            perf.likes = value
                        elif "comment" in data_type:
                            perf.comments = value
                        elif "share" in data_type:
                            perf.shares = value

                except Exception as e:
                    continue

            # Save to database
            self._save_performance(videos)

            print(f"   ✓ Scraped {len(videos)} videos")

            return videos

        except Exception as e:
            print(f"   ❌ Scraping error: {e}")
            return []

        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None

    def _parse_count(self, text: str) -> int:
        """Parse count text like '1.2K' or '5M' to integer"""
        if not text:
            return 0

        text = text.strip().upper()

        try:
            if 'K' in text:
                return int(float(text.replace('K', '')) * 1000)
            elif 'M' in text:
                return int(float(text.replace('M', '')) * 1000000)
            elif 'B' in text:
                return int(float(text.replace('B', '')) * 1000000000)
            else:
                return int(text.replace(',', ''))
        except:
            return 0

    def _save_performance(self, videos: List[VideoPerformance]):
        """Save performance data to database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        for v in videos:
            # Upsert performance
            c.execute("""
                INSERT INTO video_performance
                (video_id, url, views, likes, comments, shares, engagement_rate, viral_score, scraped_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(video_id) DO UPDATE SET
                    views = excluded.views,
                    likes = excluded.likes,
                    comments = excluded.comments,
                    shares = excluded.shares,
                    engagement_rate = excluded.engagement_rate,
                    viral_score = excluded.viral_score,
                    scraped_at = excluded.scraped_at
            """, (v.video_id, v.url, v.views, v.likes, v.comments, v.shares,
                  v.engagement_rate, v.viral_score, v.scraped_at))

            # Add to history
            c.execute("""
                INSERT INTO performance_history (video_id, views, likes, comments, shares, scraped_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (v.video_id, v.views, v.likes, v.comments, v.shares, v.scraped_at))

        conn.commit()
        conn.close()

    def link_to_content(self, video_id: str, content_id: str, hook_style: str = "", product: str = ""):
        """Link a TikTok video to our content metadata"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute("""
            UPDATE video_performance
            SET content_id = ?, hook_style = ?, product = ?
            WHERE video_id = ?
        """, (content_id, hook_style, product, video_id))

        conn.commit()
        conn.close()

    def get_performance_summary(self, days: int = 7) -> Dict:
        """Get performance summary for recent period"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        # Overall stats
        c.execute("""
            SELECT
                COUNT(*) as total_videos,
                SUM(views) as total_views,
                SUM(likes) as total_likes,
                SUM(comments) as total_comments,
                SUM(shares) as total_shares,
                AVG(engagement_rate) as avg_engagement,
                AVG(viral_score) as avg_viral_score
            FROM video_performance
            WHERE scraped_at > ?
        """, (cutoff,))

        row = c.fetchone()

        summary = {
            "period_days": days,
            "total_videos": row[0] or 0,
            "total_views": row[1] or 0,
            "total_likes": row[2] or 0,
            "total_comments": row[3] or 0,
            "total_shares": row[4] or 0,
            "avg_engagement_rate": round(row[5] or 0, 2),
            "avg_viral_score": round(row[6] or 0, 2),
        }

        # Best performing videos
        c.execute("""
            SELECT video_id, views, likes, engagement_rate, viral_score, hook_style, product
            FROM video_performance
            WHERE scraped_at > ?
            ORDER BY viral_score DESC
            LIMIT 5
        """, (cutoff,))

        summary["top_videos"] = [
            {
                "video_id": r[0],
                "views": r[1],
                "likes": r[2],
                "engagement_rate": round(r[3], 2),
                "viral_score": round(r[4], 2),
                "hook_style": r[5],
                "product": r[6]
            }
            for r in c.fetchall()
        ]

        # Performance by hook style
        c.execute("""
            SELECT hook_style, COUNT(*) as count, AVG(viral_score) as avg_score
            FROM video_performance
            WHERE hook_style != '' AND scraped_at > ?
            GROUP BY hook_style
            ORDER BY avg_score DESC
        """, (cutoff,))

        summary["by_hook_style"] = [
            {"style": r[0], "count": r[1], "avg_score": round(r[2], 2)}
            for r in c.fetchall()
        ]

        # Performance by product
        c.execute("""
            SELECT product, COUNT(*) as count, AVG(viral_score) as avg_score
            FROM video_performance
            WHERE product != '' AND scraped_at > ?
            GROUP BY product
            ORDER BY avg_score DESC
        """, (cutoff,))

        summary["by_product"] = [
            {"product": r[0], "count": r[1], "avg_score": round(r[2], 2)}
            for r in c.fetchall()
        ]

        conn.close()

        return summary

    def analyze_and_adapt(self) -> Dict:
        """
        Analyze performance and update content strategy.

        Returns recommended adjustments.
        """
        print("\n🧠 Analyzing Performance & Adapting Strategy...")

        summary = self.get_performance_summary(days=14)

        adjustments = {
            "recommended_hook_styles": [],
            "recommended_products": [],
            "avoid_hook_styles": [],
            "avoid_products": [],
            "insights": []
        }

        # Analyze hook styles
        if summary["by_hook_style"]:
            best_hooks = [h for h in summary["by_hook_style"] if h["avg_score"] > 50]
            worst_hooks = [h for h in summary["by_hook_style"] if h["avg_score"] < 20]

            adjustments["recommended_hook_styles"] = [h["style"] for h in best_hooks[:3]]
            adjustments["avoid_hook_styles"] = [h["style"] for h in worst_hooks]

            if best_hooks:
                adjustments["insights"].append(
                    f"Best hook style: {best_hooks[0]['style']} (score: {best_hooks[0]['avg_score']})"
                )

        # Analyze products
        if summary["by_product"]:
            best_products = [p for p in summary["by_product"] if p["avg_score"] > 50]
            worst_products = [p for p in summary["by_product"] if p["avg_score"] < 20]

            adjustments["recommended_products"] = [p["product"] for p in best_products[:3]]
            adjustments["avoid_products"] = [p["product"] for p in worst_products]

            if best_products:
                adjustments["insights"].append(
                    f"Best product: {best_products[0]['product']} (score: {best_products[0]['avg_score']})"
                )

        # Engagement analysis
        if summary["avg_engagement_rate"] < 3:
            adjustments["insights"].append(
                "Low engagement - try more provocative hooks or questions"
            )
        elif summary["avg_engagement_rate"] > 8:
            adjustments["insights"].append(
                "High engagement - double down on current strategy"
            )

        # Save adjustments to adaptive engine
        self._update_adaptive_engine(adjustments)

        # Log strategy change
        self._log_strategy_change(adjustments)

        print(f"   ✓ Analysis complete")
        for insight in adjustments["insights"]:
            print(f"   → {insight}")

        return adjustments

    def _update_adaptive_engine(self, adjustments: Dict):
        """Update the adaptive engine with new learnings"""
        try:
            from src.video_engine.adaptive_engine import AdaptiveEngine

            engine = AdaptiveEngine()

            # Update preferred hooks
            if adjustments["recommended_hook_styles"]:
                # The adaptive engine will use these for next content generation
                pass  # Engine reads from performance DB

        except ImportError:
            pass

    def _log_strategy_change(self, adjustments: Dict):
        """Log strategy adjustments"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute("""
            INSERT INTO strategy_log (adjustment_type, old_value, new_value, reason)
            VALUES (?, ?, ?, ?)
        """, (
            "content_strategy",
            json.dumps({}),
            json.dumps(adjustments),
            "; ".join(adjustments["insights"])
        ))

        conn.commit()
        conn.close()

    def record_link_click(self, source: str, campaign: str = ""):
        """Manually record a link click"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        today = datetime.now().strftime("%Y-%m-%d")

        c.execute("""
            INSERT INTO link_clicks (source, campaign, clicks, date)
            VALUES (?, ?, 1, ?)
            ON CONFLICT DO UPDATE SET clicks = clicks + 1
        """, (source, campaign, today))

        conn.commit()
        conn.close()

    def get_click_stats(self, days: int = 7) -> Dict:
        """Get link click statistics"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        c.execute("""
            SELECT source, SUM(clicks) as total
            FROM link_clicks
            WHERE date > ?
            GROUP BY source
            ORDER BY total DESC
        """, (cutoff,))

        by_source = {r[0]: r[1] for r in c.fetchall()}

        c.execute("""
            SELECT SUM(clicks) FROM link_clicks WHERE date > ?
        """, (cutoff,))

        total = c.fetchone()[0] or 0

        conn.close()

        return {
            "total_clicks": total,
            "by_source": by_source,
            "period_days": days
        }

    def show_dashboard(self):
        """Display performance dashboard"""
        print("\n" + "=" * 60)
        print("📊 PERFORMANCE DASHBOARD")
        print("=" * 60)

        summary = self.get_performance_summary(days=7)

        print(f"\n📈 Last 7 Days:")
        print(f"   Videos tracked: {summary['total_videos']}")
        print(f"   Total views: {summary['total_views']:,}")
        print(f"   Total likes: {summary['total_likes']:,}")
        print(f"   Avg engagement: {summary['avg_engagement_rate']}%")
        print(f"   Avg viral score: {summary['avg_viral_score']}/100")

        if summary["top_videos"]:
            print(f"\n🏆 Top Performers:")
            for i, v in enumerate(summary["top_videos"][:3], 1):
                print(f"   {i}. {v['views']:,} views, {v['engagement_rate']}% eng, score: {v['viral_score']}")

        if summary["by_hook_style"]:
            print(f"\n🎣 By Hook Style:")
            for h in summary["by_hook_style"][:3]:
                print(f"   {h['style']}: {h['count']} videos, score: {h['avg_score']}")

        if summary["by_product"]:
            print(f"\n💰 By Product:")
            for p in summary["by_product"][:3]:
                print(f"   {p['product']}: {p['count']} videos, score: {p['avg_score']}")

        # Click stats
        clicks = self.get_click_stats(7)
        print(f"\n🔗 Link Clicks (7 days): {clicks['total_clicks']}")
        if clicks["by_source"]:
            for source, count in list(clicks["by_source"].items())[:3]:
                print(f"   {source}: {count}")


def main():
    """Test the performance tracker"""
    tracker = PerformanceTracker()

    # Show current dashboard
    tracker.show_dashboard()

    # Optionally scrape new data
    print("\n" + "=" * 60)
    response = input("Scrape latest TikTok stats? (y/n): ").strip().lower()
    if response == 'y':
        username = input("TikTok username (without @): ").strip()
        tracker.scrape_tiktok_stats(username or None)

        # Analyze and adapt
        tracker.analyze_and_adapt()

        # Show updated dashboard
        tracker.show_dashboard()


if __name__ == "__main__":
    main()
