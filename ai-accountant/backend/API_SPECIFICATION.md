# AI Accountant API Specification

## Overview
The AI Accountant API is a FastAPI-based service that automatically categorizes financial transactions using rule-based logic and OpenAI's GPT-4o-mini model for intelligent categorization.

## Base Information
- **Title**: AI Accountant - Lite
- **Version**: 1.0.0
- **Description**: AI-powered transaction categorization service using OpenAI GPT-4o-mini
- **Base URL**: `http://localhost:8000`
- **Documentation**: 
  - Swagger UI: `http://localhost:8000/docs`
  - ReDoc: `http://localhost:8000/redoc`

## Authentication
- **Type**: API Key
- **Key**: OpenAI API Key
- **Value**: `028fa2e1-fb69-4cca-89aa-1e11ffc4dcc1`
- **Base URL**: `https://openai.dplit.com/v1`

## Endpoints

### 1. Root Endpoint
- **URL**: `GET /`
- **Description**: Returns API information
- **Response**: 
```json
{
  "message": "AI Accountant API",
  "version": "1.0.0"
}
```

### 2. Upload CSV (Primary)
- **URL**: `POST /upload_csv`
- **Description**: Upload and categorize CSV file with transaction data
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `file` (required): CSV file with transaction data

#### Required CSV Columns:
- `date`: Transaction date (string)
- `description`: Transaction description (string)
- `amount`: Transaction amount (numeric)
- `currency`: Currency code (string, e.g., USD, EUR)

#### Response Model:
```json
{
  "rows": [
    {
      "date": "2024-01-15",
      "description": "Shell Gas Station",
      "amount": 45.50,
      "currency": "USD",
      "category": "Fuel"
    }
  ],
  "totals": {
    "Fuel": 45.50,
    "Groceries": 120.30,
    "Transport": 25.00
  },
  "summary": {
    "summary": [
      "Total spending: $190.80",
      "Top category: Groceries ($120.30)",
      "Number of transactions: 5"
    ],
    "budget_tip": "Consider meal planning to reduce grocery spending.",
    "tax_hint": "Keep receipts for $45.50 in potentially deductible expenses (Health, Utilities, Transport)."
  }
}
```

### 3. Upload CSV (Frontend Compatible)
- **URL**: `POST /api/v1/upload`
- **Description**: Alias endpoint for frontend compatibility
- **Same functionality as `/upload_csv`**

## Transaction Categories
The API categorizes transactions into the following categories:

1. **Fuel** - Gas stations, fuel purchases
2. **Health/Pharmacy** - Medical expenses, pharmacy purchases
3. **Groceries** - Supermarkets, grocery stores, food markets
4. **Transport** - Uber, taxi, ride-sharing, public transport
5. **Dining** - Restaurants, cafes, food delivery
6. **Utilities** - Electric, water, internet, phone bills
7. **Misc** - Uncategorized or miscellaneous expenses

## Processing Flow

1. **File Validation**: Checks for CSV format and required columns
2. **Rule-Based Categorization**: Applies regex patterns to categorize known transactions
3. **AI Enhancement**: Uses OpenAI GPT-4o-mini to categorize unknown transactions
4. **Insight Generation**: Creates spending analysis and recommendations
5. **Response**: Returns categorized data, totals, and insights

## Error Handling

### 400 Bad Request
- Missing required columns
- Invalid file format (non-CSV)
- Invalid amount values

### 500 Internal Server Error
- Processing errors
- LLM API failures (with fallback to "Misc" category)

## Example Usage

### cURL Example
```bash
curl -X POST "http://localhost:8000/upload_csv" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@transactions.csv"
```

### Python Example
```python
import requests

url = "http://localhost:8000/upload_csv"
files = {"file": open("transactions.csv", "rb")}
response = requests.post(url, files=files)
data = response.json()
```

### JavaScript Example
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:8000/api/v1/upload', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

## Sample CSV Format
```csv
date,description,amount,currency
2024-01-15,Shell Gas Station,45.50,USD
2024-01-16,Walmart Supercenter,120.30,USD
2024-01-17,Uber Ride,25.00,USD
2024-01-18,Starbucks Coffee,8.50,USD
2024-01-19,Electric Bill,85.00,USD
```

## Dependencies
- FastAPI
- pandas
- httpx
- python-multipart
- python-dotenv
- OpenAI API (GPT-4o-mini)

## Rate Limits
- No built-in rate limiting
- Limited by OpenAI API rate limits
- Fallback to "Misc" category if OpenAI API fails
