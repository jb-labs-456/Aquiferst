const express = require('express');
const path = require('path');
const { exec } = require('child_process');

const app = express();
const port = 100;

// Store sensor data globally so it can be returned quickly
let cachedSensorData = {
    score: null,
    suggestions: [],
    lastUpdated: null
};

// Function to run the Python script and update cached data
function updateSensorData() {
    exec('python -u "c:\\Users\\miaaz\\OneDrive\\Desktop\\pythonNASA\\soil_health.py"', (error, stdout, stderr) => {
        if (error) {
            console.error(`Error executing Python script: ${error}`);
            return;
        }

        // Combine stdout and stderr to capture all output
        const output = stdout + stderr;
        console.log("Python Script Output:\n", output);

        const outputLines = output.split('\n').filter(line => line);  // Remove empty lines

        // Find the line with the Soil Health Score
        const scoreLine = outputLines.find(line => line.includes('Soil Health Score'));

        if (!scoreLine) {
            console.error('Could not find the soil health score in the output');
            return;
        }

        // Extract the score using a regular expression
        const scoreMatch = scoreLine.match(/Soil Health Score:\s*([0-9.]+)/);
        const score = scoreMatch ? parseFloat(scoreMatch[1]) : NaN;

        console.log("Score Line:", scoreLine);
        console.log("Extracted Score:", score);

        if (isNaN(score)) {
            console.error('Failed to extract valid soil health score');
            return;
        }

        // Extract recommendations (find lines starting with "Recommendations to improve soil health:")
        const recommendationsIndex = outputLines.findIndex(line => line.includes("Recommendations to improve soil health:"));
        const recommendations = outputLines.slice(recommendationsIndex + 1);

        const formattedRecommendations = recommendations.map(rec => rec.trim());

        // Update the cached sensor data
        cachedSensorData = {
            score: score,
            suggestions: formattedRecommendations,
            lastUpdated: new Date().toISOString() // Store last update time
        };

        console.log('Updated sensor data:', cachedSensorData);
    });
}

// Schedule the Python script to run every 10 seconds
setInterval(updateSensorData, 10000);

// Serve static files (CSS, client-side JS)
app.use('/static', express.static(path.join(__dirname, 'static')));

// Serve the index.html file
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Route to fetch the latest sensor data
app.get('/sensor-data', (req, res) => {
    if (cachedSensorData.lastUpdated) {
        res.json(cachedSensorData);
    } else {
        res.status(503).json({ error: 'Sensor data not yet available. Please try again later.' });
    }
});

// Start the server
app.listen(port, () => {
    console.log(`Server is running at http://localhost:${port}`);
});

// Run the script once at the start to initialize the data
updateSensorData();
