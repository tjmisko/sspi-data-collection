console.log("makeGraph.js loaded with chart.js version: " + Chart.version);
const ctx = document.getElementById('myChart');

async function makeBarChart(IndicatorCode){
    await fetch('/api/v1/query/' + IndicatorCode)
        .then((response) => response.json())
        .then((indicator_data) => 
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: indicator_data.map((observation) => (observation["Country"])),
                    datasets: [{
                    label: indicator_data[0]["IndicatorNameShort"],
                    data: indicator_data.map((observation) => (observation["SCORE"])),
                    borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                    y: {
                        beginAtZero: true
                    }
                    }
                }
            })).update();
    }