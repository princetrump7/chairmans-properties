import time
import random
import logging
import os
import json
from playwright.sync_api import sync_playwright, expect
from playwright_stealth import stealth

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config(config_file="config.json"):
    """Load configuration from a JSON file"""
    default_config = {
        "form_data": {
            "phone": "1234567890",
            "city": "New York, NY",
            "years_of_experience": "5",
            "address": "123 Main St"
        },
        "actually_submit": False,
        "session_file": "linkedin_state.json"
    }
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                # Merge with defaults
                default_config.update(config)
                return default_config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
    return default_config

def bezier_curve(p0, p1, p2, p3, steps=10):
    """Calculate cubic Bezier curve points"""
    points = []
    for i in range(steps + 1):
        t = i / steps
        x = (1-t)**3 * p0[0] + 3*(1-t)**2 * t * p1[0] + 3*(1-t) * t**2 * p2[0] + t**3 * p3[0]
        y = (1-t)**3 * p0[1] + 3*(1-t)**2 * t * p1[1] + 3*(1-t) * t**2 * p2[1] + t**3 * p3[1]
        points.append((x, y))
    return points

def human_like_mouse_move(page, selector):
    """Simulate realistic human mouse movements using Bezier curves"""
    try:
        element = page.query_selector(selector)
        if not element:
            return

        bbox = element.bounding_box()
        if not bbox:
            return

        # Simple start point
        start_x, start_y = random.randint(0, 500), random.randint(0, 500)

        target_x = bbox['x'] + bbox['width'] / 2 + random.uniform(-bbox['width']/4, bbox['width']/4)
        target_y = bbox['y'] + bbox['height'] / 2 + random.uniform(-bbox['height']/4, bbox['height']/4)

        # Control points for Bezier curve
        p1 = (start_x + random.uniform(-200, 200), start_y + random.uniform(-200, 200))
        p2 = (target_x + random.uniform(-200, 200), target_y + random.uniform(-200, 200))

        steps = random.randint(20, 40)
        points = bezier_curve((start_x, start_y), p1, p2, (target_x, target_y), steps=steps)

        for x, y in points:
            page.mouse.move(x, y)
            page.wait_for_timeout(int(random.uniform(5, 15)))

    except Exception as e:
        logger.debug(f"Mouse move error: {e}")

def fill_form_fields(page, form_data):
    """Generic logic to detect and interact with standard form input elements"""
    try:
        # Handle text inputs and textareas
        inputs = page.query_selector_all("input[type='text'], textarea, input[type='tel'], input[type='email']")
        for input_el in inputs:
            if input_el.is_visible() and not input_el.input_value():
                id_attr = input_el.get_attribute('id')
                label = page.query_selector(f"label[for='{id_attr}']") if id_attr else None
                label_text = label.inner_text().lower() if label else ""

                if "phone" in label_text or "mobile" in label_text:
                    input_el.fill(form_data.get("phone", "1234567890"))
                    logger.info("Filled phone number field")
                elif "city" in label_text or "location" in label_text:
                    input_el.fill(form_data.get("city", "New York, NY"))
                    logger.info("Filled city/location field")
                elif "experience" in label_text or "years" in label_text:
                    input_el.fill(form_data.get("years_of_experience", "5"))
                    logger.info("Filled years of experience field")
                elif "street" in label_text or "address" in label_text:
                    input_el.fill(form_data.get("address", "123 Main St"))
                    logger.info("Filled address field")

        # Handle dropdowns/selects
        selects = page.query_selector_all("select")
        for select_el in selects:
            if select_el.is_visible():
                current_val = select_el.evaluate("el => el.value")
                options = select_el.query_selector_all("option")
                if options and (not current_val or current_val == options[0].get_attribute("value")):
                    if len(options) > 1:
                        select_el.select_option(index=1)
                        logger.info("Selected option in dropdown")

        # Handle radio buttons
        radios = page.query_selector_all("input[type='radio']")
        radio_groups = {}
        for radio in radios:
            name = radio.get_attribute("name")
            if name:
                if name not in radio_groups:
                    radio_groups[name] = []
                radio_groups[name].append(radio)

        for name, group in radio_groups.items():
            if not any(r.is_checked() for r in group):
                yes_radio = None
                for r in group:
                    label_text = r.evaluate("el => el.parentElement.innerText").lower()
                    if "yes" in label_text:
                        yes_radio = r
                        break
                if yes_radio:
                    yes_radio.check()
                    logger.info(f"Checked 'Yes' for radio group '{name}'")
                else:
                    group[0].check()
                    logger.info(f"Checked first option for radio group '{name}'")

        # Handle checkboxes
        checkboxes = page.query_selector_all("input[type='checkbox']")
        for cb in checkboxes:
            if cb.is_visible() and not cb.is_checked():
                label_text = cb.evaluate("el => el.parentElement.innerText").lower()
                if any(word in label_text for word in ["agree", "consent", "confirm", "understand"]):
                    cb.check()
                    logger.info("Checked agreement checkbox")

    except Exception as e:
        logger.debug(f"Form filling error: {e}")

