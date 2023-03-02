function uploadText() {
    var fichier = document.querySelector('input[type=file]');
    var msgFichier = document.querySelector('.msgFichier');

    while(msgFichier.firstChild) {
        msgFichier.removeChild(msgFichier.firstChild);
      }
    
    var file = fichier.files[0];
    
    if(file === null) {
        var para = document.createElement('p');
        para.textContent = 'Aucun fichier sélectionné';
        msgFichier.appendChild(para);
    } 
    
    else {
        var para = document.createElement('p');
        para.textContent = 'Fichier : ' + file.name;
        msgFichier.appendChild(para);
    }
}

document.getElementById('fichier').addEventListener('change', ()=> uploadText());