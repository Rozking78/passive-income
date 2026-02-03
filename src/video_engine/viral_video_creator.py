"""
Viral Video Creator
====================
Creates high-engagement TikTok/Reels videos with:
- Background stock footage (Pexels/Pixabay)
- Royalty-free trending music
- Dynamic voiceover (Edge TTS)
- Animated text overlays
- Pattern interrupts for retention
- Motivational hooks

Based on viral content research:
- Completion rate is #1 factor
- Hook in first 1-3 seconds
- Pattern interrupts every 2-3 seconds
- Text in upper third, avoid bottom 20%
- 3-7 words per text chunk
- Strong voice builds trust and engagement
"""

import os
import json
import random
import tempfile
import subprocess
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    from moviepy.editor import (
        VideoFileClip, AudioFileClip, ImageClip, TextClip,
        CompositeVideoClip, CompositeAudioClip, concatenate_videoclips,
        ColorClip, vfx
    )
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False


class StockMediaFetcher:
    """Fetches royalty-free videos and music from APIs"""

    def __init__(self, cache_dir: str = "content/stock_media"):
        self.cache_dir = Path(cache_dir)
        self.video_cache = self.cache_dir / "videos"
        self.music_cache = self.cache_dir / "music"
        self.video_cache.mkdir(parents=True, exist_ok=True)
        self.music_cache.mkdir(parents=True, exist_ok=True)

        # API keys (free tiers available)
        self.pexels_key = os.environ.get("PEXELS_API_KEY", "")
        self.pixabay_key = os.environ.get("PIXABAY_API_KEY", "")

        # Psychology-aligned video search terms
        # Matching the transformation narrative: Pain → Discovery → Freedom

        # Pain state visuals (relatable struggle)
        self.pain_visuals = [
            "stressed person working",
            "tired at desk",
            "person frustrated computer",
            "overwhelmed office",
            "exhausted working late",
            "burnout stress",
        ]

        # Discovery/Solution visuals
        self.discovery_visuals = [
            "laptop typing",
            "person using phone",
            "technology screen",
            "modern workspace",
            "creative working",
        ]

        # Transformation/Freedom visuals
        self.transformation_visuals = [
            "person relaxing beach",
            "freedom happy person",
            "celebrating success",
            "coffee morning relaxed",
            "travel lifestyle",
            "person smiling laptop",
            "financial freedom",
            "work from anywhere",
        ]

        # Aspirational/Luxury (use sparingly - believability)
        self.aspirational_visuals = [
            "modern city lifestyle",
            "luxury apartment view",
            "successful entrepreneur",
            "morning routine wealthy",
        ]

        # Combined default (balanced)
        self.motivational_terms = (
            self.pain_visuals[:2] +
            self.discovery_visuals +
            self.transformation_visuals[:4]
        )

        # Music moods for different content types
        self.music_moods = {
            "motivational": ["uplifting", "inspiring", "motivational", "epic"],
            "chill": ["lo-fi", "ambient", "chill", "relaxing"],
            "energetic": ["upbeat", "energetic", "electronic", "dance"],
            "dramatic": ["cinematic", "dramatic", "intense", "powerful"]
        }

    def fetch_psychology_videos(self, num_clips: int = 2) -> List[str]:
        """
        Fetch multiple videos matching the psychological journey:
        Pain → Discovery → Transformation

        Returns list of video paths for cutting between.
        """
        videos = []

        # Define the journey stages and their visuals
        stages = [
            ("pain", self.pain_visuals),
            ("discovery", self.discovery_visuals),
            ("transformation", self.transformation_visuals),
        ]

        # Fetch at least num_clips videos, spread across stages
        clips_per_stage = max(1, num_clips // len(stages))

        for stage_name, stage_terms in stages:
            query = random.choice(stage_terms)
            video = self.fetch_pexels_video(query)
            if video:
                videos.append(video)
            if len(videos) >= num_clips:
                break

        # If we don't have enough, fill with transformation visuals
        while len(videos) < num_clips:
            query = random.choice(self.transformation_visuals)
            video = self.fetch_pexels_video(query)
            if video and video not in videos:
                videos.append(video)
            else:
                # Use cached if API fails
                cached = self._get_cached_video()
                if cached and cached not in videos:
                    videos.append(cached)
                break

        return videos

    def fetch_pexels_video(self, query: str = None, orientation: str = "portrait") -> Optional[str]:
        """
        Fetch a video from Pexels API.
        Returns path to downloaded video.
        """
        if not self.pexels_key:
            return self._get_cached_video()

        query = query or random.choice(self.motivational_terms)

        # Check cache first
        cache_key = f"pexels_{query.replace(' ', '_')}"
        cached = list(self.video_cache.glob(f"{cache_key}*.mp4"))
        if cached:
            return str(random.choice(cached))

        try:
            url = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(query)}&orientation={orientation}&per_page=10"
            req = urllib.request.Request(url)
            req.add_header("Authorization", self.pexels_key)
            req.add_header("User-Agent", "Mozilla/5.0")

            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode())

            if data.get("videos"):
                video = random.choice(data["videos"])
                # Get HD quality video file - prefer portrait/vertical
                video_files = video.get("video_files", [])
                # Prefer 720p or 1080p portrait
                suitable = [v for v in video_files if v.get("height", 0) >= 720 and v.get("height", 0) > v.get("width", 0)]
                if not suitable:
                    suitable = [v for v in video_files if v.get("height", 0) >= 720]
                if suitable:
                    # Sort by height descending, take best quality
                    suitable.sort(key=lambda x: x.get("height", 0), reverse=True)
                    video_url = suitable[0]["link"]

                    # Download video
                    output_path = self.video_cache / f"{cache_key}_{video['id']}.mp4"
                    print(f"   Downloading Pexels video: {video['id']}...")

                    # Download with headers
                    dl_req = urllib.request.Request(video_url)
                    dl_req.add_header("User-Agent", "Mozilla/5.0")
                    with urllib.request.urlopen(dl_req, timeout=60) as response:
                        with open(output_path, 'wb') as f:
                            f.write(response.read())

                    print(f"   ✓ Downloaded: {output_path.name}")
                    return str(output_path)
        except Exception as e:
            print(f"Pexels API error: {e}")

        return self._get_cached_video()

    def fetch_pixabay_video(self, query: str = None) -> Optional[str]:
        """
        Fetch a video from Pixabay API.
        Returns path to downloaded video.
        """
        if not self.pixabay_key:
            return self._get_cached_video()

        query = query or random.choice(self.motivational_terms)

        # Check cache first
        cache_key = f"pixabay_{query.replace(' ', '_')}"
        cached = list(self.video_cache.glob(f"{cache_key}*.mp4"))
        if cached:
            return str(random.choice(cached))

        try:
            url = f"https://pixabay.com/api/videos/?key={self.pixabay_key}&q={urllib.parse.quote(query)}&per_page=10"

            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())

            if data.get("hits"):
                video = random.choice(data["hits"])
                # Get medium quality for balance of size/quality
                video_url = video.get("videos", {}).get("medium", {}).get("url")
                if video_url:
                    output_path = self.video_cache / f"{cache_key}_{video['id']}.mp4"
                    urllib.request.urlretrieve(video_url, output_path)
                    return str(output_path)
        except Exception as e:
            print(f"Pixabay API error: {e}")

        return self._get_cached_video()

    def fetch_background_video(self, query: str = None) -> Optional[str]:
        """Fetch a background video from available APIs"""
        # Try Pexels first, then Pixabay
        video = self.fetch_pexels_video(query)
        if not video:
            video = self.fetch_pixabay_video(query)
        return video

    def fetch_music(self, mood: str = "motivational") -> Optional[str]:
        """
        Fetch royalty-free music.
        Uses local cache or downloads from Pixabay.
        """
        # Check local music cache
        cached = list(self.music_cache.glob("*.mp3"))
        if cached:
            return str(random.choice(cached))

        if not self.pixabay_key:
            return None

        search_terms = self.music_moods.get(mood, ["motivational"])
        query = random.choice(search_terms)

        try:
            url = f"https://pixabay.com/api/?key={self.pixabay_key}&q={urllib.parse.quote(query)}&category=music&per_page=5"

            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())

            # Note: Pixabay's free API has limited music access
            # In production, you'd use their audio API or Mixkit
            if data.get("hits"):
                # For demo, we'll use the cache
                pass
        except Exception as e:
            print(f"Music API error: {e}")

        return None

    def _get_cached_video(self) -> Optional[str]:
        """Get a random video from cache"""
        cached = list(self.video_cache.glob("*.mp4"))
        if cached:
            return str(random.choice(cached))
        return None

    def get_local_music(self, category: str = "any") -> Optional[str]:
        """
        Get a music track from local cache.

        Categories:
        - "cinematic" / "epic" - dramatic, inspiring
        - "lofi" / "chill" - relaxed, ambient
        - "any" - random selection
        """
        music_files = list(self.music_cache.glob("*.mp3"))
        if not music_files:
            return None

        # Filter by category if specified
        if category in ["cinematic", "epic", "dramatic", "motivational"]:
            filtered = [f for f in music_files if any(x in f.name.lower() for x in ["cinematic", "epic", "motivational"])]
            if filtered:
                music_files = filtered
        elif category in ["lofi", "chill", "ambient", "soft"]:
            filtered = [f for f in music_files if any(x in f.name.lower() for x in ["lofi", "chill", "ambient", "soft", "study"])]
            if filtered:
                music_files = filtered

        return str(random.choice(music_files))

    def download_sample_videos(self):
        """Download some sample videos for offline use"""
        print("📥 Downloading sample background videos...")

        # These are free stock video URLs from Pexels/Pixabay CDN
        # In production, you'd fetch these via the API
        samples = [
            # Add sample video URLs here when you have API keys
        ]

        for i, url in enumerate(samples):
            try:
                output = self.video_cache / f"sample_{i}.mp4"
                if not output.exists():
                    urllib.request.urlretrieve(url, output)
                    print(f"  ✓ Downloaded sample_{i}.mp4")
            except Exception as e:
                print(f"  ✗ Failed to download sample {i}: {e}")


