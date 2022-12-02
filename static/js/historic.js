function now() {
    var today = new Date();
    var date = today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate();
    var time = today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds();

    return date+'T'+time;
}

document.getElementById("start").value = now();

document.getElementById("start").max = now();

function print() {
    console.log(document.getElementById('start').value);  
    console.log(document.getElementById('end').value);  

};

// 2022-12-21T11%3A11