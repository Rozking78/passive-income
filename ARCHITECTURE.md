# Passive Income Automation System - Architecture

## Overview
Automated affiliate marketing system targeting $10k/week through AI-powered content creation, video generation, and multi-platform distribution.

**Current Focus**: AI Writing Tools (Jasper, Copy.ai, Writesonic, Rytr)

---

## Directory Structure

```
passive-income/
├── automate.py              # Main automation entry point
├── main.py                  # Interactive CLI menu
├── generate.py              # Quick content generation
├── setup_media.py           # Download stock music/videos
│
├── config/
│   └── settings.py          # Affiliate programs, niches, API keys
│
├── src/
│   ├── content_engine/      # Content generation
│   │   ├── generator.py         # Basic content templates
│   │   ├── auto_generator.py    # AI-powered generation
│   │   └── psychology_hooks.py  # Psychology-based copywriting
│   │
│   ├── video_engine/        # Video creation
│   │   ├── video_creator.py     # Basic slideshow videos
│   │   ├── viral_video_creator.py # Full viral videos with stock footage
│   │   ├── voiceover.py         # Edge TTS natural voiceovers
│   │   ├── auto_poster.py       # Platform posting/queueing
│   │   └── adaptive_engine.py   # ML-based optimization
│   │
│   ├── link_tracker/        # Affiliate link tracking
│   │   └── tracker.py           # SQLite-based tracking
│   │
│   └── niche_finder/        # Niche research
│       └── finder.py            # Reddit/trend analysis
│
├── content/                 # Generated content
│   ├── videos/              # Output videos
│   ├── voiceovers/          # Generated audio
│   ├── stock_media/
│   │   ├── videos/          # Pexels/Pixabay footage
│   │   └── music/           # Royalty-free music
│   └── tiktok_queue/        # Videos ready to post
│
├── data/
│   └── affiliate_tracker.db # SQLite database
│
└── templates/               # Email/landing page templates
```

---

## Core Components

### 1. Content Engine (`src/content_engine/`)

#### `psychology_hooks.py`
Psychology-based copywriting for wealth aspiration audience:
- **Hook Types**: Pain-to-aspiration, Identity, Curiosity, Social proof, Story, Transformation
- **Emotional Arc**: Pain → Discovery → Transformation → CTA
- **Key Lists**:
  - `ASPIRATIONS_FIRST_PERSON` - "Now I check my bank account"
  - `ASPIRATIONS_SECOND_PERSON` - "You could check your bank account"
  - `PAIN_POINTS` - Relatable struggles
  - `REALISTIC_OUTCOMES` - Believable results ($500/month, not $10k/day)

#### `auto_generator.py`
AI-powered content generation:
- TikTok scripts with style variations (hook, tutorial, story, rant)
- Product-specific content for each affiliate
- Caption and hashtag generation

### 2. Video Engine (`src/video_engine/`)

#### `viral_video_creator.py`
Full viral video creation:
- **Stock Footage**: Pexels API integration (psychology-aligned clips)
- **Multi-Clip Support**: Minimum 1 cut per video (pain → transformation visual journey)
- **Text Overlays**: Bold white text in upper third (TikTok safe zones)
- **Music**: Royalty-free from local cache, 20% volume
- **Output**: 1080x1920 MP4, 30fps

#### `voiceover.py`
Natural text-to-speech:
- **Engine**: Edge TTS (Microsoft Neural voices)
- **Voices**: Andrew (storyteller), Aria (energetic), Brian (confident), Ava (warm)
- **Processing**: Natural pacing, no awkward connectors

#### `adaptive_engine.py`
ML-based content optimization:
- Tracks performance by hook style, product, posting time
- Recommends best-performing combinations
- SQLite storage for historical data

### 3. Link Tracker (`src/link_tracker/`)

#### `tracker.py`
Affiliate link management:
- Short code generation
- Click/conversion tracking by platform
- Revenue analytics
- Dashboard stats

### 4. Automation (`automate.py`)

Full automation cycle:
1. Get AI recommendations (best hook/product/time)
2. Generate psychology-based scripts
3. Create videos with stock footage + voiceover
4. Queue for TikTok posting
5. Record for learning/optimization

---

## Data Flow

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Psychology     │────▶│  Auto Generator  │────▶│  Viral Video    │
│  Hooks          │     │  (scripts)       │     │  Creator        │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
┌─────────────────┐     ┌──────────────────┐              │
│  Pexels API     │────▶│  Stock Media     │──────────────┤
│  (videos)       │     │  Fetcher         │              │
└─────────────────┘     └──────────────────┘              │
                                                          │
┌─────────────────┐     ┌──────────────────┐              │
│  Edge TTS       │────▶│  Voiceover       │──────────────┤
│  (voices)       │     │  Generator       │              │
└─────────────────┘     └──────────────────┘              │
                                                          ▼
                                               ┌─────────────────┐
                                               │  Final Video    │
                                               │  (MP4 + Audio)  │
                                               └────────┬────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │  TikTok Queue   │
                                               │  (manual post)  │
                                               └─────────────────┘
```

---

## API Integrations

| Service | Purpose | Status |
|---------|---------|--------|
| Pexels | Stock video footage | ✅ Working |
| Edge TTS | Neural voiceovers | ✅ Working |
| Pixabay | Backup stock footage | ⚠️ Needs API key |
| TikTok | Auto-posting | ❌ Manual only |
| Twitter | Social posting | ❌ Not implemented |
| YouTube | Long-form content | ❌ Not implemented |

---

## Database Schema

### `affiliate_tracker.db`

```sql
-- Affiliate links
links (id, url, product_name, program, commission, short_code, created_at)

-- Click tracking
clicks (id, link_id, platform, campaign, ip_hash, user_agent, created_at)

-- Conversions
conversions (id, link_id, amount, is_recurring, notes, created_at)

-- Content performance (adaptive engine)
content_metrics (id, content_id, platform, hook_style, topic, product,
                 views, likes, comments, shares, clicks, conversions,
                 revenue, posted_at, created_at)
```

---

## Configuration

### Environment Variables (`.env`)
```
PEXELS_API_KEY=xxx          # Stock footage
PIXABAY_API_KEY=xxx         # Backup footage
TWITTER_API_KEY=xxx         # Social posting
TWITTER_API_SECRET=xxx
TWITTER_ACCESS_TOKEN=xxx
TWITTER_ACCESS_SECRET=xxx
```

### Target Affiliate Programs
- **Jasper**: 30% recurring
- **Copy.ai**: 45% first year
- **Writesonic**: 30% recurring
- **Rytr**: 30% recurring

---

## Usage

### Full Automation
```bash
python automate.py run 5    # Generate 5 videos
python automate.py status   # Show system status
python automate.py learn    # Show what's working
```

### Interactive Mode
```bash
python automate.py          # Interactive menu
python main.py              # Legacy interactive menu
```

### Quick Generation
```bash
python generate.py          # Generate single video
```

---

## Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Weekly Revenue | $10,000 | Tracking |
| Videos/Day | 3-5 | ✅ |
| Conversion Rate | 2-5% | Tracking |
| Views/Video | 10k+ | TBD |
