"""
Dynamic Voiceover Generator
============================
Creates natural, human-like voiceovers using Edge TTS with SSML.

Key techniques for natural speech:
- SSML for precise pause/emphasis control
- Varied pacing based on emotional content
- Emphasis on key words (numbers, products, emotions)
- Natural breathing rhythm between phrases
- Prosody variations for storytelling flow
"""

import asyncio
import re
import random
from pathlib import Path
from typing import Optional, List, Tuple

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


# Voice profiles with style-appropriate settings
VOICE_PROFILES = {
    # Male voices - natural, conversational
    "andrew_storyteller": {
        "voice": "en-US-AndrewNeural",
        "rate": "-5%",  # Slightly slower for storytelling
        "pitch": "-2Hz",
        "style": "narrative",
    },
    "brian_confident": {
        "voice": "en-US-BrianNeural",
        "rate": "+0%",
        "pitch": "+0Hz",
        "style": "confident",
    },
    "christopher_calm": {
        "voice": "en-US-ChristopherNeural",
        "rate": "-8%",  # Calmer, slower
        "pitch": "-3Hz",
        "style": "calm",
    },
    "guy_friendly": {
        "voice": "en-US-GuyNeural",
        "rate": "+0%",
        "pitch": "+0Hz",
        "style": "friendly",
    },

    # Female voices - warm, authentic
    "ava_warm": {
        "voice": "en-US-AvaNeural",
        "rate": "-3%",
        "pitch": "+0Hz",
        "style": "warm",
    },
    "emma_natural": {
        "voice": "en-US-EmmaNeural",
        "rate": "+0%",
        "pitch": "+0Hz",
        "style": "natural",
    },
    "aria_energetic": {
        "voice": "en-US-AriaNeural",
        "rate": "+3%",  # Slightly faster, more energy
        "pitch": "+2Hz",
        "style": "energetic",
    },
    "jenny_conversational": {
        "voice": "en-US-JennyNeural",
        "rate": "-2%",
        "pitch": "+0Hz",
        "style": "conversational",
    },
}

# Content style to voice mapping
CONTENT_VOICE_MAP = {
    "motivational": ["andrew_storyteller", "aria_energetic", "brian_confident"],
    "tutorial": ["emma_natural", "christopher_calm"],
    "story": ["ava_warm", "andrew_storyteller", "jenny_conversational"],
    "hype": ["aria_energetic", "brian_confident"],
    "calm": ["ava_warm", "christopher_calm", "jenny_conversational"],
}

# Words that should be emphasized
EMPHASIS_WORDS = {
    # Money/numbers - strong emphasis
    "strong": [
        r"\$\d+", r"\d+k", r"\d+%", r"\d+ hours", r"\d+ weeks", r"\d+ days",
        "free", "zero", "nothing", "everything", "doubled", "tripled",
    ],
    # Emotional words - moderate emphasis
    "moderate": [
        "finally", "actually", "honestly", "literally", "seriously",
        "changed", "transformed", "discovered", "realized", "secret",
        "tired", "exhausted", "struggling", "broke", "stuck",
        "freedom", "success", "wealthy", "rich", "thriving",
    ],
    # Transition words - slight emphasis
    "slight": [
        "but", "then", "now", "so", "and", "because",
    ],
}

# Phrases that need pauses before/after
PAUSE_PHRASES = {
    "before": [
        "here's the thing", "the truth is", "honestly", "look",
        "listen", "trust me", "i'm telling you", "real talk",
    ],
    "after": [
        "changed everything", "that's when", "and then", "but then",
        "here's why", "here's how", "think about it",
    ],
}


