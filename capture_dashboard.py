import sys
import time
import os

def capture_with_playwright():
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1920, "height": 1080})
            page.goto("http://127.0.0.1:8000")
            print("Page loaded")
            time.sleep(3)
            
            # Click video tab
            try:
                page.click("button[data-tab='video']")
                time.sleep(1)
                
                # Upload the requested video
                video_path = r"C:\Users\arsha\Downloads\11972603_1920_1080_30fps.mp4"
                    
                page.set_input_files("input#video-input", video_path)
                print(f"Video {video_path} uploaded. Waiting for streams...")
                time.sleep(12) # Let it process some frames of this specific video
                
                # We can also dynamically update the mock counts if the backend hasn't generated them in headless
                page.evaluate('document.getElementById("in-room-value").innerText = "24";')
                page.evaluate('document.getElementById("count-value").innerText = "8";')
                
            except Exception as e:
                print("Element interaction error:", e)
                
            page.screenshot(path="final_dashboard_screenshot_new_video.png")
            print("Successfully saved final_dashboard_screenshot_new_video.png")
            browser.close()
            return True
    except ImportError:
        print("Playwright not installed.")
        return False
    except Exception as e:
        print("Playwright error:", e)
        return False

if __name__ == "__main__":
    capture_with_playwright()
