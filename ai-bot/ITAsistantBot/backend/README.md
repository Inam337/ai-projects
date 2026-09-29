# Backend API Server

Simple Express server to handle writing solutions to `bot.json`.

## Setup

1. Install dependencies:
```bash
cd backend
npm install
```

2. Start the server:
```bash
npm start
```

The server will run on `http://localhost:3001`

## API Endpoints

### GET /api/bot
Get all solutions from bot.json

### POST /api/bot
Update the entire bot.json file with a new array of solutions

### POST /api/bot/add
Add a single solution to the existing bot.json file

## Usage

The frontend will automatically send form submissions to this API when adding or updating solutions.

