"""
Affiliate Marketing Automation - Configuration
"""

# High-paying affiliate programs to target
AFFILIATE_PROGRAMS = {
    "hosting": [
        {"name": "Bluehost", "commission": "$65-130/sale", "cookie": "90 days", "url": "https://www.bluehost.com/affiliates"},
        {"name": "Cloudways", "commission": "$50-125/sale", "cookie": "90 days", "url": "https://www.cloudways.com/en/affiliate.php"},
        {"name": "SiteGround", "commission": "$50-100/sale", "cookie": "60 days", "url": "https://www.siteground.com/affiliates"},
    ],
    "saas_tools": [
        {"name": "ConvertKit", "commission": "30% recurring", "cookie": "90 days", "url": "https://convertkit.com/affiliates"},
        {"name": "Kajabi", "commission": "30% recurring", "cookie": "30 days", "url": "https://kajabi.com/affiliates"},
        {"name": "ClickFunnels", "commission": "30% recurring", "cookie": "45 days", "url": "https://www.clickfunnels.com/affiliates"},
        {"name": "Systeme.io", "commission": "50% recurring", "cookie": "lifetime", "url": "https://systeme.io/affiliates"},
    ],
    "ai_tools": [
        {"name": "Jasper", "commission": "30% recurring", "cookie": "30 days", "url": "https://www.jasper.ai/affiliates"},
        {"name": "Copy.ai", "commission": "45% first year", "cookie": "60 days", "url": "https://www.copy.ai/affiliates"},
        {"name": "Writesonic", "commission": "30% recurring", "cookie": "60 days", "url": "https://writesonic.com/affiliates"},
    ],
    "courses_education": [
        {"name": "Skillshare", "commission": "$7/free trial", "cookie": "30 days", "url": "https://www.skillshare.com/affiliates"},
        {"name": "Coursera", "commission": "10-45%", "cookie": "30 days", "url": "https://about.coursera.org/affiliates"},
        {"name": "Teachable", "commission": "30% recurring", "cookie": "90 days", "url": "https://teachable.com/affiliates"},
    ],
    "finance": [
        {"name": "Webull", "commission": "$30-150/referral", "cookie": "varies", "url": "https://www.webull.com/activity"},
        {"name": "Coinbase", "commission": "50% of fees 3mo", "cookie": "30 days", "url": "https://www.coinbase.com/affiliates"},
        {"name": "Acorns", "commission": "$10-30/signup", "cookie": "30 days", "url": "https://www.acorns.com/affiliate/"},
    ],
    "ecommerce": [
        {"name": "Shopify", "commission": "$150/paid plan", "cookie": "30 days", "url": "https://www.shopify.com/affiliates"},
        {"name": "BigCommerce", "commission": "200% first payment", "cookie": "90 days", "url": "https://www.bigcommerce.com/affiliates/"},
    ]
}

# Profitable niches to research
NICHE_CATEGORIES = [
    "make money online",
    "personal finance",
    "investing for beginners",
    "side hustles",
    "ai tools",
    "productivity software",
    "online business",
    "freelancing",
    "dropshipping",
    "crypto trading",
    "web hosting reviews",
    "email marketing",
    "course creation",
    "remote work tools",
    "health and fitness apps",
]

# Content platforms to target
PLATFORMS = {
    "youtube": {"type": "video", "monetization": "high", "effort": "high"},
    "tiktok": {"type": "video", "monetization": "medium", "effort": "low"},
    "instagram": {"type": "mixed", "monetization": "medium", "effort": "medium"},
    "pinterest": {"type": "image", "monetization": "medium", "effort": "low"},
    "twitter": {"type": "text", "monetization": "low", "effort": "low"},
    "blog": {"type": "text", "monetization": "high", "effort": "high"},
    "medium": {"type": "text", "monetization": "medium", "effort": "medium"},
}

# Database settings
DATABASE_PATH = "data/affiliate_tracker.db"

# API Keys (to be filled in)
API_KEYS = {
    "openai": "",  # For content generation
    "serpapi": "",  # For keyword research
    "twitter": "",  # For social posting
    "tiktok": "",  # For TikTok posting
}
