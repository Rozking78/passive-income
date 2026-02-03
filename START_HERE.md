# START HERE - Step by Step Guide

## Your Goal: $10,000/week from Affiliate Marketing

Follow these steps in order. Check off each one as you complete it.

---

## PHASE 1: SETUP (Do Today - 30 minutes)

### Step 1: Install Dependencies
Open Terminal and run:
```bash
cd /Users/roswellking/Desktop/passive-income
pip3 install moviepy gTTS Pillow
```

If you don't have FFmpeg:
```bash
brew install ffmpeg
```

### Step 1.5: Setup Viral Media (Music & Backgrounds)
```bash
python3 setup_media.py
```
This downloads royalty-free music and creates gradient backgrounds.

**Optional - For More Video Variety:**
1. Get free API key: https://www.pexels.com/api/
2. Add to `.env` file: `PEXELS_API_KEY=your-key-here`

### Step 2: Sign Up for Affiliate Programs

Sign up for these (free to join):

| Program | Commission | Sign Up Link |
|---------|------------|--------------|
| **Jasper** | 30% recurring (~$15/mo per customer) | https://jasper.ai/affiliates |
| **Copy.ai** | 45% first year | https://copy.ai/affiliates |
| **Writesonic** | 30% recurring | https://writesonic.com/affiliates |

**Do this now:** Open each link, create an account, get your affiliate links.

### Step 3: Add Your Links to the Tracker
```bash
cd /Users/roswellking/Desktop/passive-income
python3 main.py
# Select option 7 (Add New Link)
# Add each affiliate link
```

### Step 4: Create Your TikTok Account
1. Download TikTok app
2. Create account (use business email)
3. Set username related to AI/productivity
4. Bio: "AI tools that save you hours ⬇️"
5. Add Linktree or Stan Store link in bio

### Step 5: Set Up Your Bio Link
Option A - **Linktree** (free):
1. Go to linktr.ee
2. Create account
3. Add your affiliate links with titles like:
   - "Try Jasper FREE (7 days)"
   - "Copy.ai - Free Plan"

Option B - **Stan Store** (better, $29/mo):
1. Go to stan.store
2. Set up store
3. Add affiliate products

---

## PHASE 2: CREATE YOUR FIRST CONTENT (Do Today - 1 hour)

### Step 6: Generate Your First Videos
```bash
cd /Users/roswellking/Desktop/passive-income
python3 automate.py run 3
```

This creates 3 videos automatically in `content/videos/`

### Step 7: Review the Videos
1. Open `content/videos/` folder
2. Watch each video
3. Check `content/tiktok_queue/` for captions

### Step 8: Post Your First TikTok

**Option A: Desktop (easier)**
1. Go to tiktok.com/upload
2. Upload video from `content/videos/`
3. Copy caption from matching `.json` file in `content/tiktok_queue/`
4. Add hashtags from the file
5. Post!

**Option B: Mobile**
1. AirDrop videos to phone
2. Open TikTok → tap +
3. Select Upload → choose video
4. Paste caption
5. Post!

### Step 9: Post All 3 Videos
- Post 1 video now
- Post 1 video at 12pm
- Post 1 video at 7pm

---

## PHASE 3: DAILY ROUTINE (15 min/day)

### Every Morning (5 min):
```bash
cd /Users/roswellking/Desktop/passive-income
python3 automate.py run 3
```
This generates your daily content.

### Throughout the Day (5 min):
- Post videos at: 7am, 12pm, 7pm
- Reply to ANY comments (algorithm loves this)

### Every Evening (5 min):
Check your stats and update the system:
```bash
python3 automate.py
# Select option 6 (Update Metrics)
# Enter views, likes, clicks for each video
```

---

## PHASE 4: WEEKLY REVIEW (30 min/week)

### Every Sunday:
```bash
python3 automate.py learn
```

This shows:
- Which hooks are working best
- Which products convert best
- Best times to post

**Adjust your strategy based on the data.**

---

## POSTING SCHEDULE

| Day | Videos | Times |
|-----|--------|-------|
| Mon | 3 | 7am, 12pm, 7pm |
| Tue | 3 | 7am, 12pm, 7pm |
| Wed | 3 | 7am, 12pm, 7pm |
| Thu | 3 | 7am, 12pm, 7pm |
| Fri | 3 | 7am, 12pm, 7pm |
| Sat | 2 | 10am, 7pm |
| Sun | 2 | 10am, 7pm |

**Total: 19 videos/week**

---

## QUICK REFERENCE COMMANDS

```bash
# Go to project folder
cd /Users/roswellking/Desktop/passive-income

# Generate 3 videos (daily task)
python3 automate.py run 3

# Interactive dashboard
python3 automate.py

# See what's working
python3 automate.py learn

# Check your stats
python3 automate.py status

# Generate scripts only (no video)
python3 generate.py tiktok 5
```

---

## REVENUE MILESTONES

| Week | Expected | Cumulative |
|------|----------|------------|
| 1-2 | $0 | Building audience |
| 3-4 | $50-200 | First conversions |
| 5-8 | $200-500/week | Finding winners |
| 9-12 | $500-2000/week | Scaling |
| 13-20 | $2000-5000/week | Optimizing |
| 21+ | $5000-10000/week | Full scale |

---

## TROUBLESHOOTING

**"No views on my videos"**
- Post more (volume wins)
- Use trending sounds
- Hook must grab attention in first 1 second
- Post at peak times (7am, 12pm, 7pm)

**"Views but no clicks"**
- Make sure link in bio works
- Mention "link in bio" in video
- CTA should be clear

**"Clicks but no conversions"**
- Try different products
- Check affiliate link is correct
- Landing page might be the issue

**"Video creation failed"**
```bash
brew install ffmpeg
pip3 install moviepy gTTS Pillow
```

---

## YOUR FIRST WEEK CHECKLIST

### Day 1 (Today):
- [ ] Install dependencies
- [ ] Sign up for Jasper affiliate
- [ ] Sign up for Copy.ai affiliate
- [ ] Create TikTok account
- [ ] Set up Linktree with affiliate links
- [ ] Generate 3 videos
- [ ] Post first video

### Day 2-7:
- [ ] Post 3 videos daily
- [ ] Reply to all comments
- [ ] Generate new content each morning
- [ ] Track metrics each evening

### End of Week 1:
- [ ] Run `python3 automate.py learn`
- [ ] Review what's working
- [ ] Adjust strategy if needed

---

## REMEMBER

1. **Consistency beats perfection** - Post every day, even if not perfect
2. **Volume wins** - More videos = more chances to go viral
3. **Engage with comments** - TikTok rewards engagement
4. **Track everything** - The system learns and improves
5. **Be patient** - Real results take 4-8 weeks

---

## NEED HELP?

All your tools:
```bash
cd /Users/roswellking/Desktop/passive-income
python3 automate.py    # Full automation
python3 main.py        # Dashboard & tracking
python3 generate.py    # Content generation
```

GitHub backup: https://github.com/Rozking78/passive-income

---

**START NOW: Open Terminal and run:**
```bash
cd /Users/roswellking/Desktop/passive-income
pip3 install moviepy gTTS Pillow
python3 automate.py run 3
```

Then post your first video!
