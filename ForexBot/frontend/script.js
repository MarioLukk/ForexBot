function getSignal() {
    console.log("Butonul a fost apăsat ✅");

    const pair = document.getElementById("pair").value.toUpperCase();
    const interval = document.getElementById("interval").value;
    const period = document.getElementById("period").value;

    fetch(`http://localhost:5000/api/signal?pair=${pair}&interval=${interval}&period=${period}`)
        .then(response => {
            if (!response.ok) {
                throw new Error("Răspuns invalid de la server.");
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                alert("Eroare: " + data.error);
                return;
            }

            const chart = data.chart;
            const rsiSignalText = chart.signal || "N/A";
            const latestRsi = chart.latest_rsi !== undefined ? chart.latest_rsi.toFixed(2) : "N/A";
            const latestPrice = chart.latest_price !== undefined ? chart.latest_price.toFixed(4) : "N/A";

            const rsiSignalDiv = document.getElementById("rsi-signal");
            rsiSignalDiv.innerText = `Semnal RSI: ${rsiSignalText} (RSI: ${latestRsi}, Preț: ${latestPrice})`;

            const trace = {
                x: chart.dates,
                open: chart.open,
                high: chart.high,
                low: chart.low,
                close: chart.close,
                type: 'candlestick',
                name: pair,
                increasing: { line: { color: 'green' } },
                decreasing: { line: { color: 'red' } }
            };

            const layout = {
                title: `Grafic ${pair} (${interval})`,
                xaxis: { title: 'Dată' },
                yaxis: { title: 'Preț' },
                plot_bgcolor: '#ffffff',
                paper_bgcolor: '#ffffff'
            };

            Plotly.newPlot('chart', [trace], layout);
        })
        .catch(error => {
            console.error("Eroare:", error);
            alert("Ceva n-a mers. Verifică consola.");
        });
}
