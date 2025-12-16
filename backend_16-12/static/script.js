function loadData() {
    fetch("/api/measurements")
        .then(res => res.json())
        .then(data => {
            document.getElementById("dbValue").innerText = data.db;
            document.getElementById("hzValue").innerText = data.hz;
        });
}

function activateMotor(id) {
    fetch(`/api/motor/${id}/activate`, { method: "POST" })
        .then(res => res.json())
        .then(data => {
            alert("Motor " + id + " aktiveret!");
        });
}
