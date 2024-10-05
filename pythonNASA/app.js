const express = require('express');
const path = require('path');
const { exec } = require('child_process');

const app = express();
const port = 3000;

// Serve static files (CSS, client-side JS)
app.use('/static', express.static(path.join(__dirname, 'static')));

// Serve the index.html file
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Run Python script and fetch sensor data for the /sensor-data route
app.get('/sensor-data', (req, res) => {
    exec('python -u "c:\\Users\\miaaz\\OneDrive\\Desktop\\pythonNASA\\soil_health.py"', (error, stdout, stderr) => {
        if (error) {
            console.error(`Error executing Python script: ${error}`);
            return res.status(500).json({ error: 'Failed to get sensor data' });
        }

        // Combine stdout and stderr to capture all output
        const output = stdout + stderr;
        console.log("Python Script Output:\n", output);

        const outputLines = output.split('\n').filter(line => line);  // Remove empty lines

        // Find the line with the Soil Health Score
        const scoreLine = outputLines.find(line => line.includes('Soil Health Score'));

        if (!scoreLine) {
            return res.status(500).json({ error: 'Could not find the soil health score in the output' });
        }

        // Extract the score using a regular expression to ensure we get the correct part
        const scoreMatch = scoreLine.match(/Soil Health Score:\s*([0-9.]+)/);
        const score = scoreMatch ? parseFloat(scoreMatch[1]) : NaN;

        console.log("Score Line:", scoreLine);
        console.log("Extracted Score:", score);

        if (isNaN(score)) {
            return res.status(500).json({ error: 'Failed to extract valid soil health score' });
        }

        // Extract recommendations (find lines starting with "Recommendations to improve soil health:")
        const recommendationsIndex = outputLines.findIndex(line => line.includes("Recommendations to improve soil health:"));
        const recommendations = outputLines.slice(recommendationsIndex + 1);

        const formattedRecommendations = recommendations.map(rec => rec.trim());

        const sensorData = {
            score: score,
            suggestions: formattedRecommendations
        };

        // Send the data as JSON response
        res.json(sensorData);
    });
});

// Start the server
app.listen(port, () => {
    console.log(`Server is running at http://localhost:${port}`);
});
