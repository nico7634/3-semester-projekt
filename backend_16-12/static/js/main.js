let dbChart;
let hzChart;

async function loadData() {
    const response = await fetch("/api/data");
    const data = await response.json();

    const dbValues = data.map(x => x.dB);
    const hzValues = data.map(x => x.Hz);

    const labels = data.map((_, i) => "Måling " + i);

    if (!dbChart) {
        dbChart = new Chart(document.getElementById("dbChart"), {
            type: "line",
            data: {
                labels: labels,
                datasets: [{
                    label: "dB",
                    data: dbValues,
                    borderColor: "orange"
                }]
            }
        });
    } else {
        dbChart.data.labels = labels;
        dbChart.data.datasets[0].data = dbValues;
        dbChart.update();
    }

    if (!hzChart) {
        hzChart = new Chart(document.getElementById("hzChart"), {
            type: "line",
            data: {
                labels: labels,
                datasets: [{
                    label: "Hz",
                    data: hzValues,
                    borderColor: "cyan"
                }]
            }
        });
    } else {
        hzChart.data.labels = labels;
        hzChart.data.datasets[0].data = hzValues;
        hzChart.update();
    }
}

setInterval(loadData, 2000);


function startServo() {
    fetch("/api/servo/start", { method: "POST" });
}

function startStepper() {
    fetch("/api/stepper/start", { method: "POST" });
}
