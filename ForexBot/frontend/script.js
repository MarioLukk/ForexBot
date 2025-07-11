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

            const msg = `Semnal: ${data.signal}\nRSI: ${data.rsi}\nPreț: ${data.latest_price}`;
            alert(msg);
            document.getElementById("output").innerText = msg;

            const trace = {
                x: data.chart.dates,
                open: data.chart.open,
                high: data.chart.high,
                low: data.chart.low,
                close: data.chart.close,
                type: 'candlestick',
                name: pair,
                increasing: { line: { color: 'green' } },
                decreasing: { line: { color: 'red' } }
            };

            const layout = {
                title: `Grafic ${pair} (${interval})`,
                xaxis: { title: 'Dată' },
                yaxis: { title: 'Preț' }
            };

            Plotly.newPlot('chart', [trace], layout);
        })
        .catch(error => {
            console.error("Eroare:", error);
            alert("Ceva n-a mers. Verifică consola.");
        });
}
