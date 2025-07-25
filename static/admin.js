// static/admin.js

document.addEventListener('DOMContentLoaded', function() {
    // Ez a kód csak akkor fut le, ha az admin oldalon a "Faces" fül aktív
    const facesTab = document.getElementById('tab-faces');
    if (facesTab) {
        loadUnknownFaces();
    }
});

async function loadUnknownFaces() {
    const container = document.getElementById('unknown-faces-container');
    const template = document.getElementById('face-card-template');
    const loadingSpinner = document.getElementById('loading-spinner');
    const noFacesMessage = document.getElementById('no-unknown-faces');

    try {
        // 1. Lekérjük a választható neveket és az ismeretlen arcokat párhuzamosan
        const [personsResponse, facesResponse] = await Promise.all([
            fetch('/api/persons'),
            fetch('/api/faces/unknown')
        ]);

        if (!personsResponse.ok || !facesResponse.ok) {
            throw new Error('Hiba a szerverrel való kommunikáció során.');
        }

        const personNames = await personsResponse.json();
        const unknownFaces = await facesResponse.json();
        
        loadingSpinner.style.display = 'none'; // Töltés ikon elrejtése

        if (unknownFaces.length === 0) {
            noFacesMessage.style.display = 'block'; // Üzenet megjelenítése, ha nincs több arc
            return;
        }

        // 2. Minden ismeretlen archoz létrehozunk egy kártyát
        unknownFaces.forEach(face => {
            const cardClone = template.content.cloneNode(true);
            const cardElement = cardClone.querySelector('.card');
            
            // Beállítjuk a kép forrását
            cardElement.querySelector('.face-image').src = `/${face.face_path}`;
            
            // Feltöltjük a dropdown menüt a nevekkel
            const select = cardElement.querySelector('.name-select');
            personNames.forEach(name => {
                const option = document.createElement('option');
                option.value = name;
                option.textContent = name;
                select.appendChild(option);
            });

            // Eseménykezelő a mentés gombra
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
            // Sikeres mentés után eltávolítjuk a kártyát a felületről
            cardElement.parentElement.remove();
            
            // Ellenőrizzük, maradt-e még kártya
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