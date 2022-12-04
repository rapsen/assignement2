
// Load google charts
google.load("visualization", "1", { packages: ["corechart"] });
google.charts.setOnLoadCallback(drawChart);

// Draw the chart and set the chart values
function drawChart() {

    var d = JSON.parse(document.getElementById("efficiency").value)

    console.log(Object.entries(d).length)

    var data = new google.visualization.DataTable();
    data.addColumn('string', 'State');
    data.addColumn('number', 'Percentage');
    for (let [key, value] of Object.entries(d)) {
        data.addRow([key, value]);
    }
    
    // Display the chart"
    var chart = new google.visualization.PieChart(document.getElementById('piechart'));
    chart.draw(data, {height: 400});

}

$(document).ready()
{
    document.getElementById('start').value = time();
    document.getElementById('end').value = time()
}

function time() {
    let time = new Date();
    time.setHours(time.getHours() + 2) // Adapt to GMT+2 time
    return time.toISOString().slice(0, 16);
}

function change() {
    document.getElementById("id").value = document.getElementById("select").value
    console.log(document.getElementById("id").value)
}