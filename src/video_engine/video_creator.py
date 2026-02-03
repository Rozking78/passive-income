"""
Automated Video Creator
=======================
Creates TikTok/Reels style videos automatically.

Features:
- Text-to-speech voiceover (free APIs)
- Animated text overlays
- Background music
- Auto-captions
- Multiple visual styles

Requirements:
  pip install moviepy gTTS Pillow requests
"""

import os
import json
import random
import tempfile
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Check for required packages
try:
    from moviepy.editor import (
        VideoFileClip, AudioFileClip, ImageClip, TextClip,
        CompositeVideoClip, CompositeAudioClip, concatenate_videoclips,
        ColorClip
    )
    from moviepy.video.fx.all import fadein, fadeout
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    print("MoviePy not installed. Run: pip install moviepy")

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    print("gTTS not installed. Run: pip install gTTS")

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Pillow not installed. Run: pip install Pillow")


class VideoCreator:
    """Creates short-form videos automatically"""

    def __init__(self, output_dir: str = "content/videos"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Video settings (TikTok/Reels format)
        self.width = 1080
        self.height = 1920
        self.fps = 30

        # Visual styles
        self.styles = {
            "dark": {
                "bg_color": (15, 15, 15),
                "text_color": "white",
                "accent_color": "#00ff88",
                "font": "Arial-Bold",
            },
            "light": {
                "bg_color": (250, 250, 250),
                "text_color": "black",
                "accent_color": "#6366f1",
                "font": "Arial-Bold",
            },
            "gradient": {
                "bg_color": (30, 30, 60),
                "text_color": "white",
                "accent_color": "#ff6b6b",
                "font": "Arial-Bold",
            },
            "neon": {
                "bg_color": (10, 10, 30),
                "text_color": "#00ffff",
                "accent_color": "#ff00ff",
                "font": "Arial-Bold",
            },
        }

        # Hook templates for text-based videos
        self.hook_animations = ["fade", "slide", "zoom", "typewriter"]

    def create_video_from_script(self, script: Dict, style: str = "dark") -> Optional[str]:
        """
        Create a video from a generated script.

        Args:
            script: Script dict with 'hook', 'script', 'caption', etc.
            style: Visual style ('dark', 'light', 'gradient', 'neon')

        Returns:
            Path to created video file
        """
        if not MOVIEPY_AVAILABLE:
            print("Error: MoviePy required. Run: pip install moviepy")
            return None

        style_config = self.styles.get(style, self.styles["dark"])

        # Parse script into scenes
        scenes = self._parse_script_to_scenes(script)

        # Generate voiceover
        audio_path = self._generate_voiceover(script)

        # Create video clips for each scene
        clips = []
        current_time = 0

        for scene in scenes:
            clip = self._create_scene_clip(
                scene,
                style_config,
                duration=scene.get("duration", 3)
            )
            clip = clip.set_start(current_time)
            clips.append(clip)
            current_time += scene.get("duration", 3)

        # Composite all clips
        video = CompositeVideoClip(clips, size=(self.width, self.height))

        # Add audio if generated
        if audio_path and os.path.exists(audio_path):
            audio = AudioFileClip(audio_path)
            # Match video duration to audio
            video = video.set_duration(audio.duration)
            video = video.set_audio(audio)

        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"video_{timestamp}.mp4"

        # Export video
        video.write_videofile(
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
        video.close()
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)

        return str(output_path)

    def _parse_script_to_scenes(self, script: Dict) -> List[Dict]:
        """Parse a script into individual scenes"""

        scenes = []

        # Extract hook
        hook = script.get("hook", "")
        if hook:
            scenes.append({
                "type": "hook",
                "text": hook,
                "duration": 3,
                "animation": "zoom"
            })

        # Parse the main script content
        full_script = script.get("script", "")

        # Split into sections based on markers
        sections = full_script.split("\n\n")

        for section in sections:
            if not section.strip():
                continue

            # Skip stage directions in brackets
            if section.strip().startswith("[") and "]" in section:
                # Extract any quoted text as the actual content
                import re
                quotes = re.findall(r'"([^"]*)"', section)
                if quotes:
                    scenes.append({
                        "type": "text",
                        "text": quotes[0],
                        "duration": max(2, len(quotes[0].split()) * 0.4),
                        "animation": random.choice(self.hook_animations)
                    })
            elif section.strip().startswith('"') and section.strip().endswith('"'):
                text = section.strip().strip('"')
                scenes.append({
                    "type": "text",
                    "text": text,
                    "duration": max(2, len(text.split()) * 0.4),
                    "animation": "fade"
                })

        # Add CTA scene
        cta = script.get("cta", "Link in bio")
        scenes.append({
            "type": "cta",
            "text": cta,
            "duration": 3,
            "animation": "fade"
        })

        return scenes

    def _create_scene_clip(self, scene: Dict, style: Dict, duration: float) -> VideoFileClip:
        """Create a video clip for a single scene"""

        # Create background
        bg = ColorClip(
            size=(self.width, self.height),
            color=style["bg_color"],
            duration=duration
        )

        # Create text overlay
        text = scene.get("text", "")
        if not text:
            return bg

        # Wrap text for display
        wrapped_text = self._wrap_text(text, max_chars=25)

        try:
            txt_clip = TextClip(
                wrapped_text,
                fontsize=70,
                color=style["text_color"],
                font=style.get("font", "Arial-Bold"),
                size=(self.width - 100, None),
                method="caption",
                align="center"
            )
        except Exception:
            # Fallback if font not found
            txt_clip = TextClip(
                wrapped_text,
                fontsize=70,
                color=style["text_color"],
                size=(self.width - 100, None),
                method="caption",
                align="center"
            )

        txt_clip = txt_clip.set_duration(duration)
        txt_clip = txt_clip.set_position("center")

        # Apply animation
        animation = scene.get("animation", "fade")
        if animation == "fade":
            txt_clip = txt_clip.crossfadein(0.5).crossfadeout(0.5)
        elif animation == "zoom":
            txt_clip = txt_clip.resize(lambda t: 1 + 0.1 * t)
            txt_clip = txt_clip.set_position("center")

        # Composite
        return CompositeVideoClip([bg, txt_clip], size=(self.width, self.height))

    def _wrap_text(self, text: str, max_chars: int = 30) -> str:
        """Wrap text for video display"""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            if current_length + len(word) + 1 <= max_chars:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word)

        if current_line:
            lines.append(" ".join(current_line))

        return "\n".join(lines)

    def _generate_voiceover(self, script: Dict) -> Optional[str]:
        """Generate text-to-speech voiceover"""

        if not GTTS_AVAILABLE:
            return None

        # Extract spoken text from script
        full_script = script.get("script", "")

        # Clean up the script - extract only spoken parts
        import re
        # Remove stage directions [in brackets]
        spoken_text = re.sub(r'\[.*?\]', '', full_script)
        # Extract quoted text
        quotes = re.findall(r'"([^"]*)"', full_script)
        if quotes:
            spoken_text = " ".join(quotes)
        else:
            # Clean up remaining text
            spoken_text = spoken_text.replace("*", "").replace("#", "")
            spoken_text = " ".join(spoken_text.split())

        if not spoken_text.strip():
            spoken_text = script.get("hook", "Check this out")

        try:
            # Generate TTS
            tts = gTTS(text=spoken_text, lang='en', slow=False)

            # Save to temp file
            temp_path = tempfile.mktemp(suffix=".mp3")
            tts.save(temp_path)

            return temp_path
        except Exception as e:
            print(f"TTS Error: {e}")
            return None

    def create_text_video(self, texts: List[str], style: str = "dark",
                          duration_per_text: float = 3.0) -> Optional[str]:
        """
        Create a simple text-based video with multiple screens.

        Args:
            texts: List of text strings to show
            style: Visual style
            duration_per_text: Seconds per text screen
        """
        if not MOVIEPY_AVAILABLE:
            print("Error: MoviePy required")
            return None

        style_config = self.styles.get(style, self.styles["dark"])
        clips = []

        for text in texts:
            scene = {
                "type": "text",
                "text": text,
                "duration": duration_per_text,
                "animation": "fade"
            }
            clip = self._create_scene_clip(scene, style_config, duration_per_text)
            clips.append(clip)

        # Concatenate clips
        video = concatenate_videoclips(clips, method="compose")

        # Export
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"text_video_{timestamp}.mp4"

        video.write_videofile(
            str(output_path),
            fps=self.fps,
            codec="libx264",
            threads=4,
            preset="fast",
            verbose=False,
            logger=None
        )

        video.close()
        return str(output_path)


