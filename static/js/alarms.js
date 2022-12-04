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