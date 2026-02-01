# LinkedIn Easy Apply Bot

A stealthy, human-like automated tool for applying to LinkedIn jobs using Playwright.

## ✨ Features

- **Human-like Interactions**: Simulates realistic mouse movements using Bezier curves and natural typing/scrolling behaviors.
- **Enhanced Stealth**: Integrates `playwright-stealth` and custom fingerprinting to bypass bot detection systems.
- **Automated Form Handling**: Intelligently detects and interacts with common application form elements.
- **reCAPTCHA Support**: Basic detection and handling of reCAPTCHA challenges.
- **Session Management**: Supports saving and loading LinkedIn session states to avoid repeated logins.
- **Robust Error Handling**: Improved logging and error recovery for a more reliable automation experience.

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- [Playwright](https://playwright.dev/python/docs/intro)

### Installation

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

### Usage

1. (Optional) Create a `linkedin_state.json` by logging into LinkedIn manually and saving the state.
2. Run the bot:
   ```bash
   python linkedin_bot.py
   ```
3. Enter the LinkedIn job URL when prompted.

## 📄 License

This project is open-source and free to use or modify under the MIT License.
