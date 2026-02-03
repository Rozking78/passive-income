"""
Dynamic Voiceover Generator
============================
Creates natural, energetic voiceovers using Edge TTS (Microsoft).

Voices optimized for motivational/sales content:
- Strong, confident male voices
- Energetic, inspiring female voices
- Adjustable speed and pitch for impact
"""

import asyncio
import tempfile
import random
from pathlib import Path
from typing import Optional, List

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False


# Dynamic voice options for motivational content
VOICE_PROFILES = {
    # Male voices - strong, confident
    "guy_energetic": {
        "voice": "en-US-GuyNeural",
        "rate": "+15%",
        "pitch": "+5Hz",
        "style": "energetic"
    },
    "christopher_confident": {
        "voice": "en-US-ChristopherNeural",
        "rate": "+10%",
        "pitch": "+0Hz",
        "style": "confident"
    },
    "tony_intense": {
        "voice": "en-US-TonyNeural",
        "rate": "+20%",
        "pitch": "+10Hz",
        "style": "intense"
    },

    # Female voices - inspiring, dynamic
    "jenny_inspiring": {
        "voice": "en-US-JennyNeural",
        "rate": "+10%",
        "pitch": "+5Hz",
        "style": "inspiring"
    },
    "aria_powerful": {
        "voice": "en-US-AriaNeural",
        "rate": "+15%",
        "pitch": "+0Hz",
        "style": "powerful"
    },
    "sara_motivational": {
        "voice": "en-US-SaraNeural",
        "rate": "+12%",
        "pitch": "+3Hz",
        "style": "motivational"
    },
}

# Default profiles for different content types
CONTENT_VOICE_MAP = {
    "motivational": ["guy_energetic", "aria_powerful", "tony_intense"],
    "tutorial": ["christopher_confident", "jenny_inspiring"],
    "story": ["sara_motivational", "guy_energetic"],
    "hype": ["tony_intense", "aria_powerful"],
    "calm": ["christopher_confident", "jenny_inspiring"],
}


class VoiceoverGenerator:
    """Generates natural voiceovers for video content"""

    def __init__(self, cache_dir: str = "content/voiceovers"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.available = EDGE_TTS_AVAILABLE
        self.fallback_available = GTTS_AVAILABLE

    async def _generate_edge_tts(
        self,
        text: str,
        output_path: str,
        voice: str = "en-US-GuyNeural",
        rate: str = "+10%",
        pitch: str = "+0Hz"
    ) -> bool:
        """Generate voiceover using Edge TTS"""
        try:
            communicate = edge_tts.Communicate(
                text,
                voice,
                rate=rate,
                pitch=pitch
            )
            await communicate.save(output_path)
            return True
        except Exception as e:
            print(f"Edge TTS error: {e}")
            return False

    def generate_voiceover(
        self,
        text: str,
        style: str = "motivational",
        voice_profile: str = None,
        output_path: str = None
    ) -> Optional[str]:
        """
        Generate a voiceover for the given text.

        Args:
            text: The text to speak
            style: Content style (motivational, tutorial, story, hype, calm)
            voice_profile: Specific voice profile to use (overrides style)
            output_path: Where to save the audio (optional)

        Returns:
            Path to generated audio file
        """
        if not text.strip():
            return None

        # Generate output path if not provided
        if not output_path:
            output_path = str(self.cache_dir / f"vo_{hash(text) % 100000}.mp3")

        # Select voice profile
        if voice_profile and voice_profile in VOICE_PROFILES:
            profile = VOICE_PROFILES[voice_profile]
        else:
            # Pick random voice for the style
            style_voices = CONTENT_VOICE_MAP.get(style, ["guy_energetic"])
            profile_name = random.choice(style_voices)
            profile = VOICE_PROFILES[profile_name]

        # Try Edge TTS first (best quality)
        if self.available:
            success = asyncio.run(self._generate_edge_tts(
                text,
                output_path,
                voice=profile["voice"],
                rate=profile["rate"],
                pitch=profile["pitch"]
            ))
            if success:
                return output_path

        # Fallback to gTTS
        if self.fallback_available:
            try:
                tts = gTTS(text=text, lang='en', slow=False)
                tts.save(output_path)
                return output_path
            except Exception as e:
                print(f"gTTS fallback error: {e}")

        return None

    def generate_multi_segment_voiceover(
        self,
        texts: List[str],
        style: str = "motivational",
        pause_duration: float = 0.3
    ) -> Optional[str]:
        """
        Generate voiceover for multiple text segments.

        Each segment is spoken with a pause between them.
        Returns a single combined audio file.
        """
        if not texts:
            return None

        # For now, combine texts with pauses marked by ellipsis
        # This creates natural pauses in speech
        combined_text = "... ".join(texts)

        return self.generate_voiceover(combined_text, style)

    def generate_for_video_texts(
        self,
        texts: List[str],
        style: str = "motivational"
    ) -> Optional[str]:
        """
        Generate voiceover optimized for video overlay texts.

        Adds emphasis and pacing appropriate for short-form content.
        """
        if not texts:
            return None

        # Clean up texts for speaking
        spoken_texts = []
        for text in texts:
            # Remove hashtags and emojis for cleaner speech
            clean = text
            clean = ' '.join(word for word in clean.split() if not word.startswith('#'))
            clean = clean.replace('...', '')
            clean = clean.strip()
            if clean:
                spoken_texts.append(clean)

        if not spoken_texts:
            return None

        # Join with dramatic pauses
        script = " ... ".join(spoken_texts)

        return self.generate_voiceover(script, style)


def get_available_voices() -> List[str]:
    """Get list of available voice profiles"""
    return list(VOICE_PROFILES.keys())


def test_voiceover():
    """Test the voiceover generator"""
    generator = VoiceoverGenerator()

    print("=" * 60)
    print("VOICEOVER GENERATOR TEST")
    print("=" * 60)
    print(f"Edge TTS available: {EDGE_TTS_AVAILABLE}")
    print(f"gTTS fallback available: {GTTS_AVAILABLE}")

    if not generator.available and not generator.fallback_available:
        print("No TTS engines available!")
        return

    test_texts = [
        "This changed everything for me",
        "I was working 60 hours and still broke",
        "Then I found Jasper AI",
        "Now I check my bank account and smile",
        "Link in bio if you're ready"
    ]

    print("\nGenerating test voiceover...")
    output = generator.generate_for_video_texts(test_texts, style="motivational")

    if output:
        print(f"Generated: {output}")
        # Get duration
        import subprocess
        result = subprocess.run(
            ["ffprobe", "-i", output, "-show_entries", "format=duration",
             "-v", "quiet", "-of", "csv=p=0"],
            capture_output=True, text=True
        )
        if result.stdout.strip():
            print(f"Duration: {float(result.stdout.strip()):.1f}s")
    else:
        print("Generation failed!")


if __name__ == "__main__":
    test_voiceover()
