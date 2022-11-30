const sse = new EventSource('/sse');

const status = document.getElementById("status");
sse.addEventListener("click", update);


function update() {
    console.log(element.src);
  }
