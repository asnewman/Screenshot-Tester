import os
import time
import shutil
import pyautogui
from screenshot_tester import ScreenshotTester

def run_ajk_test():
    """
    Test that opens ajkprojects.com and finds the RSS button using screenshot matching
    """
    print("Starting AJK Projects test with PyAutoGUI click")
    
    # Check if PyAutoGUI can move the mouse as a basic permissions test
    try:
        initial_pos = pyautogui.position()
        print(f"Initial mouse position: {initial_pos}")
        
        # Try to move the mouse slightly
        test_x, test_y = initial_pos.x + 5, initial_pos.y + 5
        print(f"Attempting to move mouse to: ({test_x}, {test_y})...")
        pyautogui.moveTo(test_x, test_y, duration=0.5)
        
        # Check if the mouse actually moved
        new_pos = pyautogui.position()
        print(f"Mouse position after move: {new_pos}")
        
        if abs(new_pos.x - test_x) > 3 or abs(new_pos.y - test_y) > 3:
            print("\n⚠️ WARNING: PyAutoGUI cannot move the mouse!")
            print("This is likely due to permission issues or security settings.")
            print("The test will continue but will require manual interaction.")
            
            # Set a flag to indicate PyAutoGUI automation won't work
            can_automate = False
        else:
            print("PyAutoGUI mouse movement working correctly.")
            can_automate = True
            
        # Move mouse back to original position
        pyautogui.moveTo(initial_pos.x, initial_pos.y, duration=0.2)
    except Exception as e:
        print(f"Error testing PyAutoGUI: {str(e)}")
        can_automate = False
    
    # Initialize the screenshot tester
    tester = ScreenshotTester()
    
    try:
        # Navigate to AJK Projects
        tester.go_to("https://ajkprojects.com/")
        print("ajkprojects.com opened in Chrome browser.")
        time.sleep(2)  # Wait for page to fully load
        
        # Check if the screenshot directory exists, create if needed
        if not os.path.exists('screenshots'):
            os.makedirs('screenshots')
            print("Created 'screenshots' directory.")
        
        # Path for the RSS button screenshot and after_click reference
        rss_button_path = os.path.join('simple_test', 'rss_button.png')
        after_click_path = os.path.join('simple_test', 'after_click.png')
        
        # Check reference screenshots
        if not os.path.exists(rss_button_path):
            print(f"Error: {rss_button_path} not found.")
            print("Please create a screenshot of the RSS button first.")
            return
        
        if not os.path.exists(after_click_path):
            print(f"Error: {after_click_path} not found.")
            print("Please provide an after_click.png reference image to verify that the click worked.")
            return
        
        print(f"Using reference images: {rss_button_path} and {after_click_path}")
        
        # Try to match the RSS button on the page
        print("\nLooking for the RSS button on the page using image matching...")
        
        # Use the desktop screenshot approach for finding the RSS button
        match_result = tester.wait_for_match(rss_button_path, timeout=10, threshold=0.6)
        if match_result:
            x, y, w, h = match_result
            center_x = x + w // 2
            center_y = y + h // 2
            print(f"✅ Found the RSS button at coordinates: ({x}, {y}), size: {w}x{h}")
            print(f"Center point in desktop screenshot: ({center_x}, {center_y})")
            
            # Attempt to click with PyAutoGUI
            print("\nAttempting to click the RSS button automatically...")
            try:
                tester.click_on_match(x, y, w, h)
                print("✅ Sent click event to the RSS button.")
                time.sleep(3)  # Wait for page to update
            except Exception as e:
                print(f"Automated click failed: {str(e)}")
                can_automate = False  # Fall back to manual
            
            # Take a screenshot after clicking for verification
            after_click_actual = tester.take_desktop_screenshot("after_click_actual.png")
            
            # Get the current URL after clicking
            current_url = tester.driver.current_url
            print(f"Current URL after click: {current_url}")
            
            # Verify the click worked by comparing with after_click.png
            print("\nVerifying the click worked by comparing with after_click.png...")
            
            # Check if the after_click.png matches something on the current page
            print("Attempting to match the after_click.png reference image...")
            verify_result = tester.wait_for_match(after_click_path, timeout=5, threshold=0.5)  # Lower threshold for verification
            
            if verify_result:
                verify_x, verify_y, verify_w, verify_h = verify_result
                print(f"✅ Verification successful! Found match at ({verify_x}, {verify_y}), size: {verify_w}x{verify_h}")
                print("The click worked as expected and produced the expected changes.")
                return True
            else:
                print("❌ Verification failed. The click did not produce the expected UI change.")
                print("\nPossible reasons:")
                print("1. The RSS button was not actually clicked (wrong element or click not registered)")
                print("2. The 'after_click.png' image doesn't match what actually appears after clicking")
                print("3. The website behavior has changed since the reference image was created")
        else:
            print("❌ Could not find the RSS button on the page.")
        
        print("\nTest completed.")
        return False
    finally:
        # Clean up
        tester.close()
        print("Browser closed.")

if __name__ == "__main__":
    run_ajk_test() 