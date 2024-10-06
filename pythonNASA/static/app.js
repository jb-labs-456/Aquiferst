function fetchSensorData() {
    fetch('/sensor-data')
        .then(response => response.json())
        .then(data => {
            // Update the score
            document.getElementById('score').textContent = data.score.toFixed(2);
            
            // Clear the current suggestions
            const suggestionsList = document.getElementById('suggestions');
            suggestionsList.innerHTML = '';
            
            // Display recommendations from the Python output
            data.suggestions.forEach(suggestion => {
                const listItem = document.createElement('li');
                listItem.textContent = suggestion;
                suggestionsList.appendChild(listItem);
            });
        })
        .catch(error => {
            console.error('Error fetching sensor data:', error);
        });
}

// Fetch data every 5 minutes (300,000 ms)
setInterval(fetchSensorData, 300000);

// Initial fetch on page load
window.onload = fetchSensorData;
