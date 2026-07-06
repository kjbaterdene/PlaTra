function updateAircraft() {
  fetch("/data")
    .then(response => response.json())
    .then(data => {
      document.getElementById("aircraft-list").innerHTML = JSON.stringify(data);
    });
}

updateAircraft();
setInterval(updateAircraft, 10000);