window.addEventListener("load", initNav, false);
window.addEventListener("load", initMessages, false);

function initNav() {
    document.getElementById("nav-open").addEventListener("click", openNav, false);
    document.getElementById("nav-close").addEventListener("click", closeNav, false);
}

function openNav() {
    let nav = document.getElementById("nav");
    nav.classList.add('visible');
    document.getElementById("nav-open").classList.remove("visible");
}

function closeNav() {
    let nav = document.getElementById("nav");
    nav.classList.remove('visible');
    document.getElementById("nav-open").classList.add("visible");
}

function initMessages() {
    let messages = document.getElementsByClassName("messages");
    for (let i = 0; i < messages.length; i++) {
        messages[i].classList.add("disappear");
    }
}