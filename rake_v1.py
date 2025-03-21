import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
import datetime

# Set up the Tkinter GUI
root = tk.Tk()
root.title("Automation Bot")
root.geometry("600x400")
root.configure(bg="#2b2b2b")  # Dark background for modern look

# Define styles for themed widgets
style = ttk.Style()
style.configure("TFrame", background="#2b2b2b")
style.configure("TLabel", background="#2b2b2b", foreground="#ffffff", font=("Helvetica", 12))
style.configure("Title.TLabel", background="#2b2b2b", foreground="#00ccff", font=("Helvetica", 14, "bold"))

# Title label with a splash of color
title_label = ttk.Label(root, text="Rake Tayo Automation Bot", style="Title.TLabel")
title_label.pack(pady=10)

# Frame for the text area with subtle border
frame = ttk.Frame(root, style="TFrame", padding=10, relief="flat", borderwidth=2)
frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

# Scrolled text area with dark theme and monospaced font
text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, bg="#1e1e1e", fg="#e0e0e0", 
                                      font=("Consolas", 12), state=tk.DISABLED, borderwidth=0, highlightthickness=0)
text_area.pack(fill=tk.BOTH, expand=True)

# Function to update the GUI text area with timestamp (thread-safe)
def update_text(message):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    root.after(0, lambda: text_area.config(state=tk.NORMAL))
    root.after(0, lambda: text_area.insert(tk.END, f"[{timestamp}] {message}\n"))
    root.after(0, lambda: text_area.see(tk.END))
    root.after(0, lambda: text_area.config(state=tk.DISABLED))

# Countdown function before starting automation
def countdown(seconds):
    if seconds > 0:
        update_text(f"Bot has been started, running the automation in {seconds}...")
        root.after(1000, countdown, seconds - 1)
    else:
        update_text("Automation started!")
        automation_thread.start()

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
                update_text("Successfully clicked the element using normal click.")
                return True
            except Exception as e:
                print(f"Normal click failed: {e}")
                driver.execute_script("arguments[0].click();", clickable_element)
                update_text("Successfully clicked the element using JavaScript.")
                return True
        else:
            update_text("Element is not enabled or not visible.")
            return False
    except Exception as e:
        print(f"Failed to click element: {e}")
        return False

# Function to dismiss ads
def dismiss_ad(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it(
                (By.XPATH, "//iframe[contains(@src, 'google_vignette')]")
            )
        )
        dismiss_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "dismiss-button"))
        )
        dismiss_button.click()
        print("Ad dismissed successfully.")
        driver.switch_to.default_content()
    except TimeoutException:
        try:
            dismiss_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//*[contains(text(), 'Close') or contains(text(), 'Skip Ad')]")
                )
            )
            dismiss_button.click()
            print("Ad dismissed via alternative button.")
            driver.switch_to.default_content()
        except TimeoutException:
            print("No dismiss options found.")

# Main automation function
def run_automation():
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)

    update_text("Browser started opening site...")
    driver.get('https://raketayo.dropz.xyz/')

    driver.delete_all_cookies()
    update_text("Injecting cookies...")
    cookie_str = "cookies_here"
    
    for cookie in cookie_str.split(";"):
        try:
            name, value = cookie.split("=", 1)
            cookie_dict = {"name": name.strip(), "value": value.strip(), "domain": "raketayo.dropz.xyz", "path": "/"}
            driver.add_cookie(cookie_dict)
            update_text(f"Added cookie: {name.strip()}")
        except ValueError:
            update_text(f"Skipping malformed cookie: {cookie}")

    driver.refresh()
    update_text("Loading...")
    time.sleep(5)

    while True:
        try:
            current_url = driver.current_url

            if "checkpoint" in current_url:
                update_text("Check point detected!! ❌ Solve captcha first before bot can run again.")
                while "checkpoint" in driver.current_url:
                    time.sleep(5)
                update_text("Captcha solved. Resuming bot operations.")

            if "browse" not in driver.current_url:
                driver.get('https://raketayo.dropz.xyz/member/t/browse')
                update_text("Navigated to browse page.")

            ad_attempts = 0
            max_attempts = 3

            while True:
                try:
                    button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.ID, "butn"))
                    )
                    update_text("Starting task...")
                    safe_click(driver, button)
                    break
                except ElementClickInterceptedException:
                    if ad_attempts < max_attempts:
                        ad_attempts += 1
                        update_text(f"Ad detected, attempting to dismiss (attempt {ad_attempts})...")
                        dismiss_ad(driver)
                        time.sleep(2)
                    else:
                        update_text("Max ad dismissal attempts reached. Refreshing page.")
                        driver.refresh()
                        time.sleep(5)
                        ad_attempts = 0
                except TimeoutException:
                    print("Button not found, possibly page not loaded.")
                    time.sleep(5)
                    continue

            original_window = driver.current_window_handle
            time.sleep(2)
            all_windows = driver.window_handles
            if len(all_windows) > 1:
                new_window = [window for window in all_windows if window != original_window][0]
                driver.switch_to.window(new_window)
                update_text("Switched to new window.")
                time.sleep(11)
                driver.close()
                driver.switch_to.window(original_window)
                update_text("Switched back to original window.")

            try:
                WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, "swal2-popup"))
                )
                modal_text = driver.find_element(By.ID, "swal2-html-container").text
                if "Task Complete! Earned 150 points" in modal_text:
                    update_text("Earned points ✅")
                ok_button = driver.find_element(By.CLASS_NAME, "swal2-confirm")
                ok_button.click()
                update_text("Clicked OK on the modal.")
            except TimeoutException:
                print("Modal not found.")

            time.sleep(5)

        except KeyboardInterrupt:
            update_text("Script stopped by user.")
            driver.quit()
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            update_text("An error occurred, retrying...")
            time.sleep(5)

    driver.quit()

# Set up the automation thread as a daemon
automation_thread = threading.Thread(target=run_automation, daemon=True)

# Start the countdown and GUI
countdown(5)
root.mainloop()
