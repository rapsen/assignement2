
// Load google charts
google.load("visualization", "1", { packages: ["corechart"] });
google.charts.setOnLoadCallback(drawChart);

// Draw the chart and set the chart values
function drawChart() {
    var d = JSON.parse(document.getElementById("percentage").value)

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
