"""
TikTok Auto-Uploader
====================
Automates TikTok video uploads using browser automation.

Requirements:
    pip install selenium webdriver-manager

Setup:
    1. Run once manually to login and save cookies
    2. Then it posts automatically

Usage:
    uploader = TikTokUploader()
    uploader.login()  # First time only - saves session
    uploader.upload_video("video.mp4", "Caption here", ["hashtag1", "hashtag2"])
"""

import os
import json
import time
import pickle
from pathlib import Path
from typing import List, Optional
from datetime import datetime

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False


class TikTokUploader:
    """Automates TikTok video uploads"""

    def __init__(self, cookies_path: str = "data/tiktok_cookies.pkl"):
        self.cookies_path = Path(cookies_path)
        self.cookies_path.parent.mkdir(parents=True, exist_ok=True)

        self.driver = None
        self.logged_in = False
        self.upload_url = "https://www.tiktok.com/upload"

        if not SELENIUM_AVAILABLE:
            print("⚠️  Selenium not installed. Run: pip install selenium")
        if not WEBDRIVER_MANAGER_AVAILABLE:
            print("⚠️  webdriver-manager not installed. Run: pip install webdriver-manager")

    def _init_driver(self, headless: bool = False):
        """Initialize Chrome driver"""
        if not SELENIUM_AVAILABLE or not WEBDRIVER_MANAGER_AVAILABLE:
            raise RuntimeError("Install dependencies: pip install selenium webdriver-manager")

        options = Options()

        if headless:
            options.add_argument("--headless=new")

        # Avoid detection
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        # Use user data directory to persist login
        user_data_dir = Path("data/chrome_profile")
        user_data_dir.mkdir(parents=True, exist_ok=True)
        options.add_argument(f"--user-data-dir={user_data_dir.absolute()}")

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

        # Mask webdriver detection
        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

    def login(self, manual: bool = True):
        """
        Login to TikTok.

        Args:
            manual: If True, opens browser for manual login and saves session
        """
        print("🔐 TikTok Login")
        print("=" * 40)

        self._init_driver(headless=False)

        # Load existing cookies if available
        if self.cookies_path.exists():
            print("   Found saved session, attempting to restore...")
            self.driver.get("https://www.tiktok.com")
            time.sleep(2)

            try:
                with open(self.cookies_path, "rb") as f:
                    cookies = pickle.load(f)
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except:
                        pass

                self.driver.refresh()
                time.sleep(3)

                # Check if logged in
                if self._check_logged_in():
                    print("   ✓ Session restored successfully!")
                    self.logged_in = True
                    return True
            except Exception as e:
                print(f"   Session restore failed: {e}")

        if manual:
            print("\n   Opening TikTok login page...")
            print("   Please login manually in the browser window.")
            print("   Press Enter here when done...")

            self.driver.get("https://www.tiktok.com/login")
            input()

            # Save cookies
            cookies = self.driver.get_cookies()
            with open(self.cookies_path, "wb") as f:
                pickle.dump(cookies, f)

            print("   ✓ Session saved!")
            self.logged_in = True
            return True

        return False

    def _check_logged_in(self) -> bool:
        """Check if currently logged in"""
        try:
            self.driver.get("https://www.tiktok.com/upload")
            time.sleep(3)

            # If redirected to login, not logged in
            if "login" in self.driver.current_url.lower():
                return False

            # Look for upload button
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
                )
                return True
            except:
                return False
        except:
            return False

    def upload_video(
        self,
        video_path: str,
        caption: str,
        hashtags: List[str] = None,
        schedule_time: datetime = None
    ) -> bool:
        """
        Upload a video to TikTok.

        Args:
            video_path: Path to the video file
            caption: Video caption/description
            hashtags: List of hashtags (without #)
            schedule_time: Optional scheduled post time

        Returns:
            True if upload successful
        """
        if not self.driver:
            self._init_driver(headless=False)

        if not self.logged_in:
            if not self.login():
                print("❌ Not logged in")
                return False

        video_path = Path(video_path).absolute()
        if not video_path.exists():
            print(f"❌ Video not found: {video_path}")
            return False

        print(f"\n📤 Uploading: {video_path.name}")

        try:
            # Navigate to upload page
            self.driver.get(self.upload_url)
            time.sleep(3)

            # Find file input and upload
            file_input = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
            )
            file_input.send_keys(str(video_path))
            print("   ✓ Video uploaded")

            # Wait for video to process
            time.sleep(5)
            print("   ⏳ Processing video...")

            # Wait for upload to complete (look for the caption editor)
            WebDriverWait(self.driver, 120).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true']"))
            )
            print("   ✓ Video processed")

            # Find caption editor and add caption
            time.sleep(2)
            caption_editor = self.driver.find_element(By.CSS_SELECTOR, "div[contenteditable='true']")

            # Clear existing text
            caption_editor.clear()
            time.sleep(0.5)

            # Build full caption with hashtags
            full_caption = caption
            if hashtags:
                hashtag_text = " ".join(f"#{tag.strip('#')}" for tag in hashtags)
                full_caption = f"{caption}\n\n{hashtag_text}"

            # Type caption (character by character to avoid issues)
            caption_editor.click()
            time.sleep(0.3)

            # Use JavaScript to set content
            self.driver.execute_script(
                "arguments[0].textContent = arguments[1]",
                caption_editor,
                full_caption
            )
            print("   ✓ Caption added")

            time.sleep(2)

            # Find and click Post button
            post_button = None
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                text = button.text.lower()
                if "post" in text and "discard" not in text:
                    post_button = button
                    break

            if post_button:
                # Scroll to button
                self.driver.execute_script("arguments[0].scrollIntoView(true);", post_button)
                time.sleep(1)

                post_button.click()
                print("   ✓ Post button clicked")

                # Wait for upload to complete
                time.sleep(10)

                # Check for success
                if "manage" in self.driver.current_url.lower() or self._check_upload_success():
                    print("   ✓ Video posted successfully!")
                    return True
                else:
                    print("   ⚠️  Upload may have succeeded - check TikTok")
                    return True
            else:
                print("   ❌ Post button not found")
                return False

        except Exception as e:
            print(f"   ❌ Upload failed: {e}")
            return False

    def _check_upload_success(self) -> bool:
        """Check if upload was successful"""
        try:
            # Look for success message or redirect
            time.sleep(3)
            page_source = self.driver.page_source.lower()
            return "upload another" in page_source or "your video is being uploaded" in page_source
        except:
            return False

    def upload_from_queue(self, queue_dir: str = "content/tiktok_queue", limit: int = 1) -> int:
        """
        Upload videos from the queue directory.

        Args:
            queue_dir: Directory containing queued videos
            limit: Maximum number of videos to upload

        Returns:
            Number of videos uploaded
        """
        queue_path = Path(queue_dir)
        if not queue_path.exists():
            print(f"Queue directory not found: {queue_dir}")
            return 0

        # Find queued videos (those with .json metadata)
        uploaded = 0

        for json_file in sorted(queue_path.glob("*.json")):
            if uploaded >= limit:
                break

            try:
                with open(json_file) as f:
                    metadata = json.load(f)

                # Skip if already posted
                if metadata.get("status") == "posted":
                    continue

                video_path = metadata.get("video")
                if not video_path or not Path(video_path).exists():
                    continue

                caption = metadata.get("caption", "")
                hashtags = metadata.get("hashtags", [])

                print(f"\n{'='*50}")
                print(f"Uploading from queue: {Path(video_path).name}")

                if self.upload_video(video_path, caption, hashtags):
                    # Mark as posted
                    metadata["status"] = "posted"
                    metadata["posted_at"] = datetime.now().isoformat()

                    with open(json_file, "w") as f:
                        json.dump(metadata, f, indent=2)

                    uploaded += 1
                    print(f"✓ Marked as posted")

                    # Wait between uploads
                    if uploaded < limit:
                        print(f"\n⏳ Waiting 30 seconds before next upload...")
                        time.sleep(30)

            except Exception as e:
                print(f"Error processing {json_file}: {e}")
                continue

        return uploaded

    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            self.driver = None


def setup_tiktok():
    """Interactive setup for TikTok automation"""
    print("=" * 60)
    print("TIKTOK AUTO-POSTER SETUP")
    print("=" * 60)

    if not SELENIUM_AVAILABLE:
        print("\n❌ Selenium not installed!")
        print("   Run: pip install selenium webdriver-manager")
        return

    print("\nThis will open a browser window for you to login to TikTok.")
    print("Your session will be saved for future auto-posting.")

    input("\nPress Enter to continue...")

    uploader = TikTokUploader()

    try:
        if uploader.login(manual=True):
            print("\n✅ TikTok setup complete!")
            print("   You can now run automated posts.")
        else:
            print("\n❌ Setup failed. Please try again.")
    finally:
        uploader.close()


if __name__ == "__main__":
    setup_tiktok()
