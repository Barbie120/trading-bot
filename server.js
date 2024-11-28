const express = require('express');
const bodyParser = require('body-parser');
const { spawn } = require('child_process');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

const app = express();
app.use(bodyParser.json());

let botProcess = null; // Track the Python bot process

// Endpoint to start the bot
app.post('/start-bot', (req, res) => {
    if (botProcess) {
        return res.status(400).send({ message: 'Bot is already running!' });
    }
    botProcess = spawn('python', ['../bybit_bot/bybit_trading_bot.py']);

    botProcess.stdout.on('data', (data) => {
        console.log(`Bot Output: ${data}`);
    });

    botProcess.stderr.on('data', (data) => {
        console.error(`Bot Error: ${data}`);
    });

    botProcess.on('close', (code) => {
        console.log(`Bot process exited with code ${code}`);
        botProcess = null; // Reset process when it exits
    });

    res.send({ message: 'Bot started successfully!' });
});

// Endpoint to stop the bot
app.post('/stop-bot', (req, res) => {
    if (botProcess) {
        botProcess.kill('SIGINT'); // Gracefully stop the process
        botProcess = null;
        return res.send({ message: 'Bot stopped successfully.' });
    }
    res.status(400).send({ message: 'No bot is currently running.' });
});

// Endpoint to check bot status
app.get('/status', (req, res) => {
    if (botProcess) {
        res.send({ message: 'Bot is running.', pid: botProcess.pid });
    } else {
        res.send({ message: 'Bot is not running.' });
    }
});

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