class ViralVideoCreator:
    """
    Creates viral-optimized short-form videos with:
    - Background footage
    - Text overlays
    - Music + Voiceover
    - Pattern interrupts
    """

    def __init__(self, output_dir: str = "content/videos"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.width = 1080
        self.height = 1920
        self.fps = 30

        self.media_fetcher = StockMediaFetcher()

        # Initialize voiceover generator
        try:
            from src.video_engine.voiceover import VoiceoverGenerator
            self.voiceover = VoiceoverGenerator()
            self.voiceover_available = self.voiceover.available or self.voiceover.fallback_available
        except ImportError:
            self.voiceover = None
            self.voiceover_available = False

        # Text positioning (upper third, avoid bottom 20%)
        # TikTok safe zones
        self.text_y_position = 0.25  # 25% from top (upper third)
        self.text_margin = 50

        # Visual styles
        self.text_styles = {
            "bold_white": {
                "fontsize": 80,
                "color": "white",
                "stroke_color": "black",
                "stroke_width": 4,
            },
            "neon_green": {
                "fontsize": 75,
                "color": "#00ff88",
                "stroke_color": "black",
                "stroke_width": 3,
            },
            "yellow_pop": {
                "fontsize": 85,
                "color": "#ffff00",
                "stroke_color": "black",
                "stroke_width": 5,
            },
            "minimal_white": {
                "fontsize": 70,
                "color": "white",
                "stroke_color": "none",
                "stroke_width": 0,
            }
        }

        # Hook templates for maximum engagement
        self.viral_hooks = [
            "This changed everything",
            "Nobody talks about this",
            "POV: You discovered",
            "The secret they hide",
            "Stop scrolling if you",
            "I wish I knew this sooner",
            "This is the sign you need",
            "What they don't tell you",
            "In 30 seconds you'll learn",
            "Wait for it..."
        ]

        # Pattern interrupt transitions
        self.pattern_interrupts = [
            "zoom_in",
            "shake",
            "flash",
            "glitch",
            "color_pop"
        ]

    def check_ffmpeg(self) -> bool:
        """Check if FFmpeg is available"""
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def create_viral_video(
        self,
        texts: List[str],
        background_query: str = None,
        music_path: str = None,
        style: str = "bold_white",
        add_hook: bool = True,
        add_voiceover: bool = True,
        voice_style: str = "motivational",
        output_name: str = None,
        min_cuts: int = 1,
        use_psychology_videos: bool = True
    ) -> Optional[str]:
        """
        Create a viral-optimized video.

        Args:
            texts: List of text strings to display (3-7 words each)
            add_voiceover: Whether to add dynamic voiceover
            voice_style: Voice style (motivational, tutorial, story, hype)
            background_query: Search term for background video
            music_path: Path to music file (optional)
            style: Text style name
            add_hook: Whether to add a hook at the start
            output_name: Custom output filename
            min_cuts: Minimum number of cuts (video changes) - default 1 means at least 2 clips
            use_psychology_videos: Use psychology-aligned video selection

        Returns:
            Path to created video
        """
        if not self.check_ffmpeg():
            print("Error: FFmpeg not found. Install with: brew install ffmpeg")
            return None

        if not PIL_AVAILABLE:
            print("Error: Pillow required. Run: pip install Pillow")
            return None

        # Add viral hook if requested
        if add_hook and texts:
            hook = random.choice(self.viral_hooks)
            texts = [hook] + texts

        # Ensure texts are short (3-7 words)
        texts = [self._shorten_text(t) for t in texts]

        # Fetch background videos - multiple clips for cuts
        num_clips = min_cuts + 1  # 1 cut = 2 clips, 2 cuts = 3 clips, etc.

        if use_psychology_videos:
            # Fetch psychology-aligned clips (pain → discovery → transformation)
            print(f"   Fetching {num_clips} psychology-aligned video clips...")
            bg_videos = self.media_fetcher.fetch_psychology_videos(num_clips=num_clips)
        else:
            # Fetch based on query
            bg_videos = []
            for i in range(num_clips):
                video = self.media_fetcher.fetch_background_video(background_query)
                if video and video not in bg_videos:
                    bg_videos.append(video)

        # Ensure we have at least one video
        if not bg_videos:
            bg_videos = [self.media_fetcher.fetch_background_video(background_query)]

        print(f"   ✓ Got {len(bg_videos)} video clips for {max(0, len(bg_videos)-1)} cuts")

        # Fetch music if not provided
        if not music_path:
            # Try API first, fall back to local cache
            music_path = self.media_fetcher.fetch_music("motivational")
            if not music_path:
                # Use cinematic/motivational music by default (not beeps)
                music_path = self.media_fetcher.get_local_music("cinematic")

        # Generate voiceover if enabled
        voiceover_path = None
        if add_voiceover and self.voiceover_available:
            print("   Generating voiceover...")
            voiceover_path = self.voiceover.generate_for_video_texts(texts, style=voice_style)
            if voiceover_path:
                print(f"   ✓ Voiceover generated")

        # Create video with multiple clips
        return self._create_with_ffmpeg_multiclip(texts, bg_videos, music_path, style, output_name, voiceover_path)

    def _shorten_text(self, text: str, max_words: int = 7) -> str:
        """Ensure text is short for viral format"""
        words = text.split()
        if len(words) <= max_words:
            return text
        return " ".join(words[:max_words]) + "..."

    def _create_with_moviepy(
        self,
        texts: List[str],
        bg_video: str,
        music_path: str,
        style: str,
        output_name: str,
        voiceover_path: str = None
    ) -> Optional[str]:
        """Create video using MoviePy for advanced effects"""

        style_config = self.text_styles.get(style, self.text_styles["bold_white"])

        try:
            # Load background video
            bg_clip = VideoFileClip(bg_video)

            # Resize to 9:16 (TikTok format)
            bg_clip = self._resize_to_vertical(bg_clip)

            # Calculate timing
            duration_per_text = 2.5  # seconds
            total_duration = len(texts) * duration_per_text

            # Loop background if needed
            if bg_clip.duration < total_duration:
                loops_needed = int(total_duration / bg_clip.duration) + 1
                bg_clip = bg_clip.loop(n=loops_needed)

            bg_clip = bg_clip.subclip(0, total_duration)

            # Add slight zoom for engagement
            bg_clip = bg_clip.resize(lambda t: 1 + 0.02 * t)
            bg_clip = bg_clip.set_position("center")

            # Darken background for text visibility
            darkened = bg_clip.fl_image(lambda frame: (frame * 0.6).astype('uint8'))

            # Create text clips
            text_clips = []
            for i, text in enumerate(texts):
                start_time = i * duration_per_text

                # Create text clip
                txt = TextClip(
                    text,
                    fontsize=style_config["fontsize"],
                    color=style_config["color"],
                    font="Arial-Bold",
                    stroke_color=style_config.get("stroke_color", "black"),
                    stroke_width=style_config.get("stroke_width", 3),
                    size=(self.width - 100, None),
                    method="caption",
                    align="center"
                )

                # Position in upper third
                txt = txt.set_position(("center", self.height * self.text_y_position))
                txt = txt.set_start(start_time)
                txt = txt.set_duration(duration_per_text)

                # Add fade in/out
                txt = txt.crossfadein(0.3).crossfadeout(0.3)

                text_clips.append(txt)

            # Composite all clips
            final = CompositeVideoClip(
                [darkened] + text_clips,
                size=(self.width, self.height)
            )

            # Add music
            if music_path and os.path.exists(music_path):
                audio = AudioFileClip(music_path)
                if audio.duration > total_duration:
                    audio = audio.subclip(0, total_duration)
                # Fade music
                audio = audio.audio_fadeout(2)
                final = final.set_audio(audio)

            # Export
            if not output_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_name = f"viral_{timestamp}.mp4"

            output_path = self.output_dir / output_name

            final.write_videofile(
                str(output_path),
                fps=self.fps,
                codec="libx264",
                audio_codec="aac",
                threads=4,
                preset="medium",
                verbose=False,
                logger=None
            )

            # Cleanup
            final.close()
            bg_clip.close()

            return str(output_path)

        except Exception as e:
            print(f"MoviePy error: {e}")
            return self._create_with_ffmpeg(texts, bg_video, music_path, style, output_name, voiceover_path)

    def _resize_to_vertical(self, clip):
        """Resize video to 9:16 vertical format"""
        # Calculate scale to fill vertical frame
        scale_w = self.width / clip.w
        scale_h = self.height / clip.h
        scale = max(scale_w, scale_h)

        new_w = int(clip.w * scale)
        new_h = int(clip.h * scale)

        clip = clip.resize((new_w, new_h))

        # Center crop to 9:16
        x_center = new_w // 2
        y_center = new_h // 2

        clip = clip.crop(
            x_center=x_center,
            y_center=y_center,
            width=self.width,
            height=self.height
        )

        return clip

    def _create_with_ffmpeg(
        self,
        texts: List[str],
        bg_video: str,
        music_path: str,
        style: str,
        output_name: str,
        voiceover_path: str = None
    ) -> Optional[str]:
        """Create video using FFmpeg directly (fallback method)"""

        temp_dir = Path(tempfile.mkdtemp())

        try:
            # Create text overlay images
            duration_per_text = 2.5
            total_duration = len(texts) * duration_per_text

            # If we have a background video, extract and resize
            if bg_video:
                processed_bg = temp_dir / "bg_processed.mp4"
                subprocess.run([
                    "ffmpeg", "-y",
                    "-i", bg_video,
                    "-vf", f"scale={self.width}:{self.height}:force_original_aspect_ratio=increase,crop={self.width}:{self.height},setsar=1,eq=brightness=-0.2",
                    "-t", str(total_duration),
                    "-an",  # Remove audio from video
                    str(processed_bg)
                ], capture_output=True, check=True)
                bg_source = str(processed_bg)
            else:
                # Create black background
                bg_source = f"color=c=black:s={self.width}x{self.height}:d={total_duration}"

            # Create text overlay images
            overlay_paths = []
            for i, text in enumerate(texts):
                img_path = temp_dir / f"text_{i:03d}.png"
                self._create_text_overlay(text, str(img_path), style)
                overlay_paths.append(img_path)

            # Output path
            if not output_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_name = f"viral_{timestamp}.mp4"

            output_path = self.output_dir / output_name

            # Step 1: Create video with text overlays (no audio)
            video_no_audio = temp_dir / "video_no_audio.mp4"

            # Build FFmpeg filter for text overlays
            filter_parts = []
            inputs = f'-i "{bg_source}"' if bg_video else f'-f lavfi -i "{bg_source}"'

            for i, path in enumerate(overlay_paths):
                inputs += f' -i "{path}"'
                start_time = i * duration_per_text
                end_time = start_time + duration_per_text

                if i == 0:
                    filter_parts.append(
                        f"[0][1]overlay=(W-w)/2:(H-h)/4:enable='between(t,{start_time},{end_time})'[v{i}]"
                    )
                else:
                    filter_parts.append(
                        f"[v{i-1}][{i+1}]overlay=(W-w)/2:(H-h)/4:enable='between(t,{start_time},{end_time})'[v{i}]"
                    )

            filter_complex = ";".join(filter_parts)
            final_output = f"[v{len(overlay_paths)-1}]"

            cmd = f'ffmpeg -y {inputs} -filter_complex "{filter_complex}" -map "{final_output}" -c:v libx264 -pix_fmt yuv420p -r {self.fps} -t {total_duration} "{video_no_audio}"'
            subprocess.run(cmd, shell=True, capture_output=True, check=True)

            # Step 2: Add audio (voiceover + music mix)
            has_voiceover = voiceover_path and os.path.exists(voiceover_path)
            has_music = music_path and os.path.exists(music_path)

            if has_voiceover and has_music:
                # Mix voiceover (loud) with music (background, quieter)
                # Voice at full volume, music at 20% volume
                subprocess.run([
                    "ffmpeg", "-y",
                    "-i", str(video_no_audio),
                    "-i", voiceover_path,
                    "-stream_loop", "-1",
                    "-i", music_path,
                    "-filter_complex",
                    f"[1:a]volume=1.0[voice];[2:a]volume=0.2[music];[voice][music]amix=inputs=2:duration=first:dropout_transition=2,afade=t=out:st={total_duration-2}:d=2[aout]",
                    "-map", "0:v",
                    "-map", "[aout]",
                    "-c:v", "copy",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-t", str(total_duration),
                    "-shortest",
                    str(output_path)
                ], capture_output=True, check=True)
            elif has_voiceover:
                # Just voiceover, no music
                subprocess.run([
                    "ffmpeg", "-y",
                    "-i", str(video_no_audio),
                    "-i", voiceover_path,
                    "-c:v", "copy",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-t", str(total_duration),
                    "-af", f"afade=t=out:st={total_duration-2}:d=2",
                    "-shortest",
                    str(output_path)
                ], capture_output=True, check=True)
            elif has_music:
                # Just music, no voiceover
                subprocess.run([
                    "ffmpeg", "-y",
                    "-i", str(video_no_audio),
                    "-stream_loop", "-1",
                    "-i", music_path,
                    "-c:v", "copy",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-t", str(total_duration),
                    "-af", f"afade=t=out:st={total_duration-2}:d=2",
                    "-shortest",
                    str(output_path)
                ], capture_output=True, check=True)
            else:
                # No audio, just copy the video
                import shutil
                shutil.copy(str(video_no_audio), str(output_path))

            return str(output_path)

        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error: {e.stderr.decode() if e.stderr else e}")

            # Ultimate fallback: simple slideshow
            return self._create_simple_slideshow(texts, output_name)
        finally:
            # Cleanup temp files
            for p in temp_dir.iterdir():
                try:
                    p.unlink()
                except:
                    pass
            try:
                temp_dir.rmdir()
            except:
                pass

    def _create_with_ffmpeg_multiclip(
        self,
        texts: List[str],
        bg_videos: List[str],
        music_path: str,
        style: str,
        output_name: str,
        voiceover_path: str = None
    ) -> Optional[str]:
        """
        Create video using FFmpeg with multiple background clips (cuts).

        Distributes clips across text segments to match psychological journey:
        - Early texts (pain/hook) → first clips
        - Middle texts (discovery) → middle clips
        - Late texts (transformation/CTA) → later clips
        """

        temp_dir = Path(tempfile.mkdtemp())

        try:
            # Calculate timing
            duration_per_text = 2.5
            total_duration = len(texts) * duration_per_text

            # Filter valid video files
            valid_videos = [v for v in bg_videos if v and os.path.exists(v)]
            if not valid_videos:
                print("   No valid background videos, using solid background")
                return self._create_with_ffmpeg(texts, None, music_path, style, output_name, voiceover_path)

            # Distribute clips across texts
            # Each clip covers certain text segments
            num_clips = len(valid_videos)
            texts_per_clip = max(1, len(texts) // num_clips)

            # Assign texts to clips
            clip_assignments = []  # List of (clip_path, start_time, end_time, text_indices)
            current_text_idx = 0

            for clip_idx, clip_path in enumerate(valid_videos):
                # Determine which texts this clip covers
                if clip_idx == num_clips - 1:
                    # Last clip gets all remaining texts
                    end_text_idx = len(texts)
                else:
                    end_text_idx = min(current_text_idx + texts_per_clip, len(texts))

                start_time = current_text_idx * duration_per_text
                end_time = end_text_idx * duration_per_text
                clip_duration = end_time - start_time

                if clip_duration > 0:
                    clip_assignments.append({
                        "path": clip_path,
                        "start_time": start_time,
                        "end_time": end_time,
                        "duration": clip_duration,
                        "text_indices": list(range(current_text_idx, end_text_idx))
                    })

                current_text_idx = end_text_idx

            print(f"   Clip distribution: {len(clip_assignments)} segments")
            for i, ca in enumerate(clip_assignments):
                print(f"      Clip {i+1}: {ca['duration']:.1f}s, texts {ca['text_indices']}")

            # Step 1: Process and concatenate background clips
            processed_clips = []
            for i, ca in enumerate(clip_assignments):
                processed_path = temp_dir / f"clip_{i:03d}.mp4"

                # Process: resize, crop to vertical, darken, set duration
                subprocess.run([
                    "ffmpeg", "-y",
                    "-i", ca["path"],
                    "-vf", f"scale={self.width}:{self.height}:force_original_aspect_ratio=increase,crop={self.width}:{self.height},setsar=1,eq=brightness=-0.2",
                    "-t", str(ca["duration"]),
                    "-an",  # Remove audio
                    "-c:v", "libx264",
                    "-pix_fmt", "yuv420p",
                    str(processed_path)
                ], capture_output=True, check=True)

                processed_clips.append(processed_path)

            # Step 2: Concatenate clips
            concat_list = temp_dir / "concat.txt"
            with open(concat_list, "w") as f:
                for clip_path in processed_clips:
                    f.write(f"file '{clip_path}'\n")

            concatenated_bg = temp_dir / "bg_concat.mp4"
            subprocess.run([
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_list),
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                str(concatenated_bg)
            ], capture_output=True, check=True)

            # Step 3: Create text overlay images
            overlay_paths = []
            for i, text in enumerate(texts):
                img_path = temp_dir / f"text_{i:03d}.png"
                self._create_text_overlay(text, str(img_path), style)
                overlay_paths.append(img_path)

            # Step 4: Apply text overlays to concatenated video
            video_no_audio = temp_dir / "video_no_audio.mp4"

            # Build FFmpeg filter for text overlays
            inputs = f'-i "{concatenated_bg}"'

            filter_parts = []
            for i, path in enumerate(overlay_paths):
                inputs += f' -i "{path}"'
                start_time = i * duration_per_text
                end_time = start_time + duration_per_text

                if i == 0:
                    filter_parts.append(
                        f"[0][1]overlay=(W-w)/2:(H-h)/4:enable='between(t,{start_time},{end_time})'[v{i}]"
                    )
                else:
                    filter_parts.append(
                        f"[v{i-1}][{i+1}]overlay=(W-w)/2:(H-h)/4:enable='between(t,{start_time},{end_time})'[v{i}]"
                    )

            filter_complex = ";".join(filter_parts)
            final_output = f"[v{len(overlay_paths)-1}]"

            cmd = f'ffmpeg -y {inputs} -filter_complex "{filter_complex}" -map "{final_output}" -c:v libx264 -pix_fmt yuv420p -r {self.fps} -t {total_duration} "{video_no_audio}"'
            subprocess.run(cmd, shell=True, capture_output=True, check=True)

            # Step 5: Add audio (voiceover + music mix)
            if not output_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_name = f"viral_{timestamp}.mp4"

            output_path = self.output_dir / output_name

            has_voiceover = voiceover_path and os.path.exists(voiceover_path)
            has_music = music_path and os.path.exists(music_path)

            if has_voiceover and has_music:
                # Mix voiceover (loud) with music (background, quieter)
                subprocess.run([
                    "ffmpeg", "-y",
                    "-i", str(video_no_audio),
                    "-i", voiceover_path,
                    "-stream_loop", "-1",
                    "-i", music_path,
                    "-filter_complex",
                    f"[1:a]volume=1.0[voice];[2:a]volume=0.2[music];[voice][music]amix=inputs=2:duration=first:dropout_transition=2,afade=t=out:st={total_duration-2}:d=2[aout]",
                    "-map", "0:v",
                    "-map", "[aout]",
                    "-c:v", "copy",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-t", str(total_duration),
                    "-shortest",
                    str(output_path)
                ], capture_output=True, check=True)
            elif has_voiceover:
                subprocess.run([
                    "ffmpeg", "-y",
                    "-i", str(video_no_audio),
                    "-i", voiceover_path,
                    "-c:v", "copy",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-t", str(total_duration),
                    "-af", f"afade=t=out:st={total_duration-2}:d=2",
                    "-shortest",
                    str(output_path)
                ], capture_output=True, check=True)
            elif has_music:
                subprocess.run([
                    "ffmpeg", "-y",
                    "-i", str(video_no_audio),
                    "-stream_loop", "-1",
                    "-i", music_path,
                    "-c:v", "copy",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-t", str(total_duration),
                    "-af", f"afade=t=out:st={total_duration-2}:d=2",
                    "-shortest",
                    str(output_path)
                ], capture_output=True, check=True)
            else:
                import shutil
                shutil.copy(str(video_no_audio), str(output_path))

            print(f"   ✓ Video created with {len(valid_videos)} clips ({len(valid_videos)-1} cuts)")
            return str(output_path)

        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error: {e.stderr.decode() if e.stderr else e}")
            # Fallback to single-clip method
            if bg_videos:
                return self._create_with_ffmpeg(texts, bg_videos[0], music_path, style, output_name, voiceover_path)
            return self._create_simple_slideshow(texts, output_name)
        finally:
            # Cleanup temp files
            for p in temp_dir.iterdir():
                try:
                    p.unlink()
                except:
                    pass
            try:
                temp_dir.rmdir()
            except:
                pass

    def _create_text_overlay(self, text: str, output_path: str, style: str = "bold_white"):
        """Create a transparent PNG with text overlay"""

        style_config = self.text_styles.get(style, self.text_styles["bold_white"])

        # Create transparent image
        img = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Load font
        font_size = style_config["fontsize"]
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()

        # Wrap text (3-7 words per line)
        wrapped = self._wrap_text(text, max_words=4)

        # Calculate text position (upper third)
        bbox = draw.multiline_textbbox((0, 0), wrapped, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (self.width - text_width) // 2
        y = int(self.height * self.text_y_position)

        # Draw stroke/outline
        stroke_width = style_config.get("stroke_width", 3)
        stroke_color = style_config.get("stroke_color", "black")

        if stroke_color != "none" and stroke_width > 0:
            for dx in range(-stroke_width, stroke_width + 1):
                for dy in range(-stroke_width, stroke_width + 1):
                    if dx*dx + dy*dy <= stroke_width*stroke_width:
                        draw.multiline_text(
                            (x + dx, y + dy),
                            wrapped,
                            font=font,
                            fill=stroke_color,
                            align="center"
                        )

        # Draw main text
        draw.multiline_text(
            (x, y),
            wrapped,
            font=font,
            fill=style_config["color"],
            align="center"
        )

        img.save(output_path)

    def _wrap_text(self, text: str, max_words: int = 4) -> str:
        """Wrap text into short lines"""
        words = text.split()
        lines = []

        for i in range(0, len(words), max_words):
            lines.append(" ".join(words[i:i + max_words]))

        return "\n".join(lines)

    def _create_simple_slideshow(self, texts: List[str], output_name: str) -> Optional[str]:
        """Create a simple slideshow as fallback"""

        temp_dir = Path(tempfile.mkdtemp())

        try:
            duration_per_slide = 2.5

            # Create slide images
            image_paths = []
            for i, text in enumerate(texts):
                img_path = temp_dir / f"slide_{i:03d}.png"

                # Create dark gradient background with text
                img = Image.new("RGB", (self.width, self.height), (20, 20, 30))
                draw = ImageDraw.Draw(img)

                font_size = 80
                try:
                    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
                except:
                    font = ImageFont.load_default()

                wrapped = self._wrap_text(text, 4)
                bbox = draw.multiline_textbbox((0, 0), wrapped, font=font)
                text_width = bbox[2] - bbox[0]

                x = (self.width - text_width) // 2
                y = int(self.height * 0.35)

                # Draw text with shadow
                draw.multiline_text((x+3, y+3), wrapped, font=font, fill=(0, 0, 0), align="center")
                draw.multiline_text((x, y), wrapped, font=font, fill="white", align="center")

                img.save(img_path)
                image_paths.append(img_path)

            # Create file list for FFmpeg
            list_path = temp_dir / "files.txt"
            with open(list_path, "w") as f:
                for img_path in image_paths:
                    f.write(f"file '{img_path}'\n")
                    f.write(f"duration {duration_per_slide}\n")
                f.write(f"file '{image_paths[-1]}'\n")

            # Output
            if not output_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_name = f"viral_{timestamp}.mp4"

            output_path = self.output_dir / output_name

            subprocess.run([
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(list_path),
                "-vf", f"scale={self.width}:{self.height}",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-r", "30",
                str(output_path)
            ], capture_output=True, check=True)

            return str(output_path)

        except Exception as e:
            print(f"Slideshow error: {e}")
            return None
        finally:
            for p in temp_dir.iterdir():
                try:
                    p.unlink()
                except:
                    pass
            try:
                temp_dir.rmdir()
            except:
                pass


class MotivationalContentGenerator:
    """
    Generates motivational content optimized for virality.

    Based on psychology research:
    - Target audience is cognitively taxed - keep messaging SIMPLE
    - Lead with transformation, not features
    - Use identity-based language
    - Validate pain without exploiting
    - Be specific (numbers, timeframes, realistic outcomes)
    """

    def __init__(self):
        # Import psychology hooks
        try:
            from src.content_engine.psychology_hooks import (
                get_viral_text_sequence,
                get_psychological_hook,
                PAIN_POINTS,
                ASPIRATIONS,
                REALISTIC_OUTCOMES,
                CTAS
            )
            self.use_psychology = True
            self.get_viral_sequence = get_viral_text_sequence
            self.get_hook = get_psychological_hook
            self.pain_points = PAIN_POINTS
            self.aspirations = ASPIRATIONS
            self.outcomes = REALISTIC_OUTCOMES
            self.ctas = CTAS
        except ImportError:
            self.use_psychology = False
            self._init_fallback()

    def _init_fallback(self):
        """Fallback if psychology module not available"""
        self.pain_points = [
            "working 60 hours and still broke",
            "watching others succeed while you struggle",
            "feeling stuck in the same place",
        ]
        self.aspirations = [
            "wake up without an alarm",
            "check your bank account and smile",
            "finally breathe",
        ]
        self.outcomes = [
            "$500 extra this month",
            "15 hours back every week",
            "doubled your output",
        ]
        self.ctas = [
            "Link in bio if you're ready",
            "Save this. You'll need it.",
            "Try it free. Link in bio.",
        ]

    def generate_viral_script(self, product: str, benefit: str) -> List[str]:
        """Generate a viral video script (list of text screens)"""

        if self.use_psychology:
            # Use psychology-optimized sequence
            return self.get_viral_sequence(product, benefit)

        # Fallback generation
        patterns = [
            # Pain → Discovery → Transformation → CTA
            [
                f"Tired of {random.choice(self.pain_points)}?",
                f"I found {product}",
                f"Now I {random.choice(self.aspirations)}",
                random.choice(self.ctas),
            ],
            # Hook → Problem → Solution → Result
            [
                "This changed everything for me",
                f"I was {random.choice(self.pain_points)}",
                f"Then {product} happened",
                f"Result: {random.choice(self.outcomes)}",
                random.choice(self.ctas),
            ],
            # Identity → Challenge → Bridge
            [
                "For people who refuse to settle",
                f"{product} {benefit}",
                f"You could {random.choice(self.aspirations)}",
                random.choice(self.ctas),
            ],
        ]

        return random.choice(patterns)


def main():
    """Demo the viral video creator"""

    print("=" * 60)
    print("VIRAL VIDEO CREATOR - Multi-Clip Edition")
    print("=" * 60)

    creator = ViralVideoCreator()
    content = MotivationalContentGenerator()

    print("\n📋 Checking dependencies...")
    print(f"   FFmpeg: {'✓' if creator.check_ffmpeg() else '✗'}")
    print(f"   Pillow: {'✓' if PIL_AVAILABLE else '✗'}")
    print(f"   MoviePy: {'✓' if MOVIEPY_AVAILABLE else '✗'}")
    print(f"   Voiceover: {'✓' if creator.voiceover_available else '✗'}")

    if not creator.check_ffmpeg():
        print("\nInstall FFmpeg: brew install ffmpeg")
        return

    # Generate motivational script
    print("\n📝 Generating viral script...")
    script = content.generate_viral_script("Jasper AI", "writing 10x faster")

    for i, text in enumerate(script):
        print(f"   {i+1}. {text}")

    # Create video with multi-clip psychology-aligned backgrounds
    print("\n🎬 Creating viral video with psychology-aligned clips...")
    print("   Using pain → discovery → transformation video progression")
    video_path = creator.create_viral_video(
        texts=script,
        style="bold_white",
        add_hook=False,  # Already included in script
        add_voiceover=True,
        voice_style="motivational",
        min_cuts=2,  # At least 2 cuts (3 clips)
        use_psychology_videos=True
    )

    if video_path:
        print(f"\n✓ Video created: {video_path}")

        # Show video details
        try:
            result = subprocess.run(
                ["ffprobe", "-i", video_path, "-show_entries", "format=duration",
                 "-v", "quiet", "-of", "csv=p=0"],
                capture_output=True, text=True
            )
            if result.stdout.strip():
                print(f"   Duration: {float(result.stdout.strip()):.1f}s")
        except:
            pass
    else:
        print("\n✗ Video creation failed")


if __name__ == "__main__":
    main()
