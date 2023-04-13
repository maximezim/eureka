function toggleTheme() {
    cookies = document.cookie.split("; ");

    if (cookies[1] == "theme=dark" || cookies[1] == "theme=pink" || cookies[0] == "theme=dark" || cookies[0] == "theme=pink") document.cookie = "theme=light; path=/; expires=Thu, 18 Dec 9999 12:00:00 UTC";
    else document.cookie = "theme=dark; path=/; expires=Thu, 18 Dec 9999 12:00:00 UTC";

    console.log(document.cookie);

    location.reload();
}

function closePopUp() {
    document.cookie = "avertissement=false; path=/; expires=Thu, 18 Dec 9999 12:00:00 UTC";
    document.getElementById("avertissement").classList.add("avertissement_hidden");
}

document.getElementById("bouton-theme").addEventListener("click", ()=>{toggleTheme()});

document.getElementById("bouton-ferme").addEventListener("click", ()=>{closePopUp()});