class VoiceoverGenerator:
    """Generates natural, human-like voiceovers"""

    def __init__(self, cache_dir: str = "content/voiceovers"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.available = EDGE_TTS_AVAILABLE
        self.fallback_available = GTTS_AVAILABLE

    async def _generate_edge_tts(
        self,
        text: str,
        output_path: str,
        voice: str = "en-US-AndrewNeural",
        rate: str = "+0%",
        pitch: str = "+0Hz"
    ) -> bool:
        """Generate voiceover using Edge TTS with natural speech"""
        try:
            # Add natural pacing to text (simple approach - no SSML)
            natural_text = self._add_natural_pacing(text)

            communicate = edge_tts.Communicate(
                natural_text,
                voice,
                rate=rate,
                pitch=pitch
            )
            await communicate.save(output_path)
            return True
        except Exception as e:
            print(f"Edge TTS error: {e}")
            return False

    def _add_natural_pacing(self, text: str) -> str:
        """Add natural pacing through punctuation"""
        result = text

        # Add commas for breathing room after certain transition words
        breath_words = ["look", "honestly", "and", "but", "so", "now", "then"]
        for word in breath_words:
            # Add comma after word at start of phrase if not already there
            result = re.sub(
                rf'\b({word})\s+(?!,)',
                rf'\1, ',
                result,
                flags=re.IGNORECASE
            )

        # Clean up spacing
        result = re.sub(r'\s+', ' ', result)
        result = re.sub(r'\s*,\s*,', ',', result)
        result = re.sub(r',\s*\.', '.', result)

        return result.strip()

    def _create_natural_ssml_unused(self, text: str, rate: str, pitch: str) -> str:
        """
        Create SSML markup for natural-sounding speech.

        Adds:
        - Brief pauses for breathing/emphasis
        - Emphasis on key words
        - Natural sentence rhythm
        """
        # Start with the base text
        processed = text

        # Add brief pauses around key phrases (subtle, not long)
        for phrase in PAUSE_PHRASES["before"]:
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            processed = pattern.sub(f'<break time="150ms"/>{phrase}', processed)

        for phrase in PAUSE_PHRASES["after"]:
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            processed = pattern.sub(f'{phrase}<break time="100ms"/>', processed)

        # Add emphasis to key money/number words only (most impactful)
        for word in EMPHASIS_WORDS["strong"]:
            if word.startswith(r"\\") or word.startswith("$"):
                # Regex pattern for numbers
                try:
                    pattern = re.compile(f'({word})', re.IGNORECASE)
                    processed = pattern.sub(r'<emphasis level="strong">\1</emphasis>', processed)
                except:
                    pass
            else:
                pattern = re.compile(f'\\b({re.escape(word)})\\b', re.IGNORECASE)
                processed = pattern.sub(r'<emphasis level="moderate">\1</emphasis>', processed)

        # Natural sentence breaks - short pauses
        processed = re.sub(r'\. ', '.<break time="200ms"/> ', processed)
        processed = re.sub(r'\! ', '!<break time="150ms"/> ', processed)
        processed = re.sub(r'\? ', '?<break time="180ms"/> ', processed)

        # Very brief pause after commas
        processed = re.sub(r', ', ',<break time="80ms"/> ', processed)

        # Wrap in SSML speak tags with prosody
        ssml = f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
            <prosody rate="{rate}" pitch="{pitch}">
                {processed}
            </prosody>
        </speak>'''

        return ssml

    def _transform_for_storytelling(self, texts: List[str]) -> str:
        """
        Transform bullet points into natural flowing speech.

        Keeps original phrasing intact - just cleans and joins naturally.
        The psychology hooks are already written well, don't over-process them.
        """
        if not texts:
            return ""

        segments = []

        for i, text in enumerate(texts):
            # Clean the text
            clean = self._clean_text(text)
            if not clean:
                continue

            # Ensure it ends with punctuation
            if not clean[-1] in '.!?':
                clean = clean + "."

            segments.append(clean)

        # Join segments
        script = " ".join(segments)

        # Clean up spacing
        script = re.sub(r'\s+', ' ', script)
        script = re.sub(r'\.\s*\.', '.', script)

        return script.strip()

    def _clean_text(self, text: str) -> str:
        """Clean text for speech"""
        clean = text
        # Remove hashtags
        clean = ' '.join(word for word in clean.split() if not word.startswith('#'))
        # Remove multiple dots
        clean = re.sub(r'\.{2,}', '', clean)
        # Remove emojis (basic)
        clean = re.sub(r'[^\w\s\'".,!?$%\-]', '', clean)
        return clean.strip()

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
            style_voices = CONTENT_VOICE_MAP.get(style, ["andrew_storyteller"])
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

    def generate_for_video_texts(
        self,
        texts: List[str],
        style: str = "motivational"
    ) -> Optional[str]:
        """
        Generate voiceover optimized for video overlay texts.

        Transforms bullet points into natural storytelling flow with:
        - Emotional arc (hook → pain → discovery → transformation → CTA)
        - Natural connectors between ideas
        - Emphasis on key words
        - Breathing pauses
        """
        if not texts:
            return None

        # Transform into natural storytelling
        script = self._transform_for_storytelling(texts)

        if not script:
            return None

        return self.generate_voiceover(script, style)

    def generate_multi_segment_voiceover(
        self,
        texts: List[str],
        style: str = "motivational",
        pause_duration: float = 0.5
    ) -> Optional[str]:
        """
        Generate voiceover for multiple text segments with pauses.
        """
        if not texts:
            return None

        # Use storytelling transformation
        script = self._transform_for_storytelling(texts)
        return self.generate_voiceover(script, style)


def get_available_voices() -> List[str]:
    """Get list of available voice profiles"""
    return list(VOICE_PROFILES.keys())


def test_voiceover():
    """Test the voiceover generator"""
    generator = VoiceoverGenerator()

    print("=" * 60)
    print("NATURAL VOICEOVER TEST")
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
        "Now I make $500 extra every week",
        "Link in bio if you're ready"
    ]

    print("\nOriginal texts:")
    for i, t in enumerate(test_texts):
        print(f"  {i+1}. {t}")

    # Show transformation
    script = generator._transform_for_storytelling(test_texts)
    print(f"\nTransformed script:\n  \"{script}\"")

    print("\nGenerating voiceover...")
    output = generator.generate_for_video_texts(test_texts, style="motivational")

    if output:
        print(f"Generated: {output}")
        import subprocess
        result = subprocess.run(
            ["ffprobe", "-i", output, "-show_entries", "format=duration",
             "-v", "quiet", "-of", "csv=p=0"],
            capture_output=True, text=True
        )
        if result.stdout.strip():
            print(f"Duration: {float(result.stdout.strip()):.1f}s")

        print("\nPlaying audio...")
        subprocess.run(["afplay", output])
    else:
        print("Generation failed!")


if __name__ == "__main__":
    test_voiceover()
