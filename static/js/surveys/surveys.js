window.addEventListener("load", initSurvey, false);

function initSurvey() {
    addBackGrounds();
}

function submitAndGoToPrevious(page) {
    submitAndGoTo(parseInt(page) - 1)
}

function submitAndGoTo(page) {
    let form = document.getElementsByClassName("survey")[0];
    let input = document.createElement("input");
    input.name = "next_page";
    input.value = (page).toString();
    input.type = "hidden";
    form.appendChild(input);
}

function addBackGrounds() {
    let inputs = document.querySelectorAll("input[type=range]");
    for (let i = 0; i < inputs.length; i++) {
        inputs[i].addEventListener("input", changeBackGroundWEvent, false);
        changeBackGround(inputs[i]);
    }
}

function changeBackGroundWEvent(event) {
    changeBackGround(event.target);
}

function changeBackGround(slider) {
    let value = slider.value;
    let percentage = (value - slider.min) / (slider.max - slider.min);
    let color = "rgb(" + Math.round(255 - 255 * percentage) + "," + Math.round(255 * percentage) + ",20)";
    let left = slider.parentElement.childNodes[3];
    let right = slider.parentElement.childNodes[5];
    if (value > slider.max - (slider.max - slider.min) / 2) {
        left.style.width = "0";
        let w = value / slider.max * 50 * .96;
        right.style.width = w + "%";
    } else {
        right.style.width = "0";
        let w = Math.abs(value / slider.max * 50 * .96);
        left.style.width = w + "%";
    }
    right.style.backgroundColor = color;
    left.style.backgroundColor = color;
}
