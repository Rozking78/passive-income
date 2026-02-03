"""
Affiliate Link Tracker - Track clicks, conversions, and revenue
Uses SQLite for simple local storage
"""

import sqlite3
import hashlib
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path


class LinkTracker:
    """Track and manage affiliate links"""

    def __init__(self, db_path: str = "data/affiliate_tracker.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS links (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    short_code TEXT UNIQUE NOT NULL,
                    original_url TEXT NOT NULL,
                    product_name TEXT,
                    program TEXT,
                    commission TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT
                );

                CREATE TABLE IF NOT EXISTS clicks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    link_id INTEGER,
                    clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    source TEXT,
                    platform TEXT,
                    campaign TEXT,
                    FOREIGN KEY (link_id) REFERENCES links(id)
                );

                CREATE TABLE IF NOT EXISTS conversions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    link_id INTEGER,
                    converted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    amount REAL,
                    is_recurring BOOLEAN DEFAULT 0,
                    notes TEXT,
                    FOREIGN KEY (link_id) REFERENCES links(id)
                );

                CREATE TABLE IF NOT EXISTS campaigns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    platform TEXT,
                    start_date DATE,
                    end_date DATE,
                    budget REAL,
                    status TEXT DEFAULT 'active',
                    notes TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_clicks_link ON clicks(link_id);
                CREATE INDEX IF NOT EXISTS idx_clicks_date ON clicks(clicked_at);
                CREATE INDEX IF NOT EXISTS idx_conversions_link ON conversions(link_id);
            """)

    def _generate_short_code(self, url: str) -> str:
        """Generate a short code for tracking"""
        hash_obj = hashlib.md5(f"{url}{datetime.now().isoformat()}".encode())
        return hash_obj.hexdigest()[:8]

    # ==================== LINK MANAGEMENT ====================

    def add_link(self, original_url: str, product_name: str, program: str = "",
                 commission: str = "", notes: str = "") -> Dict:
        """Add a new affiliate link to track"""
        short_code = self._generate_short_code(original_url)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO links (short_code, original_url, product_name, program, commission, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (short_code, original_url, product_name, program, commission, notes))

            return {
                "id": cursor.lastrowid,
                "short_code": short_code,
                "original_url": original_url,
                "product_name": product_name,
                "tracking_url": f"?ref={short_code}",  # Use with your redirect
            }

    def get_links(self, limit: int = 50) -> List[Dict]:
        """Get all tracked links"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT l.*,
                       COUNT(DISTINCT c.id) as total_clicks,
                       COUNT(DISTINCT cv.id) as total_conversions,
                       COALESCE(SUM(cv.amount), 0) as total_revenue
                FROM links l
                LEFT JOIN clicks c ON l.id = c.link_id
                LEFT JOIN conversions cv ON l.id = cv.link_id
                GROUP BY l.id
                ORDER BY l.created_at DESC
                LIMIT ?
            """, (limit,)).fetchall()

            return [dict(row) for row in rows]

    def get_link_by_code(self, short_code: str) -> Optional[Dict]:
        """Get link details by short code"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM links WHERE short_code = ?", (short_code,)
            ).fetchone()
            return dict(row) if row else None

    # ==================== CLICK TRACKING ====================

    def record_click(self, short_code: str, source: str = "", platform: str = "",
                     campaign: str = "") -> bool:
        """Record a click on a link"""
        link = self.get_link_by_code(short_code)
        if not link:
            return False

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO clicks (link_id, source, platform, campaign)
                VALUES (?, ?, ?, ?)
            """, (link["id"], source, platform, campaign))

        return True

    def get_clicks(self, link_id: int = None, days: int = 30) -> List[Dict]:
        """Get click data, optionally filtered by link and date range"""
        cutoff = datetime.now() - timedelta(days=days)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            if link_id:
                rows = conn.execute("""
                    SELECT * FROM clicks
                    WHERE link_id = ? AND clicked_at >= ?
                    ORDER BY clicked_at DESC
                """, (link_id, cutoff)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT c.*, l.product_name, l.short_code
                    FROM clicks c
                    JOIN links l ON c.link_id = l.id
                    WHERE c.clicked_at >= ?
                    ORDER BY c.clicked_at DESC
                """, (cutoff,)).fetchall()

            return [dict(row) for row in rows]

    # ==================== CONVERSION TRACKING ====================

    def record_conversion(self, short_code: str, amount: float,
                          is_recurring: bool = False, notes: str = "") -> bool:
        """Record a conversion (sale)"""
        link = self.get_link_by_code(short_code)
        if not link:
            return False

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO conversions (link_id, amount, is_recurring, notes)
                VALUES (?, ?, ?, ?)
            """, (link["id"], amount, is_recurring, notes))

        return True

    def get_conversions(self, link_id: int = None, days: int = 30) -> List[Dict]:
        """Get conversion data"""
        cutoff = datetime.now() - timedelta(days=days)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            if link_id:
                rows = conn.execute("""
                    SELECT * FROM conversions
                    WHERE link_id = ? AND converted_at >= ?
                    ORDER BY converted_at DESC
                """, (link_id, cutoff)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT cv.*, l.product_name, l.short_code
                    FROM conversions cv
                    JOIN links l ON cv.link_id = l.id
                    WHERE cv.converted_at >= ?
                    ORDER BY cv.converted_at DESC
                """, (cutoff,)).fetchall()

            return [dict(row) for row in rows]

    # ==================== ANALYTICS ====================

    def get_dashboard_stats(self, days: int = 30) -> Dict:
        """Get dashboard statistics"""
        cutoff = datetime.now() - timedelta(days=days)

        with sqlite3.connect(self.db_path) as conn:
            # Total clicks
            total_clicks = conn.execute("""
                SELECT COUNT(*) FROM clicks WHERE clicked_at >= ?
            """, (cutoff,)).fetchone()[0]

            # Total conversions
            total_conversions = conn.execute("""
                SELECT COUNT(*) FROM conversions WHERE converted_at >= ?
            """, (cutoff,)).fetchone()[0]

            # Total revenue
            total_revenue = conn.execute("""
                SELECT COALESCE(SUM(amount), 0) FROM conversions WHERE converted_at >= ?
            """, (cutoff,)).fetchone()[0]

            # Recurring revenue
            recurring_revenue = conn.execute("""
                SELECT COALESCE(SUM(amount), 0) FROM conversions
                WHERE converted_at >= ? AND is_recurring = 1
            """, (cutoff,)).fetchone()[0]

            # Top performing links
            top_links = conn.execute("""
                SELECT l.product_name, l.short_code,
                       COUNT(DISTINCT c.id) as clicks,
                       COUNT(DISTINCT cv.id) as conversions,
                       COALESCE(SUM(cv.amount), 0) as revenue
                FROM links l
                LEFT JOIN clicks c ON l.id = c.link_id AND c.clicked_at >= ?
                LEFT JOIN conversions cv ON l.id = cv.link_id AND cv.converted_at >= ?
                GROUP BY l.id
                HAVING clicks > 0 OR conversions > 0
                ORDER BY revenue DESC, conversions DESC, clicks DESC
                LIMIT 10
            """, (cutoff, cutoff)).fetchall()

            # Clicks by platform
            clicks_by_platform = conn.execute("""
                SELECT platform, COUNT(*) as count
                FROM clicks
                WHERE clicked_at >= ? AND platform != ''
                GROUP BY platform
                ORDER BY count DESC
            """, (cutoff,)).fetchall()

            # Conversion rate
            conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0

            return {
                "period_days": days,
                "total_clicks": total_clicks,
                "total_conversions": total_conversions,
                "conversion_rate": round(conversion_rate, 2),
                "total_revenue": round(total_revenue, 2),
                "recurring_revenue": round(recurring_revenue, 2),
                "avg_revenue_per_conversion": round(total_revenue / total_conversions, 2) if total_conversions > 0 else 0,
                "top_links": [
                    {"product": row[0], "code": row[1], "clicks": row[2], "conversions": row[3], "revenue": row[4]}
                    for row in top_links
                ],
                "clicks_by_platform": dict(clicks_by_platform),
            }

    def get_revenue_by_day(self, days: int = 30) -> List[Dict]:
        """Get daily revenue breakdown"""
        cutoff = datetime.now() - timedelta(days=days)

        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("""
                SELECT DATE(converted_at) as date,
                       COUNT(*) as conversions,
                       SUM(amount) as revenue
                FROM conversions
                WHERE converted_at >= ?
                GROUP BY DATE(converted_at)
                ORDER BY date DESC
            """, (cutoff,)).fetchall()

            return [
                {"date": row[0], "conversions": row[1], "revenue": row[2]}
                for row in rows
            ]

    def project_monthly_revenue(self) -> Dict:
        """Project monthly revenue based on current trends"""
        stats_7d = self.get_dashboard_stats(7)
        stats_30d = self.get_dashboard_stats(30)

        daily_avg_7d = stats_7d["total_revenue"] / 7 if stats_7d["total_revenue"] > 0 else 0
        daily_avg_30d = stats_30d["total_revenue"] / 30 if stats_30d["total_revenue"] > 0 else 0

        return {
            "last_7_days": round(stats_7d["total_revenue"], 2),
            "last_30_days": round(stats_30d["total_revenue"], 2),
            "daily_average_7d": round(daily_avg_7d, 2),
            "daily_average_30d": round(daily_avg_30d, 2),
            "projected_monthly_7d_trend": round(daily_avg_7d * 30, 2),
            "projected_monthly_30d_trend": round(daily_avg_30d * 30, 2),
            "weekly_target": 10000,
            "monthly_target": 40000,
            "weekly_progress_pct": round((daily_avg_7d * 7) / 10000 * 100, 1),
        }


