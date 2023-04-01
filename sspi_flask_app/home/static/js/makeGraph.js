console.log("makeGraph.js loaded with chart.js version: " + Chart.version);
const ctx = document.getElementById('myChart');
const BarChart = new Chart(ctx, {});

async function makeBarChart(IndicatorCode){
    await fetch('/api/v1/query/' + IndicatorCode)
        .then((response) => response.json())
        .then((indicator_data) => console.log(indicator_data))
        .finally((indicator_data) => updateBarChart(indicator_data))
    }

function updateBarChart(indicator_data) {
    BarChart.data = {
            labels: indicator_data.map((observation) => (observation["Country"])),
            datasets: [{
            label: indicator_data[0]["IndicatorNameShort"],
            data: indicator_data.map((observation) => (observation["SCORE"])),
            borderWidth: 1
            }]
        }  
    BarChart.options = {
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true
                    }
                }]
            }
        }
    BarChart.update();
}