# OneDrive Photo Album Downloader

Since onedrive web does not offer a simple download all pictures from a onedrive album ...
This tool is to download photos from shared OneDrive albums using browser automation and web scraping techniques.

## 🌟 Features

- **Selenium Batch Downloader**: Smart batch processing with auto-scrolling and authentication support
- **Playwright Automation**: Modern browser automation alternative
- **Chrome DevTools Protocol**: Direct CDP communication for advanced control
- **Authentication Handling**: Supports both public and private/authenticated albums
- **Duplicate Prevention**: Intelligent tracking to avoid re-downloading photos
- **Progress Tracking**: Real-time progress indicators and batch statistics
- **Flexible Output**: Configurable download directories

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Google Chrome browser (for Selenium/CDP methods)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/onedrive-photo-downloader.git
cd onedrive-photo-downloader

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate.ps1
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# Recommended: Selenium Batch Method (handles authentication)
python download_selenium_batch.py "YOUR_ONEDRIVE_ALBUM_URL"

# Alternative methods
python download_playwright.py "YOUR_ONEDRIVE_ALBUM_URL"
python download_cdp.py "YOUR_ONEDRIVE_ALBUM_URL"
```

## 📦 Available Scripts

### 🎯 `download_selenium_batch.py` (Recommended)

**Best for: Private/authenticated albums**

Automated browser-based downloader with intelligent batch processing.

**Features:**
- Opens visible Chrome browser for manual authentication
- Downloads photos in batches while scrolling to load more
- Waits up to 3 minutes for Microsoft account sign-in
- Tracks processed tiles to prevent duplicates
- Monitors download completion (watches for `.crdownload` files)
- Smart scrolling to trigger lazy-loading
- Detailed progress reporting

**Usage:**
```bash
python download_selenium_batch.py "YOUR_ALBUM_URL" [output_directory]

# Examples:
python download_selenium_batch.py "https://1drv.ms/a/c/..." downloads
python download_selenium_batch.py "https://1drv.ms/a/c/..."  # defaults to 'downloads'
```

**How it works:**
1. Opens OneDrive album in Chrome
2. Detects authentication requirement and waits for login
3. Finds photo tiles on the page
4. For each batch:
   - Clicks photo → Opens viewer
   - Clicks download button
   - Waits for download completion
   - Closes viewer
5. Scrolls to load more photos
6. Repeats until target count or no more photos found

### 🎭 `download_playwright.py`

**Best for: Modern browser automation**

Uses Playwright for reliable cross-browser automation.

**Features:**
- Supports Chrome, Firefox, and WebKit
- Better performance than Selenium
- Modern async/await patterns
- Built-in auto-waiting

**Usage:**
```bash
python download_playwright.py "YOUR_ALBUM_URL"
```

### 🔧 `download_cdp.py`

**Best for: Advanced control and debugging**

Uses Chrome DevTools Protocol for direct browser communication.

**Features:**
- Low-level browser control
- Network request interception
- Performance monitoring
- Direct Chrome communication

**Usage:**
```bash
python download_cdp.py "YOUR_ALBUM_URL"
```

### 🛠️ Utility Scripts

- **`debug_page.py`**: Debug tool to inspect page structure and elements
- **`diagnose_page.py`**: Diagnostic tool to analyze album accessibility
- **`download_pw.py`**: Alternative Playwright implementation
- **`download_final.py`**: Consolidated downloader with multiple fallback methods

## 🔧 Requirements

```txt
requests>=2.31.0          # HTTP library
beautifulsoup4>=4.12.0    # HTML parsing
selenium>=4.15.0          # Browser automation
webdriver-manager>=4.0.0  # Automatic ChromeDriver management
playwright>=1.40.0        # Modern browser automation
```

## 📖 Detailed Configuration

### Custom Output Directory

```bash
python download_selenium_batch.py "YOUR_URL" ./my_photos
```

### Authentication

For private albums:
1. Script opens browser automatically
2. Sign in when prompted
3. Wait for "Authenticated!" message
4. Downloads proceed automatically

### Target Photo Count

By default, `download_selenium_batch.py` targets 333 photos. Modify in the script:

```python
# Line ~91 in download_selenium_batch.py
print(f"Target: 333 photos total\n")  # Change this number

# Line ~233
if self.image_counter >= 333:  # Change this threshold
```

## 🐛 Troubleshooting

### Issue: ChromeDriver not found

**Solution:**
```bash
# Install webdriver-manager (already in requirements.txt)
pip install webdriver-manager

# Or manually download ChromeDriver:
# https://chromedriver.chromium.org/downloads
```

### Issue: Authentication timeout

**Solution:**
- Increase timeout in script (line ~103):
```python
for i in range(180):  # Change to 300 for 5 minutes
```
- Sign in quickly when browser opens
- Check Microsoft account has album access

### Issue: SSL Certificate Errors

**Solution:**
The scripts already disable SSL warnings. If issues persist:
```bash
# Set environment variable
export PYTHONHTTPSVERIFY=0  # Linux/Mac
$env:PYTHONHTTPSVERIFY=0     # Windows PowerShell
```

### Issue: Downloads are incomplete

**Solution:**
- Check `downloads/` folder for `.crdownload` files
- Increase download wait timeout (line ~206):
```python
max_wait = 30  # Increase to 60 for slow connections
```

### Issue: "No new photos found" but album has more

**Solution:**
- Increase scroll attempts (line ~97):
```python
max_scroll_attempts = 100  # Increase to 200
```
- Try slower scrolling speed (line ~246):
```python
time.sleep(0.5)  # Increase to 1.0 or 2.0
```

## 📊 Expected Output

```
======================================================================
OneDrive Album Downloader (Selenium Batch Method)
======================================================================

📁 Output: C:\path\to\downloads
🖥️  Mode: Visible browser

🌐 Loading: https://1drv.ms/...
🔐 Please sign in to your Microsoft account...
✓ Authenticated! Found 20 photos in view

⬇️  Starting batch download process...
Target: 120 photos total

  Batch 1: Processing 20 new photos (total so far: 0)
    [1/20] ✓ downloaded
    [2/20] ✓ downloaded
    ...
    [20/20] ✓ downloaded
  Scrolling to load more photos...

  Batch 2: Processing 18 new photos (total so far: 20)
    ...

======================================================================
✅ COMPLETE!
======================================================================
Downloaded: 120 unique photos
Location: C:\path\to\downloads
======================================================================
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
# Install dev dependencies
pip install -e .
pip install pytest black flake8

# Run tests
pytest

# Format code
black *.py

# Lint
flake8 *.py
```

## 📄 License

MIT License - feel free to use this code for personal or commercial projects.

## ⚠️ Disclaimer

This tool is for educational purposes and personal use only. Respect Microsoft's Terms of Service and only download photos you have permission to access. Always ensure you have the right to download shared content.

## 🙏 Acknowledgments

- Built with [Selenium](https://www.selenium.dev/)
- [Playwright](https://playwright.dev/) for modern automation
- [webdriver-manager](https://github.com/SergeyPirogov/webdriver_manager) for driver management

## 📮 Support

Found a bug or have a feature request? Please open an issue on GitHub.

---

**Made with ❤️ for easier photo management**