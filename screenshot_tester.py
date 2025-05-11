import os
import time
import cv2
import numpy as np
import pyautogui
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import platform

class ScreenshotTester:
    def __init__(self, browser='chrome', headless=False, screenshots_dir='screenshots'):
        """
        Initialize the ScreenshotTester with browser configuration
        
        Args:
            browser (str): Browser to use (currently only 'chrome' supported)
            headless (bool): Run browser in headless mode
            screenshots_dir (str): Directory to store and read screenshots from
        """
        self.browser = browser
        self.headless = headless
        self.screenshots_dir = screenshots_dir
        
        # Create screenshots directory if it doesn't exist
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)
            
        # Initialize the webdriver
        self.driver = self._init_driver()
        
        # Wait a moment to ensure browser is fully initialized
        time.sleep(1)
    
    def _init_driver(self):
        """Initialize and return a webdriver instance"""
        if self.browser.lower() == 'chrome':
            options = Options()
            
            # Check if running on Apple Silicon
            is_arm64 = platform.machine() == 'arm64'
            
            try:
                if is_arm64:
                    # Special handling for Apple Silicon
                    print("Detected Apple Silicon (arm64). Using compatible ChromeDriver...")
                    # Use default Chrome path on macOS
                    options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
                    
                # Create Service with ChromeDriverManager, specifying latest_release=True
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
                return driver
            except Exception as e:
                print(f"Error initializing Chrome driver: {str(e)}")
                print("Attempting alternative initialization method...")
                
                # Alternative method: use selenium-manager directly
                try:
                    driver = webdriver.Chrome(options=options)
                    return driver
                except Exception as e2:
                    raise Exception(f"Failed to initialize Chrome driver: {str(e2)}. Original error: {str(e)}")
        else:
            raise ValueError(f"Browser '{self.browser}' is not supported")
    
    def go_to(self, url):
        """Navigate to the specified URL"""
        self.driver.get(url)
        # Update window position after navigation
        time.sleep(1)
        return self
    
    def take_desktop_screenshot(self, filename=None):
        """
        Take a screenshot of the entire desktop
        
        Args:
            filename (str, optional): Name to save the screenshot. If None, a timestamped name is used.
        
        Returns:
            str: Path to the saved screenshot
        """
        if filename is None:
            filename = f"desktop_screenshot_{int(time.time())}.png"
        
        if not filename.endswith('.png'):
            filename += '.png'
            
        filepath = os.path.join(self.screenshots_dir, filename)
        
        # Use PyAutoGUI to capture the entire screen
        desktop_screenshot = pyautogui.screenshot()
        desktop_screenshot.save(filepath)
        return filepath
    
    def wait_for_match(self, target_image, timeout=10, threshold=0.8):
        """
        Wait for an image to appear on screen
        
        Args:
            target_image (str): Path to the target image or name of image in screenshots directory
            timeout (int): Maximum time to wait in seconds
            threshold (float): Matching threshold (0-1), higher is more strict
            
        Returns:
            tuple: (x, y, w, h) coordinates of match or None if not found
        """            
        if not os.path.exists(target_image):
            raise FileNotFoundError(f"Target image not found: {target_image}")
        
        # Load the template image
        template = cv2.imread(target_image)
        if template is None:
            raise ValueError(f"Could not load template image: {target_image}")
            
        template_height, template_width = template.shape[:2]
        print(f"Template image dimensions: {template_width}x{template_height}")
        
        # Save template image for reference
        template_debug = template.copy()
        cv2.putText(template_debug, "Reference Template", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.imwrite(os.path.join(self.screenshots_dir, "debug_template.png"), template_debug)
        
        start_time = time.time()
        best_match_val = 0
        best_match_loc = None
        
        while time.time() - start_time < timeout:
            # Take screenshot - either desktop or browser
            screenshot_path = self.take_desktop_screenshot("temp_desktop_screenshot.png")
                
            screenshot = cv2.imread(screenshot_path)
            
            if screenshot is None:
                print("Warning: Could not load screenshot image")
                time.sleep(0.5)
                continue

            # Perform template matching
            print(f"Performing template matching with threshold {threshold}...")
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            print(f"Best match value: {max_val:.4f} (threshold: {threshold:.4f})")
            
            # Track best match across attempts
            if max_val > best_match_val:
                best_match_val = max_val
                best_match_loc = max_loc
            
            # Save a debug visualization
            debug_img = screenshot.copy()
            top_left = max_loc
            bottom_right = (top_left[0] + template_width, top_left[1] + template_height)
            
            # Draw a red rectangle for below threshold match, green for good match
            color = (0, 255, 0) if max_val >= threshold else (0, 0, 255)
            cv2.rectangle(debug_img, top_left, bottom_right, color, 2)
            cv2.putText(debug_img, f"Match: {max_val:.4f}", (top_left[0], top_left[1] - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Add threshold value to the image
            cv2.putText(debug_img, f"Threshold: {threshold:.4f}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            
            # Save the debug image with timestamp
            timestamp = int(time.time())
            debug_path = os.path.join(self.screenshots_dir, f"debug_match_{timestamp}.png")
            cv2.imwrite(debug_path, debug_img)
            
            if max_val >= threshold:
                # Match found, return coordinates
                top_left = max_loc
                bottom_right = (top_left[0] + template_width, top_left[1] + template_height)
                match_coords = (top_left[0], top_left[1], template_width, template_height)
                print(f"Match found at {match_coords} with confidence {max_val:.4f}")
                
                # Create a side-by-side comparison for verification
                # Extract the matching region from the screenshot
                matched_region = screenshot[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
                
                return match_coords
            
            # Wait a bit before trying again
            time.sleep(0.5)
        
        # If we get here, no match was found within the timeout
        print(f"No match found for {target_image} within {timeout} seconds")
        
        return None
    
    def click_on_match(self, x, y, w, h):
        """
        Wait for an image to appear and then click on its center using PyAutoGUI
        
        Args:
            x (int): x coordinate of the match
            y (int): y coordinate of the match
            w (int): width of the match
            h (int): height of the match
            
        Returns:
            bool: True if match was found and clicked, False otherwise
        """
        center_x = x + w // 2
        center_y = y + h // 2

        print(f"Clicking on {center_x}, {center_y}")

        pyautogui.moveTo(center_x/2, center_y/2)
        pyautogui.click()
    
    def assert_match(self, target_image, timeout=10, threshold=0.8, message=None):
        """
        Assert that an image appears on screen within timeout
        
        Args:
            target_image (str): Path to the target image or name of image in screenshots directory
            timeout (int): Maximum time to wait in seconds
            threshold (float): Matching threshold (0-1), higher is more strict
            message (str, optional): Custom error message on failure
            
        Raises:
            AssertionError: If the image is not found within timeout
        """
        match = self.wait_for_match(target_image, timeout, threshold)
        
        if not match:
            error_msg = message or f"Element matching '{target_image}' not found within {timeout} seconds"
            # Take a failure screenshot for debugging
            failure_path = self.take_screenshot(f"failure_{os.path.basename(target_image)}")
            raise AssertionError(f"{error_msg} (Failure screenshot saved to {failure_path})")
    
    def close(self):
        """Close the browser and clean up resources"""
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit() 