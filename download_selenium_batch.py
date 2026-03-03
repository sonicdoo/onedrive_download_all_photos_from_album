#!/usr/bin/env python3
"""
OneDrive Album Downloader - Selenium Batch Method
Opens page, downloads visible photos in batches, scrolls to load more
"""

import time
import hashlib
from pathlib import Path
# from urllib.parse import urlparse
import requests

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    print("ERROR: Missing dependencies")
    print("Run: pip install selenium webdriver-manager requests")
    exit(1)


class SeleniumBatchDownloader:
    def __init__(self, share_url, output_dir="downloads"):
        self.share_url = share_url
        self.output_dir = Path(output_dir)
        self.downloaded_hashes = set()
        self.downloaded_urls = set()
        self.image_counter = 0
        self.processed_tiles = set()
        
    def setup_driver(self):
        """Setup Chrome driver with download preferences"""
        options = webdriver.ChromeOptions()
        
        # Set download directory
        prefs = {
            "download.default_directory": str(self.output_dir.absolute()),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False
        }
        options.add_experimental_option("prefs", prefs)
        
        # Not headless - visible browser
        # options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Try to use chromedriver without webdriver-manager
        try:
            # First try: just use Chrome without specifying driver path (if chromedriver is in PATH)
            driver = webdriver.Chrome(options=options)
            return driver
        except:
            pass
        
        try:
            # Second try: use webdriver-manager with SSL verification disabled
            import ssl
            import certifi
            ssl._create_default_https_context = ssl._create_unverified_context
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            return driver
        except Exception as e:
            print(f"Error setting up driver: {e}")
            print("\nPlease ensure Chrome and ChromeDriver are installed.")
            print("Download ChromeDriver from: https://chromedriver.chromium.org/")
            raise
    
    def download_album(self):
        """Main download function"""
        print(f"\n{'='*70}")
        print("OneDrive Album Downloader (Selenium Batch Method)")
        print(f"{'='*70}\n")
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 Output: {self.output_dir.absolute()}")
        print(f"🖥️  Mode: Visible browser\n")
        
        driver = self.setup_driver()
        
        try:
            print(f"🌐 Loading: {self.share_url}")
            driver.get(self.share_url)
            time.sleep(5)
            
            # Check if authentication needed
            if 'login.' in driver.current_url or 'signin' in driver.current_url:
                print("\n🔐 Please sign in to your Microsoft account...")
                print("Waiting for authentication (max 3 minutes)...\n")
                
                # Wait for auth
                for i in range(180):
                    time.sleep(1)
                    try:
                        tiles = driver.find_elements(By.CSS_SELECTOR, "div[data-automationid='photo-tile']")
                        if len(tiles) > 0:
                            print(f"✓ Authenticated! Found {len(tiles)} photos in view")
                            time.sleep(3)
                            break
                    except:
                        pass
                else:
                    print("❌ Timeout waiting for authentication")
                    return
            
            print("\n⬇️  Starting batch download process...")
            print(f"Target: 333 photos total\n")
            
            # Download in batches
            batch_num = 0
            scroll_attempts = 0
            max_scroll_attempts = 100
            
            while scroll_attempts < max_scroll_attempts:
                batch_num += 1
                
                # Get visible photo tiles
                tiles = driver.find_elements(By.CSS_SELECTOR, "div[data-automationid='photo-tile']")
                
                # Filter to only new tiles (not already processed)
                # Use image src as unique identifier since data-uniqueid doesn't exist
                new_tiles = []
                for i, tile in enumerate(tiles):
                    try:
                        # Get the image element inside the tile
                        img = tile.find_element(By.CSS_SELECTOR, "img[data-automationid='photo-image']")
                        img_src = img.get_attribute('src')
                        
                        # Use image src or index as unique identifier
                        if img_src and img_src not in self.processed_tiles:
                            new_tiles.append((tile, img_src))
                        elif not img_src:
                            # Fallback: use position index
                            tile_id = f"tile_{i}"
                            if tile_id not in self.processed_tiles:
                                new_tiles.append((tile, tile_id))
                    except:
                        pass
                
                if len(new_tiles) == 0:
                    print(f"\n  Batch {batch_num}: No new photos found")
                    
                    # Try scrolling
                    print(f"  Scrolling... (attempt {scroll_attempts + 1}/{max_scroll_attempts})")
                    
                    # Scroll down slowly
                    driver.execute_script("window.scrollBy(0, 800);")
                    time.sleep(0.8)
                    
                    # Check if we've loaded more
                    new_total = len(driver.find_elements(By.CSS_SELECTOR, "div[data-automationid='photo-tile']"))
                    
                    if new_total == len(tiles):
                        scroll_attempts += 1
                        
                        # If we haven't found new tiles after multiple scrolls, we might be done
                        if scroll_attempts >= 10:
                            print(f"\n  No new photos after {scroll_attempts} scroll attempts")
                            if self.image_counter >= 333:
                                print(f"  ✓ Target reached! ({self.image_counter} photos)")
                                break
                            elif scroll_attempts >= 20:
                                print(f"  Stopping. Downloaded {self.image_counter} photos.")
                                break
                    else:
                        scroll_attempts = 0  # Reset if we found more
                    
                    continue
                
                print(f"\n  Batch {batch_num}: Processing {len(new_tiles)} new photos (total so far: {len(self.processed_tiles)})")
                
                # Download each photo in this batch
                for idx, (tile, tile_id) in enumerate(new_tiles, 1):
                    try:
                        print(f"    [{idx}/{len(new_tiles)}] ", end='', flush=True)
                        
                        # Mark as processed
                        self.processed_tiles.add(tile_id)
                        
                        # Scroll tile into view
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tile)
                        time.sleep(0.3)
                        
                        # Click tile to open viewer
                        tile.click()
                        time.sleep(1.5)
                        
                        # Click the download button
                        try:
                            download_btn = driver.find_element(By.ID, "__photo-view-download")
                            download_btn.click()
                            
                            # Wait for download to start and complete (check for .crdownload)
                            time.sleep(1)
                            max_wait = 30
                            waited = 0
                            while waited < max_wait:
                                # Check if there's a .crdownload file (Chrome download in progress)
                                crdownload_files = list(self.output_dir.glob("*.crdownload"))
                                if len(crdownload_files) == 0:
                                    # No download in progress, should be complete
                                    break
                                time.sleep(0.5)
                                waited += 0.5
                            
                            print(f"✓ downloaded")
                            self.image_counter += 1
                            
                        except Exception as dl_err:
                            print(f"✗ download button error: {dl_err}")
                        
                        # Close viewer with close button
                        try:
                            close_btn = driver.find_element(By.ID, "__photo-view-close")
                            close_btn.click()
                            time.sleep(0.3)
                        except:
                            # Fallback to ESC key
                            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                            time.sleep(0.2)
                        
                        # Check if we've reached target
                        if self.image_counter >= 333:
                            print(f"\n\n✓ Target reached! Downloaded {self.image_counter} photos")
                            return
                    
                    except Exception as e:
                        print(f"✗ failed: {e}")
                        continue
                
                # After processing batch, scroll slowly to load more
                print(f"  Scrolling to load more photos...")
                for _ in range(3):
                    driver.execute_script("window.scrollBy(0, 600);")
                    time.sleep(0.5)
                
                scroll_attempts = 0  # Reset since we processed a batch
            
            # Summary
            image_files = list(self.output_dir.glob('*.jpg')) + list(self.output_dir.glob('*.png'))
            
            print(f"\n{'='*70}")
            print(f"✅ COMPLETE!")
            print(f"{'='*70}")
            print(f"Downloaded: {len(image_files)} unique photos")
            print(f"Location: {self.output_dir.absolute()}")
            print(f"{'='*70}\n")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            time.sleep(2)
            driver.quit()
    
    def download_image(self, url):
        """Download image from URL and verify"""
        try:
            # Convert to full resolution
            url = self.convert_to_full_resolution(url)
            
            # Check if already downloaded
            url_hash = hashlib.md5(url.encode()).hexdigest()
            if url_hash in self.downloaded_urls:
                print(f"⊙ duplicate URL (skipped)")
                return True
            
            # Download
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': self.share_url,
            }
            
            response = requests.get(url, headers=headers, stream=True, timeout=30, verify=False)
            response.raise_for_status()
            
            # Get content
            content = b''
            for chunk in response.iter_content(chunk_size=8192):
                content += chunk
            
            # Verify size
            if len(content) < 5000:
                print(f"✗ too small ({len(content)}B)")
                return False
            
            # Check for duplicate content
            content_hash = hashlib.md5(content).hexdigest()
            if content_hash in self.downloaded_hashes:
                print(f"⊙ duplicate content (skipped)")
                self.downloaded_urls.add(url_hash)
                return True
            
            # Save
            self.image_counter += 1
            self.downloaded_hashes.add(content_hash)
            self.downloaded_urls.add(url_hash)
            
            # Determine extension
            content_type = response.headers.get('content-type', '')
            ext = 'jpg'
            if 'png' in content_type:
                ext = 'png'
            elif 'gif' in content_type:
                ext = 'gif'
            
            filename = f"photo_{self.image_counter:04d}.{ext}"
            filepath = self.output_dir / filename
            
            with open(filepath, 'wb') as f:
                f.write(content)
            
            # Verify file was saved
            if not filepath.exists():
                print(f"✗ save failed")
                return False
            
            saved_size = filepath.stat().st_size
            if saved_size != len(content):
                print(f"✗ size mismatch")
                return False
            
            size_kb = saved_size // 1024
            print(f"✓ {size_kb}KB")
            return True
            
        except Exception as e:
            print(f"✗ download error: {e}")
            return False
    
    def convert_to_full_resolution(self, url):
        """Convert thumbnail URL to full resolution"""
        import re
        # Remove size restrictions
        url = re.sub(r'[&?]width=\d+', '', url)
        url = re.sub(r'[&?]height=\d+', '', url)
        url = re.sub(r'[&?]w=\d+', '', url)
        url = re.sub(r'[&?]h=\d+', '', url)
        
        # Add maximum dimensions if not present
        if 'width=' not in url:
            separator = '&' if '?' in url else '?'
            url += f'{separator}width=9999&height=9999'
        
        return url


def main():
    import sys
    
    url = "https://1drv.ms/a/c/0e.../Ig..." # onedrive album share link
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "downloads"
    
    # Disable SSL warnings if needed
    # mport urllib3
    # urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    downloader = SeleniumBatchDownloader(url, output_dir)
    downloader.download_album()


if __name__ == "__main__":
    main()
