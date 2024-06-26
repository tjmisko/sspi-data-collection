raw=false

async function makeBarChart(BarChart, IndicatorCode){
    let response = await fetch('/api/v1/query/sspi_clean_api_data?IndicatorCode=' + IndicatorCode)
    let indicator_data = await response.json()
    indicator_data.sort((a, b) => b.RANK - a.RANK)
    console.log(indicator_data)
    let y_axis = raw ? getRaw(indicator_data) : getScores(indicator_data)
    BarChart.data = {
        labels: getCountries(indicator_data),
        datasets: [{
            datacode: IndicatorCode,
            label: indicator_data[0].IndicatorNameShort,
            data: y_axis,
            backgroundColor: 'rgb(255, 99, 132)',
            borderColor: 'rgb(255, 99, 132)',
            borderWidth: 1
        }]
    }

    BarChart.options = {
        elements: {
            bar: {
              borderWidth: 2,
            }
        },
        scaleShowValues: true,
        layout: {padding : 10},
        responsive: true,
        plugins: {
            legend: {
                display: false,
            }
        },
        maintainAspectRatio: false,
        scales: {
          xAxes: [{
            id: 'x',
            type: 'category',
            title: {
                display: true,
                text: 'Country'
            },
            ticks: {
              autoskip: true,
            }
          }]
        }
    }
    BarChart.update();
}


function toggleRaw() {
    raw = !raw
    try {
        IndicatorCode = BarChart.data.datasets[0].datacode
        makeBarChart(IndicatorCode);
    } catch (TypeError) {
        console.log("No Chart Loaded!\n", TypeError)
        IndicatorCode = null;
    }
}


function getCountries(indicator_data) {
    return indicator_data.map(data => data.Country)
}

function getScores(indicator_data) {
    return indicator_data.map(data => data.SCORE)
}

function getRaw(indicator_data) {
    return indicator_data.map(data => data.RAW)
}
