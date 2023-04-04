function toggleTheme() {
    var theme = document.getElementById('head-theme');
    var bouton = document.getElementById('icon-theme');

    if (document.cookie == "theme=dark") document.cookie = "theme=light; path=/; expires=Thu, 18 Dec 9999 12:00:00 UTC";
 
    else document.cookie = "theme=dark;path=/; expires=Thu, 18 Dec 9999 12:00:00 UTC";

    location.reload();
}

document.getElementById("bouton-theme").addEventListener("click", ()=>{toggleTheme()});