function toggleTheme() {
    var theme = document.getElementById('head-theme');

    if (theme.getAttribute('href') == "{{ url_for('static',filename='css/style.css')}}") {
        theme.setAttribute('href', "{{ url_for('static',filename='css/style-sombre.css')}}");
    } else {
        theme.setAttribute('href', "{{ url_for('static',filename='css/style.css')}}");
    }
}

document.getElementById('bouton-theme').addEventListener('change', ()=> toggleTheme());