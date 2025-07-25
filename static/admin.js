// static/admin.js - FRISSÍTVE A KATTINTÁSOS KIJELÖLÉSHEZ

document.addEventListener('DOMContentLoaded', function() {
    // ... (ez a rész változatlan)
});

async function loadUnknownFaces() {
    // ... (a függvény eleje változatlan)
    
    // Arckártyák létrehozása
    unknownFaces.forEach(face => {
        const cardClone = template.content.cloneNode(true);
        const cardElement = cardClone.querySelector('.face-card');
        
        cardElement.dataset.facePath = face.face_path;
        cardElement.querySelector('.face-image').src = `/${face.face_path}`;
        
        // KATTINTÁS ESEMÉNY: Kijelölés váltása a kártyán
        cardElement.addEventListener('click', (event) => {
            // Megakadályozzuk, hogy a kártya is kijelölődjön, ha a dropdown-ra vagy gombra kattintunk
            if (event.target.tagName !== 'SELECT' && event.target.tagName !== 'BUTTON') {
                cardElement.classList.toggle('selected');
            }
        });
        
        const select = cardElement.querySelector('.name-select');
        personNames.forEach(name => {
            const option = document.createElement('option');
            option.value = name;
            option.textContent = name;
            select.appendChild(option);
        });

        cardElement.querySelector('.save-button').addEventListener('click', async (event) => {
            event.stopPropagation(); // Megállítjuk az esemény továbbterjedését
            await saveFaceName(face.face_path, select.value, cardElement);
        });

        container.appendChild(cardClone);
    });

    setupBatchActions(); // Tömeges műveletek beállítása
}

function setupBatchActions() {
    const selectAllBtn = document.getElementById('select-all-button');
    const deselectAllBtn = document.getElementById('deselect-all-button');
    const batchSaveBtn = document.getElementById('batch-save-button');
    const batchNameSelect = document.getElementById('batch-name-select');
    
    selectAllBtn.addEventListener('click', () => {
        document.querySelectorAll('.face-card').forEach(card => card.classList.add('selected'));
    });

    deselectAllBtn.addEventListener('click', () => {
        document.querySelectorAll('.face-card').forEach(card => card.classList.remove('selected'));
    });

    batchSaveBtn.addEventListener('click', async () => {
        const selectedName = batchNameSelect.value;
        if (selectedName === 'Válassz egy nevet...') { /* ... */ return; }

        const selectedCards = document.querySelectorAll('.face-card.selected');
        if (selectedCards.length === 0) { /* ... */ return; }

        const savePromises = Array.from(selectedCards).map(card => {
            return saveFaceName(card.dataset.facePath, selectedName, card);
        });
        await Promise.all(savePromises);
        alert(`${selectedCards.length} arc sikeresen mentve!`);
    });
}

// saveFaceName funkció változatlan...
async function saveFaceName(facePath, newName, cardElement) {
    // ...
}