class SimpleVideoCreator:
    """
    Simplified video creator that works without MoviePy.
    Creates videos using FFmpeg directly.
    """

    def __init__(self, output_dir: str = "content/videos"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.width = 1080
        self.height = 1920

    def check_ffmpeg(self) -> bool:
        """Check if FFmpeg is available"""
        import subprocess
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def create_slideshow_video(self, texts: List[str], output_name: str = None,
                               duration_per_slide: float = 3.0,
                               bg_color: str = "black",
                               text_color: str = "white") -> Optional[str]:
        """
        Create a simple slideshow video using FFmpeg.

        Args:
            texts: List of text to show on each slide
            output_name: Output filename
            duration_per_slide: Seconds per slide
            bg_color: Background color
            text_color: Text color
        """
        if not self.check_ffmpeg():
            print("Error: FFmpeg not found. Install it first.")
            return None

        if not PIL_AVAILABLE:
            print("Error: Pillow required. Run: pip install Pillow")
            return None

        import subprocess

        # Create temporary images for each slide
        temp_dir = Path(tempfile.mkdtemp())
        image_paths = []

        for i, text in enumerate(texts):
            img_path = temp_dir / f"slide_{i:03d}.png"
            self._create_text_image(text, str(img_path), bg_color, text_color)
            image_paths.append(img_path)

        # Create file list for FFmpeg
        list_path = temp_dir / "files.txt"
        with open(list_path, "w") as f:
            for img_path in image_paths:
                f.write(f"file '{img_path}'\n")
                f.write(f"duration {duration_per_slide}\n")
            # Repeat last image to fix FFmpeg concat issue
            f.write(f"file '{image_paths[-1]}'\n")

        # Generate output path
        if not output_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"slideshow_{timestamp}.mp4"

        output_path = self.output_dir / output_name

        # Run FFmpeg
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(list_path),
            "-vf", f"scale={self.width}:{self.height}:force_original_aspect_ratio=decrease,pad={self.width}:{self.height}:(ow-iw)/2:(oh-ih)/2",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-r", "30",
            str(output_path)
        ]

        try:
            subprocess.run(cmd, capture_output=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error: {e.stderr.decode()}")
            return None
        finally:
            # Cleanup temp files
            for p in temp_dir.iterdir():
                p.unlink()
            temp_dir.rmdir()

        return str(output_path)

    def _create_text_image(self, text: str, output_path: str,
                           bg_color: str = "black",
                           text_color: str = "white"):
        """Create an image with text"""

        # Create image
        img = Image.new("RGB", (self.width, self.height), bg_color)
        draw = ImageDraw.Draw(img)

        # Try to load a font
        font_size = 80
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()

        # Wrap text
        wrapped = self._wrap_text(text, 20)

        # Calculate text position (center)
        bbox = draw.multiline_textbbox((0, 0), wrapped, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (self.width - text_width) // 2
        y = (self.height - text_height) // 2

        # Draw text
        draw.multiline_text((x, y), wrapped, font=font, fill=text_color, align="center")

        # Save
        img.save(output_path)

    def _wrap_text(self, text: str, max_chars: int = 20) -> str:
        """Wrap text for display"""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            if current_length + len(word) + 1 <= max_chars:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word)

        if current_line:
            lines.append(" ".join(current_line))

        return "\n".join(lines)


def main():
    """Demo the video creator"""

    print("=" * 60)
    print("VIDEO CREATOR - Automated Video Generation")
    print("=" * 60)

    # Check dependencies
    print("\nChecking dependencies...")
    print(f"  MoviePy: {'✓' if MOVIEPY_AVAILABLE else '✗ Run: pip install moviepy'}")
    print(f"  gTTS: {'✓' if GTTS_AVAILABLE else '✗ Run: pip install gTTS'}")
    print(f"  Pillow: {'✓' if PIL_AVAILABLE else '✗ Run: pip install Pillow'}")

    # Try simple video creator
    simple = SimpleVideoCreator()
    print(f"  FFmpeg: {'✓' if simple.check_ffmpeg() else '✗ Install FFmpeg'}")

    if simple.check_ffmpeg() and PIL_AVAILABLE:
        print("\n📹 Creating sample video...")
        texts = [
            "This AI tool is\nbreaking the internet",
            "It writes content\n10x faster",
            "I saved 15 hours\nlast week",
            "Link in bio\nto try it free"
        ]

        video_path = simple.create_slideshow_video(texts)
        if video_path:
            print(f"✓ Video created: {video_path}")
        else:
            print("✗ Video creation failed")
    else:
        print("\nInstall dependencies to create videos:")
        print("  pip install moviepy gTTS Pillow")
        print("  brew install ffmpeg  (macOS)")


if __name__ == "__main__":
    main()
