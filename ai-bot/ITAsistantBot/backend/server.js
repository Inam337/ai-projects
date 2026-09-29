const express = require('express');
const fs = require('fs').promises;
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = 3001;
const JSON_FILE_PATH = path.join(__dirname, 'api', 'bot.json');

// Middleware
app.use(cors());
app.use(express.json());

// Read the current bot.json file
app.get('/api/bot', async (req, res) => {
  try {
    const data = await fs.readFile(JSON_FILE_PATH, 'utf8');
    res.json(JSON.parse(data));
  } catch (error) {
    console.error('Error reading bot.json:', error);
    res.status(500).json({ error: 'Failed to read bot.json' });
  }
});

// Write/Update the bot.json file
app.post('/api/bot', async (req, res) => {
  try {
    const solutions = req.body;
    
    // Validate the data structure
    if (!Array.isArray(solutions)) {
      return res.status(400).json({ error: 'Data must be an array' });
    }

    // Validate each solution
    for (const solution of solutions) {
      if (!solution.title || !solution.problem_statement || !solution.description || !solution.action) {
        return res.status(400).json({ error: 'Invalid solution structure' });
      }
    }

    // Write to file
    await fs.writeFile(JSON_FILE_PATH, JSON.stringify(solutions, null, 2), 'utf8');
    
    res.json({ 
      success: true, 
      message: 'bot.json updated successfully',
      count: solutions.length 
    });
  } catch (error) {
    console.error('Error writing bot.json:', error);
    res.status(500).json({ error: 'Failed to write bot.json' });
  }
});

// Add a single solution
app.post('/api/bot/add', async (req, res) => {
  try {
    const newSolution = req.body;
    
    // Validate the solution
    if (!newSolution.title || !newSolution.problem_statement || !newSolution.description || !newSolution.action) {
      return res.status(400).json({ error: 'Invalid solution structure' });
    }

    // Read current solutions
    const data = await fs.readFile(JSON_FILE_PATH, 'utf8');
    const solutions = JSON.parse(data);

    // Add new solution
    solutions.push(newSolution);

    // Write back to file
    await fs.writeFile(JSON_FILE_PATH, JSON.stringify(solutions, null, 2), 'utf8');
    
    res.json({ 
      success: true, 
      message: 'Solution added successfully',
      count: solutions.length 
    });
  } catch (error) {
    console.error('Error adding solution:', error);
    res.status(500).json({ error: 'Failed to add solution' });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
  console.log(`Bot.json file location: ${JSON_FILE_PATH}`);
});

