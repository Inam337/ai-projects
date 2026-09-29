# AI Accountant - Environment Configuration

## Required Environment Variables

Create a `.env` file in the backend directory with the following variables:

```bash
# OpenAI API Configuration
OPENAI_API_KEY=028fa2e1-fb69-4cca-89aa-1e11ffc4dcc1
OPENAI_BASE_URL=https://openai.dplit.com/v1
OPENAI_MODEL=gpt-4o-mini
```

## Setup Instructions

1. **Create .env file**:
   ```bash
   cd backend
   echo "OPENAI_API_KEY=028fa2e1-fb69-4cca-89aa-1e11ffc4dcc1" > .env
   echo "OPENAI_BASE_URL=https://openai.dplit.com/v1" >> .env
   echo "OPENAI_MODEL=gpt-4o-mini" >> .env
   ```

2. **Or manually create the file**:
   - Create a file named `.env` in the `backend` directory
   - Add the environment variables as shown above

3. **Verify the setup**:
   ```bash
   cd backend
   python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('API Key:', os.getenv('OPENAI_API_KEY')[:10] + '...')"
   ```

## Security Notes

- Never commit `.env` files to version control
- The `.env` file should be added to `.gitignore`
- For production, use secure environment variable management

## Alternative: Set Environment Variables Directly

If you can't create a `.env` file, you can set environment variables directly:

**Windows (PowerShell)**:
```powershell
$env:OPENAI_API_KEY="028fa2e1-fb69-4cca-89aa-1e11ffc4dcc1"
$env:OPENAI_BASE_URL="https://openai.dplit.com/v1"
```

**Windows (Command Prompt)**:
```cmd
set OPENAI_API_KEY=028fa2e1-fb69-4cca-89aa-1e11ffc4dcc1
set OPENAI_BASE_URL=https://openai.dplit.com/v1
```

**Linux/Mac**:
```bash
export OPENAI_API_KEY="028fa2e1-fb69-4cca-89aa-1e11ffc4dcc1"
export OPENAI_BASE_URL="https://openai.dplit.com/v1"
```
