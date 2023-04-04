function toggleEasterEgg() {
    document.cookie = "theme=pink; path=/; expires=Thu, 18 Dec 9999 12:00:00 UTC";

    location.reload();
}

document.getElementById("about-barre").addEventListener("click", ()=>{toggleEasterEgg()});