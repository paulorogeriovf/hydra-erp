// Hydra ERP
// Responsável por: controlar interações visuais gerais da interface.

function toggleSidebar() {

    document
        .getElementById("sidebar")
        .classList
        .toggle("open");

    document
        .getElementById("overlay")
        .classList
        .toggle("show");
}


function closeSidebar() {

    document
        .getElementById("sidebar")
        .classList
        .remove("open");

    document
        .getElementById("overlay")
        .classList
        .remove("show");
}