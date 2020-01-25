window.addEventListener("load", stats, false);

function stats() {
    let stats = document.getElementsByClassName("statistics");
    for (let i = 0; i < stats.length; i++) {
        setBackgroundsStats(stats[i]);
    }
}

function setBackgroundsStats(stats) {
    let statDivs = stats.querySelectorAll(".statistics > div");
    for (let i = 0; i < statDivs.length; i++) {
        let s = statDivs[i];
        let avg = parseInt(s.querySelectorAll("p")[0].innerHTML);
        // let percentage = (avg + parseInt({{max}})) / (parseInt({{ max }}) - parseInt({{ min }}));
        let percentage = (avg + 50) / (100);
        let color = "rgb(" + Math.round(255 - 255 * percentage) + "," + Math.round(255 * percentage) + ",20)";
        s.style.backgroundColor = color;
    }
}