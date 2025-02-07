<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Température en Temps Réel</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; }
        h1 { color: #333; }
        #temp { font-size: 2em; color: red; }
    </style>
</head>
<body>
    <h1>Température en Temps Réel</h1>
    <p>Dernière mesure :</p>
    <p><strong>Température :</strong> <span id="temp">--</span> °C</p>
    <p><strong>Humidité :</strong> <span id="humidity">--</span> %</p>
    <p><strong>Horodatage :</strong> <span id="timestamp">--</span></p>

    <script>
        function updateData() {
            fetch('/data')
                .then(response => response.json())
                .then(data => {
                    if (data.temperature !== "N/A") {
                        document.getElementById('temp').textContent = data.temperature;
                        document.getElementById('humidity').textContent = data.humidity;
                        document.getElementById('timestamp').textContent = data.timestamp;
                    } else {
                        console.log("Aucune donnée disponible.");
                    }
                })
                .catch(error => console.error('Erreur de récupération des données:', error));
        }

        setInterval(updateData, 5000); // Met à jour toutes les 5 secondes
        updateData(); // Mise à jour immédiate au chargement de la page  
    </script>
</body>
</html>