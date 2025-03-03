import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


def setup_browser():
    """Initialize and return a web browser."""
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Uncomment the line below if you want the browser to run in the background
    # chrome_options.add_argument("--headless")

    try:
        # Try using Selenium's built-in manager (newer versions of Selenium)
        browser = webdriver.Chrome(options=chrome_options)
        return browser
    except Exception as e:
        print(f"Error with default Chrome setup: {e}")
        try:
            # Fallback to Safari on macOS
            print("Trying Safari as a fallback...")
            browser = webdriver.Safari()
            return browser
        except Exception as e2:
            print(f"Error with Safari fallback: {e2}")

            # Last resort - try Firefox if available
            try:
                print("Trying Firefox as a last resort...")
                from selenium.webdriver.firefox.options import Options as FirefoxOptions

                firefox_options = FirefoxOptions()
                browser = webdriver.Firefox(options=firefox_options)
                return browser
            except Exception as e3:
                print(f"Error with Firefox fallback: {e3}")
                print("\n=== BROWSER INITIALIZATION FAILED ===")
                print("Please install Chrome, Safari, or Firefox and try again.")
                print(
                    "Alternatively, you can run with SKIP_BROWSER=True to disable browser features."
                )
                print("=== BROWSER INITIALIZATION FAILED ===\n")
                return None


def open_website(browser, url):
    """Open a specific website."""
    if not url.startswith("http"):
        url = "https://" + url
    browser.get(url)
    time.sleep(2)  # Wait for the page to load
    return True


def search_youtube(browser, query):
    """Search for a video on YouTube."""
    open_website(browser, "youtube.com")
    time.sleep(2)  # Wait for page to load

    try:
        search_box = browser.find_element(By.NAME, "search_query")
        search_box.clear()
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        return True
    except Exception as e:
        print(f"Error searching YouTube: {e}")
        return False


def search_google(browser, query):
    """Perform a Google search."""
    open_website(browser, "google.com")
    time.sleep(1)

    try:
        # Handle cookie consent if it appears
        try:
            consent_buttons = browser.find_elements(
                By.XPATH, "//button[contains(text(), 'Accept all')]"
            )
            if consent_buttons:
                consent_buttons[0].click()
                time.sleep(1)
        except:
            pass

        search_box = browser.find_element(By.NAME, "q")
        search_box.clear()
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        return True
    except Exception as e:
        print(f"Error searching Google: {e}")
        return False


def search_amazon(browser, query):
    """Search for products on Amazon."""
    open_website(browser, "amazon.com")
    time.sleep(2)

    try:
        search_box = browser.find_element(By.ID, "twotabsearchtextbox")
        search_box.clear()
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        return True
    except Exception as e:
        print(f"Error searching Amazon: {e}")
        return False


def search_github(browser, query):
    """Search for repositories on GitHub."""
    open_website(browser, "github.com")
    time.sleep(2)

    try:
        # Click on the search box
        search_button = browser.find_element(By.XPATH, "//button[@aria-label='Search']")
        search_button.click()
        time.sleep(1)

        # Find the search input that appears
        search_box = browser.find_element(By.ID, "query-builder-test")
        search_box.clear()
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        return True
    except Exception as e:
        print(f"Error searching GitHub: {e}")
        return False


def search_stackoverflow(browser, query):
    """Search for questions on Stack Overflow."""
    open_website(browser, "stackoverflow.com")
    time.sleep(2)

    try:
        # Handle cookie consent if it appears
        try:
            consent_buttons = browser.find_elements(
                By.XPATH, "//button[contains(text(), 'Accept all cookies')]"
            )
            if consent_buttons:
                consent_buttons[0].click()
                time.sleep(1)
        except:
            pass

        search_box = browser.find_element(By.NAME, "q")
        search_box.clear()
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        return True
    except Exception as e:
        print(f"Error searching Stack Overflow: {e}")
        return False


def take_screenshot(browser, filename=None):
    """Take a screenshot of the current browser window."""
    if filename is None:
        filename = f"screenshot_{int(time.time())}.png"

    try:
        browser.save_screenshot(filename)
        return f"Screenshot saved as {filename}"
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return f"Error taking screenshot: {str(e)}"


def scroll_down(browser, amount=1):
    """Scroll down the page by a certain amount."""
    try:
        for _ in range(amount):
            browser.execute_script("window.scrollBy(0, 500);")
            time.sleep(0.5)
        return True
    except Exception as e:
        print(f"Error scrolling: {e}")
        return False


def fill_form(browser, form_data):
    """
    Fill a form with the provided data.

    Args:
        browser: The browser instance
        form_data: A dictionary mapping field names or IDs to values
    """
    try:
        for selector, value in form_data.items():
            try:
                # Try to find by ID first
                element = browser.find_element(By.ID, selector)
            except:
                try:
                    # Then try by name
                    element = browser.find_element(By.NAME, selector)
                except:
                    try:
                        # Then try by CSS selector
                        element = browser.find_element(By.CSS_SELECTOR, selector)
                    except:
                        print(f"Could not find form element: {selector}")
                        continue

            # Clear the field and enter the value
            element.clear()
            element.send_keys(value)

        return True
    except Exception as e:
        print(f"Error filling form: {e}")
        return False


def click_button(browser, button_text):
    """Click a button with the given text."""
    try:
        # Try to find button by text
        button = browser.find_element(
            By.XPATH, f"//button[contains(text(), '{button_text}')]"
        )
        button.click()
        return True
    except:
        try:
            # Try to find input button by value
            button = browser.find_element(
                By.XPATH,
                f"//input[@type='button' or @type='submit'][contains(@value, '{button_text}')]",
            )
            button.click()
            return True
        except:
            try:
                # Try to find a link with the text
                button = browser.find_element(
                    By.XPATH, f"//a[contains(text(), '{button_text}')]"
                )
                button.click()
                return True
            except Exception as e:
                print(f"Error clicking button '{button_text}': {e}")
                return False


def extract_text(browser, selector_type="body", selector_value="body"):
    """
    Extract text from an element on the page.

    Args:
        browser: The browser instance
        selector_type: The type of selector (id, class, tag, xpath)
        selector_value: The value of the selector
    """
    try:
        if selector_type == "id":
            element = browser.find_element(By.ID, selector_value)
        elif selector_type == "class":
            element = browser.find_element(By.CLASS_NAME, selector_value)
        elif selector_type == "tag":
            element = browser.find_element(By.TAG_NAME, selector_value)
        elif selector_type == "xpath":
            element = browser.find_element(By.XPATH, selector_value)
        else:  # Default to CSS selector
            element = browser.find_element(By.CSS_SELECTOR, selector_value)

        return element.text
    except Exception as e:
        print(f"Error extracting text: {e}")
        return f"Error extracting text: {str(e)}"
