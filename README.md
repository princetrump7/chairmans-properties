# LinkedIn Easy Apply Bot

A stealthy, human-like automated tool for applying to LinkedIn jobs using Playwright.

## ✨ Features

- **Human-like Interactions**: Simulates realistic mouse movements using Bezier curves and natural typing/scrolling behaviors.
- **Enhanced Stealth**: Integrates `playwright-stealth` and custom fingerprinting to bypass bot detection systems.
- **Automated Form Handling**: Intelligently detects and interacts with common application form elements (text inputs, selects, radios, checkboxes).
- **reCAPTCHA Support**: Basic detection and handling of reCAPTCHA challenges.
- **Session Management**: Supports saving and loading LinkedIn session states to avoid repeated logins.
- **Configurable**: Easily manage application data and behavior via a JSON configuration file.
- **Robust Error Handling**: Comprehensive logging and error recovery for a more reliable automation experience.

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

### Configuration

The bot uses a `config.json` file for automation settings. You can customize it as follows:

```json
{
  "form_data": {
    "phone": "1234567890",
    "city": "New York, NY",
    "years_of_experience": "5",
    "address": "123 Main St"
  },
  "actually_submit": false,
  "session_file": "linkedin_state.json"
}
```

- `form_data`: Information used to fill out common application fields.
- `actually_submit`: Set to `true` to actually click the final submit button.
- `session_file`: Path to store/load the LinkedIn login session.

### Usage

1. (Optional) Log into LinkedIn manually and save the session state to `linkedin_state.json` to bypass login screens.
2. Configure your details in `config.json`.
3. Run the bot:
   ```bash
   python linkedin_bot.py
   ```
4. Enter the LinkedIn job URL when prompted.

## 📄 License

This project is open-source and free to use or modify under the MIT License.
