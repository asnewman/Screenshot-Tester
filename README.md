# Screenshot Tester

A Python-based tool for automated visual testing using screenshot comparison and template matching. This tool is particularly useful for end-to-end testing and visual regression testing of web applications.

## Features

- Automated screenshot capture of desktop and web pages
- Template matching with configurable thresholds
- Support for Chrome browser automation
- Visual debugging with match visualization
- Apple Silicon (M1/M2) compatibility

## Prerequisites

- Python 3.7+
- Google Chrome browser

## Installation

1. Clone the repository

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```


## Usage

Here's a basic example of how to use the ScreenshotTester:

```python
from screenshot_tester import ScreenshotTester

# Initialize the tester
tester = ScreenshotTester(headless=False)

try:
    # Navigate to a webpage
    tester.go_to("https://example.com")
    
    # Take a screenshot
    screenshot_path = tester.take_desktop_screenshot("example.png")
    
    # Wait for and click on a specific element
    match = tester.wait_for_match("target_element.png", timeout=10, threshold=0.8)
    if match:
        x, y, w, h = match
        tester.click_on_match(x, y, w, h)
    
    # Assert that an element is visible
    tester.assert_match("expected_element.png", timeout=5, threshold=0.8)
    
finally:
    # Clean up
    tester.close()
```

## Key Methods

- `__init__(browser='chrome', headless=False, screenshots_dir='screenshots')`: Initialize the tester
- `go_to(url)`: Navigate to a URL
- `take_desktop_screenshot(filename=None)`: Capture a screenshot of the entire desktop
- `wait_for_match(target_image, timeout=10, threshold=0.8)`: Wait for an image to appear on screen
- `click_on_match(x, y, w, h)`: Click on a matched element
- `assert_match(target_image, timeout=10, threshold=0.8, message=None)`: Assert that an image appears on screen
- `close()`: Clean up resources

## Screenshots Directory

The tool automatically creates and manages a `screenshots` directory where it stores:
- Captured screenshots
- Debug visualizations
- Template matching results
- Failure screenshots

## Debugging

The tool provides visual debugging capabilities:
- Saves debug images with match visualization
- Shows confidence scores for matches
- Creates side-by-side comparisons
- Saves failure screenshots when assertions fail

## Notes

- For Apple Silicon Macs, the tool automatically detects the architecture and uses the appropriate ChromeDriver
- The tool uses OpenCV for template matching with configurable thresholds


## Contributing

Feel free to submit issues and enhancement requests! 