def main():
    """Demo the link tracker"""
    tracker = LinkTracker()

    print("=" * 60)
    print("LINK TRACKER - Affiliate Analytics")
    print("=" * 60)

    # Add some demo links
    demo_links = [
        {"url": "https://convertkit.com?ref=demo", "product": "ConvertKit", "program": "ConvertKit Affiliates", "commission": "30% recurring"},
        {"url": "https://jasper.ai?ref=demo", "product": "Jasper AI", "program": "Jasper Affiliates", "commission": "30% recurring"},
        {"url": "https://bluehost.com?ref=demo", "product": "Bluehost", "program": "Bluehost Affiliates", "commission": "$65-130/sale"},
    ]

    print("\n📎 Adding demo links...")
    for link_data in demo_links:
        result = tracker.add_link(
            link_data["url"],
            link_data["product"],
            link_data["program"],
            link_data["commission"]
        )
        print(f"  Added: {result['product_name']} -> {result['short_code']}")

    # Simulate some activity
    print("\n📊 Recording demo activity...")
    links = tracker.get_links()
    for link in links[:2]:
        for _ in range(5):
            tracker.record_click(link["short_code"], platform="youtube")
        tracker.record_conversion(link["short_code"], 29.99, is_recurring=True)

    # Show stats
    print("\n📈 Dashboard Stats (Demo):")
    stats = tracker.get_dashboard_stats()
    print(f"  Total Clicks: {stats['total_clicks']}")
    print(f"  Total Conversions: {stats['total_conversions']}")
    print(f"  Conversion Rate: {stats['conversion_rate']}%")
    print(f"  Total Revenue: ${stats['total_revenue']}")

    print("\n💰 Revenue Projection:")
    projection = tracker.project_monthly_revenue()
    print(f"  Weekly Target: ${projection['weekly_target']}")
    print(f"  Current Weekly Pace: ${projection['daily_average_7d'] * 7:.2f}")
    print(f"  Progress: {projection['weekly_progress_pct']}%")


if __name__ == "__main__":
    main()
