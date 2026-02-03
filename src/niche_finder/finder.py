"""
Niche Finder - Discover profitable affiliate niches
Uses free methods: Google Trends, Reddit, social signals
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re


class NicheFinder:
    """Find profitable niches for affiliate marketing"""

    def __init__(self):
        self.trends_url = "https://trends.google.com/trends/api/dailytrends"
        self.reddit_url = "https://www.reddit.com"

    def get_trending_searches(self, geo: str = "US") -> List[Dict]:
        """Get trending searches from Google Trends (free, no API needed)"""
        try:
            url = f"{self.trends_url}?geo={geo}&hl=en-US"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = response.read().decode("utf-8")
                # Google Trends returns JSONP, strip the prefix
                json_data = json.loads(data[5:] if data.startswith(")]}',") else data)
                trends = []
                for day in json_data.get("default", {}).get("trendingSearchesDays", []):
                    for search in day.get("trendingSearches", []):
                        trends.append({
                            "title": search.get("title", {}).get("query", ""),
                            "traffic": search.get("formattedTraffic", ""),
                            "related": [q.get("query", "") for q in search.get("relatedQueries", [])]
                        })
                return trends[:20]
        except Exception as e:
            print(f"Error fetching trends: {e}")
            return []

    def get_subreddit_hot(self, subreddit: str, limit: int = 25) -> List[Dict]:
        """Get hot posts from a subreddit to find trending topics"""
        try:
            url = f"{self.reddit_url}/r/{subreddit}/hot.json?limit={limit}"
            req = urllib.request.Request(url, headers={"User-Agent": "NicheFinder/1.0"})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
                posts = []
                for post in data.get("data", {}).get("children", []):
                    post_data = post.get("data", {})
                    posts.append({
                        "title": post_data.get("title", ""),
                        "score": post_data.get("score", 0),
                        "comments": post_data.get("num_comments", 0),
                        "url": post_data.get("url", ""),
                    })
                return posts
        except Exception as e:
            print(f"Error fetching r/{subreddit}: {e}")
            return []

    def analyze_niche_potential(self, niche: str) -> Dict:
        """Analyze a niche's potential based on multiple signals"""

        # Subreddits to check for each niche category
        niche_subreddits = {
            "money": ["personalfinance", "sidehustle", "beermoney", "passive_income", "entrepreneur"],
            "tech": ["technology", "software", "SaaS", "startups"],
            "investing": ["investing", "stocks", "cryptocurrency", "wallstreetbets"],
            "business": ["smallbusiness", "Entrepreneur", "dropship"],
            "marketing": ["marketing", "affiliatemarketing", "SEO", "socialmedia"],
        }

        # Determine relevant subreddits
        relevant_subs = []
        niche_lower = niche.lower()
        for category, subs in niche_subreddits.items():
            if any(word in niche_lower for word in category.split()):
                relevant_subs.extend(subs)

        if not relevant_subs:
            relevant_subs = ["Entrepreneur", "sidehustle"]  # Default

        # Gather signals
        signals = {
            "niche": niche,
            "reddit_activity": [],
            "trending_related": [],
            "score": 0,
        }

        # Check Reddit activity
        for sub in relevant_subs[:3]:
            posts = self.get_subreddit_hot(sub, limit=10)
            matching = [p for p in posts if niche_lower in p["title"].lower()]
            if matching:
                signals["reddit_activity"].extend(matching)

        # Calculate potential score (0-100)
        score = 0
        score += min(len(signals["reddit_activity"]) * 10, 40)  # Reddit presence
        score += 30 if len(relevant_subs) > 2 else 15  # Multiple relevant communities
        score += 30  # Base score for being researched

        signals["score"] = min(score, 100)
        signals["recommendation"] = self._get_recommendation(score)

        return signals

    def _get_recommendation(self, score: int) -> str:
        if score >= 70:
            return "HIGH POTENTIAL - Strong signals, pursue aggressively"
        elif score >= 50:
            return "MODERATE POTENTIAL - Worth testing with content"
        elif score >= 30:
            return "LOW POTENTIAL - May need more specific angle"
        else:
            return "RESEARCH MORE - Insufficient data"

    def find_content_gaps(self, niche: str) -> List[str]:
        """Find content ideas that aren't saturated"""

        content_angles = [
            f"best {niche} for beginners 2024",
            f"{niche} vs [competitor] comparison",
            f"how to start {niche} with no money",
            f"{niche} mistakes to avoid",
            f"is {niche} worth it in 2024",
            f"{niche} honest review",
            f"free alternatives to {niche}",
            f"{niche} tutorial step by step",
            f"{niche} case study",
            f"how I made money with {niche}",
        ]

        return content_angles

    def get_affiliate_match(self, niche: str) -> List[Dict]:
        """Match niche to relevant affiliate programs"""
        from config.settings import AFFILIATE_PROGRAMS

        matches = []
        niche_lower = niche.lower()

        keyword_mapping = {
            "hosting": ["hosting", "website", "blog", "wordpress"],
            "saas_tools": ["email", "marketing", "funnel", "automation", "tool"],
            "ai_tools": ["ai", "writing", "content", "copy", "chatgpt"],
            "courses_education": ["learn", "course", "skill", "education", "training"],
            "finance": ["invest", "money", "trading", "crypto", "stock", "finance"],
            "ecommerce": ["shop", "store", "ecommerce", "dropship", "sell"],
        }

        for category, keywords in keyword_mapping.items():
            if any(kw in niche_lower for kw in keywords):
                matches.extend(AFFILIATE_PROGRAMS.get(category, []))

        return matches


def main():
    """Demo the niche finder"""
    finder = NicheFinder()

    print("=" * 60)
    print("NICHE FINDER - Affiliate Marketing Research Tool")
    print("=" * 60)

    # Test niches
    test_niches = [
        "ai writing tools",
        "passive income ideas",
        "best web hosting",
        "learn to code",
        "crypto trading bots",
    ]

    for niche in test_niches:
        print(f"\n{'='*60}")
        print(f"Analyzing: {niche.upper()}")
        print("=" * 60)

        # Analyze potential
        analysis = finder.analyze_niche_potential(niche)
        print(f"\nPotential Score: {analysis['score']}/100")
        print(f"Recommendation: {analysis['recommendation']}")

        # Get content ideas
        print(f"\nContent Ideas:")
        for idea in finder.find_content_gaps(niche)[:5]:
            print(f"  - {idea}")

        # Match affiliate programs
        programs = finder.get_affiliate_match(niche)
        if programs:
            print(f"\nMatching Affiliate Programs:")
            for prog in programs[:3]:
                print(f"  - {prog['name']}: {prog['commission']}")


if __name__ == "__main__":
    main()
