# E-ZPass NJ Automation

Automation script for fetching violation/invoice information from E-ZPass New Jersey website.

## Features

- ✅ Fetch violation/invoice information by violation number and license plate
- ✅ Extract balance due amounts
- ✅ Extract violation/invoice details
- ✅ Integrated with existing dashboard system
- ✅ API endpoints for programmatic access

## Usage

### Command Line

```bash
python3 automation_selenium_nj.py <violation_number> <plate_number>
```

Example:
```bash
python3 automation_selenium_nj.py T13255735180201 T127211C
```

### Python API

```python
from automation_selenium_nj import extract_toll_info_nj

result = extract_toll_info_nj(
    violation_number="T13255735180201",
    plate_number="T127211C",
    headless=False
)

print(result)
```

### REST API

**Endpoint:** `POST /api/fetch-nj-violation`

**Request:**
```json
{
  "violation_number": "T13255735180201",
  "plate_number": "T127211C"
}
```

**Response:**
```json
{
  "success": true,
  "violation_number": "T13255735180201",
  "plate_number": "T127211C",
  "balance_amount": 25.50,
  "violation_count": 1,
  "toll_bill_numbers": ["T13255735180201"],
  "source": "NJ E-ZPass"
}
```

### Using curl

```bash
curl -X POST http://localhost:5000/api/fetch-nj-violation \
  -H "Content-Type: application/json" \
  -d '{
    "violation_number": "T13255735180201",
    "plate_number": "T127211C"
  }'
```

## Parameters

- **violation_number** (required): The violation/invoice number (e.g., "T13255735180201")
- **plate_number** (required): License plate number (e.g., "T127211C")
- **account_number** (optional): E-ZPass account number (not currently used)
- **headless** (optional): Run browser in headless mode (default: False)

## Website Reference

Based on the E-ZPass NJ website: https://www.ezpassnj.com/en/home/index.shtml

The automation accesses the "Invoice / Violations / Toll-by-Plate" section to look up violation information.

## Integration

The NJ automation is fully integrated with the existing system:

- API endpoint: `/api/fetch-nj-violation`
- Can be added to saved accounts with `source: "NJ"` field
- Supports the same email automation features
- Compatible with existing dashboard UI

## Differences from NY E-ZPass

| Feature | NY E-ZPass | NJ E-ZPass |
|---------|------------|------------|
| Lookup Method | Account + Plate | Violation Number + Plate |
| Login Required | No (public lookup) | No (public lookup) |
| Account Access | Yes | No (violation lookup only) |
| Data Source | Account balance | Violation/invoice amount |

## Troubleshooting

### Element Not Found

If you get "Could not find violation input fields", the website structure may have changed. Check:
1. The website is accessible
2. The violation lookup form is visible
3. Browser can interact with the page

### Modal/Popup Issues

The violation lookup opens in a modal. The script handles this by:
- Waiting for the modal to appear
- Using JavaScript clicks for reliability
- Multiple fallback methods for finding elements

## Notes

- The script runs in visible mode by default (you'll see the browser)
- Violation lookups may take 10-15 seconds to complete
- The website may have rate limiting or bot protection




