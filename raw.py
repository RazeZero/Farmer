from selenium import webdriver
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

# Function to handle safe clicking of elements
def safe_click(driver, element, timeout=20):
    try:
        wait = WebDriverWait(driver, timeout)
        clickable_element = wait.until(EC.element_to_be_clickable(element))
        driver.execute_script("arguments[0].scrollIntoView(true);", clickable_element)
        time.sleep(1)
        if clickable_element.is_enabled() and clickable_element.is_displayed():
            try:
                clickable_element.click()
                print("Successfully clicked the element using normal click.")
                return True
            except Exception as e:
                print(f"Normal click failed: {e}")
                driver.execute_script("arguments[0].click();", clickable_element)
                print("Successfully clicked the element using JavaScript.")
                return True
        else:
            print("Element is not enabled or not visible.")
            return False
    except Exception as e:
        print(f"Failed to click element: {e}")
        return False

# Initialize the Chrome driver
driver = webdriver.Chrome()


driver.get('https://raketayo.dropz.xyz/')


driver.delete_all_cookies()

# Define your cookie string (replace with your actual cookie string)
cookie_str = "cookies_here"


for cookie in cookie_str.split(";"):
    try:
        name, value = cookie.split("=", 1)
        cookie_dict = {
            "name": name.strip(),
            "value": value.strip(),
            "domain": "raketayo.dropz.xyz",
            "path": "/"
        }
        driver.add_cookie(cookie_dict)
        print(f"Added cookie: {name.strip()}")
    except ValueError:
        print(f"Skipping malformed cookie: {cookie}")


driver.refresh()


time.sleep(5) #dont adjust sleep time

# Start the infinite loop
while True:
    try:
        # Get the current URL
        current_url = driver.current_url

        # Check if the URL indicates a checkpoint (captcha)
        if "checkpoint" in current_url:
            print("checkpoint detected!! ❌ solve captcha first before bot can run again.")
            while "checkpoint" in driver.current_url:
                time.sleep(5)  # Wait 5 seconds before checking again
            print("Captcha solved. Resuming bot operations.")

        
        if "browse" not in driver.current_url:
            driver.get('https://raketayo.dropz.xyz/member/t/browse')

       
        wait = WebDriverWait(driver, 10)
        button = wait.until(EC.element_to_be_clickable((By.ID, "butn")))

       
        original_window = driver.current_window_handle

        
        success = safe_click(driver, button)

        if success:
            
            time.sleep(2)
            all_windows = driver.window_handles
            if len(all_windows) > 1:
                new_window = [window for window in all_windows if window != original_window][0]
                driver.switch_to.window(new_window)
                time.sleep(11)  
                driver.close()
                driver.switch_to.window(original_window)

            
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "swal2-popup")))

            # Get the modal text and check it
            modal_text = driver.find_element(By.ID, "swal2-html-container").text
            if "Task Complete! Earned 150 points" in modal_text:
                print("User successfully completed the task and earned points ✅")

            # Click the OK button
            ok_button = driver.find_element(By.CLASS_NAME, "swal2-confirm")
            ok_button.click()

            # Check if an ad has appeared
            if "#google_vignette" in driver.current_url:
                try:
                    dismiss_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "dismiss-button")))
                    dismiss_button.click()
                    print("Ad dismissed successfully.")
                except TimeoutException:
                    print("Ad dismiss button not found within 5 seconds.")

            # Wait a bit before the next iteration
            time.sleep(5)

    except KeyboardInterrupt:
        print("Script stopped by user.")
        break

    except Exception as e:
        print(f"An error occurred: {e}")
        time.sleep(5)

# Close the browser
driver.quit()
