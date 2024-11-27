const express = require('express');
const bodyParser = require('body-parser');
const { spawn } = require('child_process');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

const app = express();
app.use(bodyParser.json());

// Endpoint to start the bot
app.post('/start-bot', (req, res) => {
    const pythonProcess = spawn('python', ['../bybit_bot/bybit_trading_bot.py']);
    pythonProcess.stdout.on('data', (data) => {
        console.log(`Bot Output: ${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`Bot Error: ${data}`);
    });

    res.send({ message: 'Bot started!' });
});

// Endpoint to stop the bot (not perfect, needs PID tracking)
app.post('/stop-bot', (req, res) => {
    res.send({ message: 'Stopping bot requires custom logic (e.g., process.kill).' });
});

// Example status endpoint
app.get('/status', (req, res) => {
    res.send({ message: 'Bot is running...' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
