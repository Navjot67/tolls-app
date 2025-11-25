# E-ZPass NY Toll Dashboard

A beautiful web dashboard to automate fetching and displaying your E-ZPass NY toll balance and violation information.

## Features

- 🔐 Automated login to E-ZPass NY website
- 💰 Real-time toll balance display
- 🧾 Toll charge breakdown
- ⚠️ Violation tracking (count + details)
- 🎨 Modern, responsive dashboard UI
- 📱 Mobile-friendly design

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Selenium will automatically download ChromeDriver

Selenium uses `webdriver-manager` which automatically downloads and manages ChromeDriver, so no manual installation is needed!

### 3. Run the Application

```bash
python app.py
```

### 4. Open in Browser

Navigate to `http://localhost:5000` in your web browser.

## Usage

1. Enter your E-ZPass account number
2. Enter your license plate number
3. Click "Fetch Toll Information"
4. View your balance and violations in the dashboard

## Project Structure

```
tolls/
├── app.py                 # Flask backend server
├── automation_selenium.py # Web automation script using Selenium
├── requirements.txt       # Python dependencies
├── templates/
│   └── dashboard.html    # Dashboard HTML template
└── static/
    ├── style.css         # Dashboard styles
    └── script.js         # Dashboard JavaScript
```

## Notes

- The automation script uses Selenium to interact with the E-ZPass NY website
- The script runs in visible mode by default (browser window will be shown)
- The dashboard stores the last fetched data in memory
- After the account number is entered, the script tabs to the plate field and fills it automatically
- Tolls and violation details are extracted from any tables found on the results page

## Troubleshooting

### Common Issues

1. **ERR_ABORTED Error / Website Blocking**
   - The E-ZPass NY website may block automated browser requests as a security measure
   - This is a common anti-bot protection
   - **Solutions:**
     - Verify you can access the website manually in a regular browser
     - Try using a VPN or different network connection
     - Contact E-ZPass NY to inquire about API access or automation policies
     - The website may require additional authentication or cookies

2. **Target Page Closed Error**
   - Usually occurs when the website blocks the request
   - Check the underlying error message for `ERR_ABORTED` or network issues

3. **Installation Issues**
   - Selenium automatically downloads ChromeDriver via webdriver-manager
   - Make sure Chrome browser is installed on your system
   - Check that your account number and plate number are correct
   - Check the browser console and server logs for errors

### Testing Website Access

To test website access, try fetching toll information through the dashboard. If you encounter `ERR_ABORTED` errors, the website may be blocking automated access.

## License

MIT