def solve_recaptcha(page):
    """Handle reCAPTCHA if present"""
    try:
        recaptcha_frame_selector = "iframe[title*='reCAPTCHA']"
        recaptcha_frame_element = page.query_selector(recaptcha_frame_selector)

        if recaptcha_frame_element and recaptcha_frame_element.is_visible():
            recaptcha_frame = page.frame_locator(recaptcha_frame_selector)
            checkbox = recaptcha_frame.locator("div.recaptcha-checkbox-border")

            if checkbox.is_visible():
                logger.info("🔒 reCAPTCHA detected - solving...")
                human_like_mouse_move(page, recaptcha_frame_selector)
                checkbox.click()
                page.wait_for_timeout(3000)

                audio_btn = page.locator("#recaptcha-audio-button")
                if audio_btn.is_visible():
                    logger.warning("🗣️ Audio challenge detected - manual intervention might be needed")
                    audio_btn.click()
                    page.wait_for_timeout(2000)
    except Exception as e:
        logger.debug(f"reCAPTCHA handling error: {e}")

def apply_to_linkedin_job(job_url, config):
    """Main function to apply for a job on LinkedIn"""
    actually_submit = config.get("actually_submit", False)
    session_file = config.get("session_file", "linkedin_state.json")
    form_data = config.get("form_data", {})

    with sync_playwright() as p:
        logger.info("Starting browser...")
        browser = p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-setuid-sandbox',
            ]
        )

        storage_state = session_file if os.path.exists(session_file) else None
        if storage_state:
            logger.info(f"Using existing session state from {session_file}")

        context = browser.new_context(
            storage_state=storage_state,
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York'
        )

        page = context.new_page()
        stealth(page)

        logger.info(f"🚀 Navigating to: {job_url}")
        try:
            page.goto(job_url, wait_until="networkidle", timeout=60000)
        except Exception as e:
            logger.error(f"Failed to load job page: {e}")
            browser.close()
            return False

        page.mouse.wheel(0, random.randint(400, 800))
        page.wait_for_timeout(int(random.uniform(1000, 2500)))

        solve_recaptcha(page)

        easy_apply_selectors = [
            "button.jobs-apply-button",
            "button[aria-label*='Easy Apply']",
            "button:has-text('Easy Apply')"
        ]

        apply_btn_found = False
        for selector in easy_apply_selectors:
            btn = page.query_selector(selector)
            if btn and btn.is_visible():
                human_like_mouse_move(page, selector)
                btn.click()
                logger.info("✅ Clicked Easy Apply button")
                apply_btn_found = True
                break

        if not apply_btn_found:
            logger.warning("❌ Easy Apply button not found. You might need to log in or the job might not support Easy Apply.")
            browser.close()
            return False

        max_steps = 15
        for step in range(1, max_steps + 1):
            logger.info(f"📋 Processing application step {step}")
            page.wait_for_timeout(int(random.uniform(2000, 4000)))
            solve_recaptcha(page)

            fill_form_fields(page, form_data)
            page.wait_for_timeout(int(random.uniform(1000, 2000)))

            nav_buttons = {
                "Next": "button:has-text('Next')",
                "Review": "button:has-text('Review')",
                "Continue": "button[data-test-continue-button]",
                "Submit": "button:has-text('Submit application')"
            }

            clicked_nav = False
            for name, selector in nav_buttons.items():
                btn = page.query_selector(selector)
                if btn and btn.is_enabled() and btn.is_visible():
                    if name == "Submit":
                        logger.info("🎉 Application is ready for submission!")
                        if actually_submit:
                            human_like_mouse_move(page, selector)
                            btn.click()
                            logger.info("🚀 Application SUBMITTED!")
                            page.wait_for_timeout(5000)
                        else:
                            logger.info("💡 actually_submit is False. Skipping final submission.")

                        context.storage_state(path=session_file)
                        logger.info(f"Session state saved to {session_file}")
                        browser.close()
                        return True

                    human_like_mouse_move(page, selector)
                    btn.click()
                    logger.info(f"➡️ Moved to next step via '{name}' button")
                    clicked_nav = True
                    break

            if not clicked_nav:
                error_msg = page.query_selector(".artdeco-inline-feedback--error")
                if error_msg:
                    logger.error(f"🚫 Stopping: Found form error: {error_msg.inner_text().strip()}")
                else:
                    logger.warning("⚠️ No navigation button found. Application might be stuck or complete.")
                break

        browser.close()
        return False

if __name__ == "__main__":
    job_url = input("Enter LinkedIn job URL: ")
    config = load_config()
    apply_to_linkedin_job(job_url, config)
