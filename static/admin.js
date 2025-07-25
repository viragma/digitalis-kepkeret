// static/admin.js - JAVÍTVA A FÜLES NÉZETHEZ

document.addEventListener('DOMContentLoaded', function() {
    const facesTabButton = document.getElementById('v-pills-faces-tab');
    
    if (facesTabButton) {
        // Zászló, ami jelzi, hogy betöltöttük-e már az arcokat
        let facesLoaded = false;

        // Ha a fül már a betöltéskor aktív, azonnal töltsük be az adatokat
        if (facesTabButton.classList.contains('active')) {
            loadUnknownFaces();
            facesLoaded = true;
        }

        // Figyeljük, hogy a felhasználó mikor kattint erre a fülre
        facesTabButton.addEventListener('show.bs.tab', function () {
            // Csak akkor töltsük be újra, ha még nem tettük meg
            if (!facesLoaded) {
                loadUnknownFaces();
                facesLoaded = true;
            }
        });
    }
});


async function loadUnknownFaces() {
    const container = document.getElementById('unknown-faces-container');
    const template = document.getElementById('face-card-template');
    const loadingSpinner = document.getElementById('loading-spinner');
    const noFacesMessage = document.getElementById('no-unknown-faces');

    // Ha nincs konténer, ne csináljunk semmit
    if (!container) return;

    try {
        const [personsResponse, facesResponse] = await Promise.all([
            fetch('/api/persons'),
            fetch('/api/faces/unknown')
        ]);

        if (!personsResponse.ok || !facesResponse.ok) {
            throw new Error('Hiba a szerverrel való kommunikáció során.');
        }

        const personNames = await personsResponse.json();
        const unknownFaces = await facesResponse.json();
        
        loadingSpinner.style.display = 'none';

        if (unknownFaces.length === 0) {
            noFacesMessage.style.display = 'block';
            return;
        }

        unknownFaces.forEach(face => {
            const cardClone = template.content.cloneNode(true);
            const cardElement = cardClone.querySelector('.card');
            
            // A kép relatív útvonalát használjuk
            cardElement.querySelector('.face-image').src = `/${face.face_path}`;
            
            const select = cardElement.querySelector('.name-select');
            personNames.forEach(name => {
                const option = document.createElement('option');
                option.value = name;
                option.textContent = name;
                select.appendChild(option);
            });

            const saveButton = cardElement.querySelector('.save-button');
            saveButton.addEventListener('click', async () => {
                const selectedName = select.value;
                if (selectedName) {
                    await saveFaceName(face.face_path, selectedName, cardElement);
                }
            });

            container.appendChild(cardClone);
        });

    } catch (error) {
        console.error('Hiba az ismeretlen arcok betöltésekor:', error);
        loadingSpinner.innerHTML = `<p class="text-danger">Hiba történt a betöltés során.</p>`;
    }
}

async function saveFaceName(facePath, newName, cardElement) {
    try {
        const response = await fetch('/api/update_face_name', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                face_path: facePath,
                new_name: newName
            }),
        });

        if (!response.ok) {
            throw new Error('A mentés sikertelen.');
        }

        const result = await response.json();
        if (result.status === 'success') {
            cardElement.parentElement.remove();
            
            const container = document.getElementById('unknown-faces-container');
            if (container.children.length === 0) {
                 document.getElementById('no-unknown-faces').style.display = 'block';
            }
        } else {
            alert(`Hiba: ${result.message}`);
        }
    } catch (error) {
        console.error('Hiba az arc nevének mentésekor:', error);
        alert('Hálózati hiba történt a mentés során.');
    }
}