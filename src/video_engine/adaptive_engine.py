"""
Adaptive Learning Engine
========================
Analyzes content performance and automatically improves strategy.

Features:
- Tracks what content performs best
- Identifies winning patterns (hooks, styles, topics)
- Automatically adjusts content generation
- A/B tests different approaches
- Predicts best posting times
"""

import json
import sqlite3
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class AdaptiveEngine:
    """Learn from content performance and improve automatically"""

    def __init__(self, db_path: str = "data/adaptive_learning.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

        # Performance weights
        self.weights = {
            "views": 1.0,
            "likes": 5.0,
            "comments": 10.0,
            "shares": 15.0,
            "clicks": 50.0,  # Most valuable - leads to conversions
        }

    def _init_db(self):
        """Initialize database for learning"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS content_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_id TEXT UNIQUE,
                    platform TEXT,
                    content_type TEXT,
                    hook_style TEXT,
                    topic TEXT,
                    product TEXT,
                    posted_at TIMESTAMP,
                    hour_posted INTEGER,
                    day_of_week INTEGER,
                    views INTEGER DEFAULT 0,
                    likes INTEGER DEFAULT 0,
                    comments INTEGER DEFAULT 0,
                    shares INTEGER DEFAULT 0,
                    clicks INTEGER DEFAULT 0,
                    conversions INTEGER DEFAULT 0,
                    revenue REAL DEFAULT 0,
                    performance_score REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS winning_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_type TEXT,
                    pattern_value TEXT,
                    sample_size INTEGER,
                    avg_score REAL,
                    confidence REAL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS ab_tests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_name TEXT,
                    variant_a TEXT,
                    variant_b TEXT,
                    a_impressions INTEGER DEFAULT 0,
                    b_impressions INTEGER DEFAULT 0,
                    a_score REAL DEFAULT 0,
                    b_score REAL DEFAULT 0,
                    winner TEXT,
                    status TEXT DEFAULT 'running',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS strategy_config (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_perf_platform ON content_performance(platform);
                CREATE INDEX IF NOT EXISTS idx_perf_hook ON content_performance(hook_style);
                CREATE INDEX IF NOT EXISTS idx_perf_topic ON content_performance(topic);
            """)

            # Initialize default strategy
            defaults = {
                "preferred_hooks": json.dumps(["hook", "tutorial", "storytime", "results"]),
                "preferred_topics": json.dumps(["ai tools", "productivity", "passive income"]),
                "preferred_times": json.dumps([7, 12, 19]),  # Hours
                "min_daily_posts": "3",
                "max_daily_posts": "5",
            }

            for key, value in defaults.items():
                conn.execute("""
                    INSERT OR IGNORE INTO strategy_config (key, value)
                    VALUES (?, ?)
                """, (key, value))

    def record_content(self, content_id: str, platform: str, content_type: str,
                       hook_style: str, topic: str, product: str,
                       posted_at: datetime = None) -> int:
        """Record new content for tracking"""

        if posted_at is None:
            posted_at = datetime.now()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT OR REPLACE INTO content_performance
                (content_id, platform, content_type, hook_style, topic, product,
                 posted_at, hour_posted, day_of_week)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                content_id, platform, content_type, hook_style, topic, product,
                posted_at, posted_at.hour, posted_at.weekday()
            ))
            return cursor.lastrowid

    def update_metrics(self, content_id: str, views: int = None, likes: int = None,
                       comments: int = None, shares: int = None, clicks: int = None,
                       conversions: int = None, revenue: float = None):
        """Update performance metrics for content"""

        with sqlite3.connect(self.db_path) as conn:
            # Get current values
            row = conn.execute(
                "SELECT * FROM content_performance WHERE content_id = ?",
                (content_id,)
            ).fetchone()

            if not row:
                return

            # Update provided metrics
            updates = []
            values = []

            if views is not None:
                updates.append("views = ?")
                values.append(views)
            if likes is not None:
                updates.append("likes = ?")
                values.append(likes)
            if comments is not None:
                updates.append("comments = ?")
                values.append(comments)
            if shares is not None:
                updates.append("shares = ?")
                values.append(shares)
            if clicks is not None:
                updates.append("clicks = ?")
                values.append(clicks)
            if conversions is not None:
                updates.append("conversions = ?")
                values.append(conversions)
            if revenue is not None:
                updates.append("revenue = ?")
                values.append(revenue)

            if not updates:
                return

            # Calculate performance score
            v = views or 0
            l = likes or 0
            c = comments or 0
            s = shares or 0
            cl = clicks or 0

            score = (
                v * self.weights["views"] +
                l * self.weights["likes"] +
                c * self.weights["comments"] +
                s * self.weights["shares"] +
                cl * self.weights["clicks"]
            )

            updates.append("performance_score = ?")
            values.append(score)

            values.append(content_id)

            conn.execute(f"""
                UPDATE content_performance
                SET {', '.join(updates)}
                WHERE content_id = ?
            """, values)

    def analyze_patterns(self) -> Dict:
        """Analyze what patterns are working best"""

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            patterns = {}

            # Best hook styles
            hooks = conn.execute("""
                SELECT hook_style,
                       COUNT(*) as count,
                       AVG(performance_score) as avg_score,
                       SUM(clicks) as total_clicks
                FROM content_performance
                WHERE posted_at >= datetime('now', '-30 days')
                GROUP BY hook_style
                HAVING count >= 3
                ORDER BY avg_score DESC
            """).fetchall()

            patterns["hooks"] = [
                {"style": h["hook_style"], "count": h["count"],
                 "avg_score": round(h["avg_score"], 2), "clicks": h["total_clicks"]}
                for h in hooks
            ]

            # Best topics
            topics = conn.execute("""
                SELECT topic,
                       COUNT(*) as count,
                       AVG(performance_score) as avg_score,
                       SUM(clicks) as total_clicks
                FROM content_performance
                WHERE posted_at >= datetime('now', '-30 days')
                GROUP BY topic
                HAVING count >= 3
                ORDER BY avg_score DESC
            """).fetchall()

            patterns["topics"] = [
                {"topic": t["topic"], "count": t["count"],
                 "avg_score": round(t["avg_score"], 2), "clicks": t["total_clicks"]}
                for t in topics
            ]

            # Best products
            products = conn.execute("""
                SELECT product,
                       COUNT(*) as count,
                       AVG(performance_score) as avg_score,
                       SUM(clicks) as total_clicks,
                       SUM(conversions) as total_conversions,
                       SUM(revenue) as total_revenue
                FROM content_performance
                WHERE posted_at >= datetime('now', '-30 days')
                GROUP BY product
                HAVING count >= 3
                ORDER BY total_revenue DESC, avg_score DESC
            """).fetchall()

            patterns["products"] = [
                {"product": p["product"], "count": p["count"],
                 "avg_score": round(p["avg_score"], 2), "clicks": p["total_clicks"],
                 "conversions": p["total_conversions"], "revenue": p["total_revenue"]}
                for p in products
            ]

            # Best posting times
            times = conn.execute("""
                SELECT hour_posted,
                       COUNT(*) as count,
                       AVG(performance_score) as avg_score
                FROM content_performance
                WHERE posted_at >= datetime('now', '-30 days')
                GROUP BY hour_posted
                HAVING count >= 3
                ORDER BY avg_score DESC
            """).fetchall()

            patterns["best_times"] = [
                {"hour": t["hour_posted"], "count": t["count"],
                 "avg_score": round(t["avg_score"], 2)}
                for t in times
            ]

            # Best days
            days = conn.execute("""
                SELECT day_of_week,
                       COUNT(*) as count,
                       AVG(performance_score) as avg_score
                FROM content_performance
                WHERE posted_at >= datetime('now', '-30 days')
                GROUP BY day_of_week
                HAVING count >= 3
                ORDER BY avg_score DESC
            """).fetchall()

            day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            patterns["best_days"] = [
                {"day": day_names[d["day_of_week"]], "count": d["count"],
                 "avg_score": round(d["avg_score"], 2)}
                for d in days
            ]

            return patterns

    def get_recommendations(self) -> Dict:
        """Get AI-powered recommendations for next content"""

        patterns = self.analyze_patterns()

        recommendations = {
            "timestamp": datetime.now().isoformat(),
            "hook_style": None,
            "topic": None,
            "product": None,
            "post_time": None,
            "reasoning": []
        }

        # Recommend best performing hook style (with some exploration)
        if patterns["hooks"]:
            if random.random() < 0.8:  # 80% exploit best, 20% explore
                best_hook = patterns["hooks"][0]
                recommendations["hook_style"] = best_hook["style"]
                recommendations["reasoning"].append(
                    f"Using '{best_hook['style']}' hook - avg score {best_hook['avg_score']}"
                )
            else:
                # Explore a random style
                all_hooks = ["hook", "tutorial", "storytime", "comparison", "results", "controversy"]
                used_hooks = [h["style"] for h in patterns["hooks"]]
                unused = [h for h in all_hooks if h not in used_hooks]
                if unused:
                    recommendations["hook_style"] = random.choice(unused)
                    recommendations["reasoning"].append(
                        f"Exploring '{recommendations['hook_style']}' hook (testing new style)"
                    )

        # Recommend best topic
        if patterns["topics"]:
            best_topic = patterns["topics"][0]
            recommendations["topic"] = best_topic["topic"]
            recommendations["reasoning"].append(
                f"Topic '{best_topic['topic']}' has {best_topic['clicks']} clicks"
            )

        # Recommend best converting product
        if patterns["products"]:
            # Prioritize by revenue, then score
            best_product = patterns["products"][0]
            recommendations["product"] = best_product["product"]
            recommendations["reasoning"].append(
                f"'{best_product['product']}' has ${best_product['revenue']:.2f} revenue"
            )

        # Recommend best posting time
        if patterns["best_times"]:
            best_time = patterns["best_times"][0]
            recommendations["post_time"] = best_time["hour"]
            recommendations["reasoning"].append(
                f"Best posting time: {best_time['hour']}:00 (score {best_time['avg_score']})"
            )

        return recommendations

    def update_strategy(self):
        """Automatically update strategy based on learnings"""

        patterns = self.analyze_patterns()

        with sqlite3.connect(self.db_path) as conn:
            # Update preferred hooks
            if patterns["hooks"]:
                top_hooks = [h["style"] for h in patterns["hooks"][:4]]
                conn.execute("""
                    UPDATE strategy_config SET value = ?, updated_at = ?
                    WHERE key = 'preferred_hooks'
                """, (json.dumps(top_hooks), datetime.now()))

            # Update preferred times
            if patterns["best_times"]:
                top_times = [t["hour"] for t in patterns["best_times"][:3]]
                conn.execute("""
                    UPDATE strategy_config SET value = ?, updated_at = ?
                    WHERE key = 'preferred_times'
                """, (json.dumps(top_times), datetime.now()))

            # Store winning patterns
            for hook in patterns["hooks"][:5]:
                conn.execute("""
                    INSERT OR REPLACE INTO winning_patterns
                    (pattern_type, pattern_value, sample_size, avg_score, confidence, last_updated)
                    VALUES ('hook', ?, ?, ?, ?, ?)
                """, (
                    hook["style"],
                    hook["count"],
                    hook["avg_score"],
                    min(hook["count"] / 10, 1.0),  # Confidence based on sample size
                    datetime.now()
                ))

    def start_ab_test(self, test_name: str, variant_a: str, variant_b: str) -> int:
        """Start a new A/B test"""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO ab_tests (test_name, variant_a, variant_b, status)
                VALUES (?, ?, ?, 'running')
            """, (test_name, variant_a, variant_b))
            return cursor.lastrowid

    def record_ab_result(self, test_id: int, variant: str, score: float):
        """Record result for an A/B test variant"""

        with sqlite3.connect(self.db_path) as conn:
            if variant == 'a':
                conn.execute("""
                    UPDATE ab_tests
                    SET a_impressions = a_impressions + 1,
                        a_score = a_score + ?
                    WHERE id = ?
                """, (score, test_id))
            else:
                conn.execute("""
                    UPDATE ab_tests
                    SET b_impressions = b_impressions + 1,
                        b_score = b_score + ?
                    WHERE id = ?
                """, (score, test_id))

            # Check if we have enough data to declare winner
            test = conn.execute(
                "SELECT * FROM ab_tests WHERE id = ?", (test_id,)
            ).fetchone()

            if test:
                total = test[4] + test[5]  # a_impressions + b_impressions
                if total >= 100:  # Minimum sample size
                    a_avg = test[6] / max(test[4], 1)
                    b_avg = test[7] / max(test[5], 1)

                    # Simple winner determination (could use statistical significance)
                    if a_avg > b_avg * 1.1:  # A is 10% better
                        winner = 'a'
                    elif b_avg > a_avg * 1.1:  # B is 10% better
                        winner = 'b'
                    else:
                        winner = 'tie'

                    conn.execute("""
                        UPDATE ab_tests SET winner = ?, status = 'completed'
                        WHERE id = ?
                    """, (winner, test_id))

    def get_ab_tests(self, status: str = None) -> List[Dict]:
        """Get A/B tests"""

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            if status:
                rows = conn.execute(
                    "SELECT * FROM ab_tests WHERE status = ?", (status,)
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM ab_tests").fetchall()

            return [dict(row) for row in rows]

    def get_performance_report(self, days: int = 30) -> Dict:
        """Generate comprehensive performance report"""

        cutoff = datetime.now() - timedelta(days=days)

        with sqlite3.connect(self.db_path) as conn:
            # Overall stats
            totals = conn.execute("""
                SELECT
                    COUNT(*) as total_posts,
                    SUM(views) as total_views,
                    SUM(likes) as total_likes,
                    SUM(comments) as total_comments,
                    SUM(shares) as total_shares,
                    SUM(clicks) as total_clicks,
                    SUM(conversions) as total_conversions,
                    SUM(revenue) as total_revenue,
                    AVG(performance_score) as avg_score
                FROM content_performance
                WHERE posted_at >= ?
            """, (cutoff,)).fetchone()

            # Daily breakdown
            daily = conn.execute("""
                SELECT
                    DATE(posted_at) as date,
                    COUNT(*) as posts,
                    SUM(views) as views,
                    SUM(clicks) as clicks,
                    SUM(revenue) as revenue
                FROM content_performance
                WHERE posted_at >= ?
                GROUP BY DATE(posted_at)
                ORDER BY date DESC
            """, (cutoff,)).fetchall()

            # Patterns
            patterns = self.analyze_patterns()

            # Recommendations
            recommendations = self.get_recommendations()

            return {
                "period_days": days,
                "totals": {
                    "posts": totals[0] or 0,
                    "views": totals[1] or 0,
                    "likes": totals[2] or 0,
                    "comments": totals[3] or 0,
                    "shares": totals[4] or 0,
                    "clicks": totals[5] or 0,
                    "conversions": totals[6] or 0,
                    "revenue": round(totals[7] or 0, 2),
                    "avg_score": round(totals[8] or 0, 2),
                },
                "daily": [
                    {"date": d[0], "posts": d[1], "views": d[2], "clicks": d[3], "revenue": d[4]}
                    for d in daily
                ],
                "patterns": patterns,
                "recommendations": recommendations,
            }


def main():
    """Demo the adaptive engine"""

    engine = AdaptiveEngine()

    print("=" * 60)
    print("ADAPTIVE LEARNING ENGINE")
    print("=" * 60)

    # Simulate some content performance data
    print("\n📊 Simulating content data...")

    import random

    hooks = ["hook", "tutorial", "storytime", "comparison", "results"]
    products = ["Jasper", "Copy.ai", "Writesonic"]
    topics = ["ai writing", "productivity", "passive income"]

    for i in range(50):
        content_id = f"content_{i}"
        hook = random.choice(hooks)
        product = random.choice(products)
        topic = random.choice(topics)

        # Record content
        engine.record_content(
            content_id=content_id,
            platform="tiktok",
            content_type="video",
            hook_style=hook,
            topic=topic,
            product=product,
            posted_at=datetime.now() - timedelta(days=random.randint(1, 30))
        )

        # Simulate performance (some hooks perform better)
        base_views = random.randint(100, 5000)
        if hook == "hook":
            base_views *= 1.5
        if hook == "tutorial":
            base_views *= 1.3

        engine.update_metrics(
            content_id=content_id,
            views=int(base_views),
            likes=int(base_views * random.uniform(0.02, 0.1)),
            comments=int(base_views * random.uniform(0.005, 0.02)),
            shares=int(base_views * random.uniform(0.001, 0.01)),
            clicks=int(base_views * random.uniform(0.01, 0.05)),
            conversions=random.randint(0, 3),
            revenue=random.uniform(0, 50)
        )

    # Show patterns
    print("\n🎯 WINNING PATTERNS:")
    patterns = engine.analyze_patterns()

    print("\nBest Hooks:")
    for h in patterns["hooks"][:3]:
        print(f"  • {h['style']}: score {h['avg_score']}, {h['clicks']} clicks")

    print("\nBest Topics:")
    for t in patterns["topics"][:3]:
        print(f"  • {t['topic']}: score {t['avg_score']}")

    print("\nBest Products:")
    for p in patterns["products"][:3]:
        print(f"  • {p['product']}: ${p['revenue']:.2f} revenue")

    print("\nBest Times:")
    for t in patterns["best_times"][:3]:
        print(f"  • {t['hour']}:00: score {t['avg_score']}")

    # Get recommendations
    print("\n💡 RECOMMENDATIONS:")
    recs = engine.get_recommendations()
    print(f"  Hook: {recs['hook_style']}")
    print(f"  Topic: {recs['topic']}")
    print(f"  Product: {recs['product']}")
    print(f"  Post at: {recs['post_time']}:00")

    print("\n  Reasoning:")
    for r in recs['reasoning']:
        print(f"    • {r}")


if __name__ == "__main__":
    main()
