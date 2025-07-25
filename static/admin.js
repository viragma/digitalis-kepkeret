// static/admin.js - BŐVÍTVE TÖMEGES MŰVELETEKKEL

document.addEventListener('DOMContentLoaded', function() {
    const facesTabButton = document.getElementById('v-pills-faces-tab');
    if (facesTabButton) {
        let facesLoaded = false;
        if (facesTabButton.classList.contains('active')) {
            loadUnknownFaces();
            facesLoaded = true;
        }
        facesTabButton.addEventListener('show.bs.tab', function () {
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
    const batchActionsPanel = document.getElementById('batch-actions-panel');
    const batchNameSelect = document.getElementById('batch-name-select');

    try {
        const [personsResponse, facesResponse] = await Promise.all([
            fetch('/api/persons'),
            fetch('/api/faces/unknown')
        ]);
        const personNames = await personsResponse.json();
        const unknownFaces = await facesResponse.json();
        
        loadingSpinner.style.display = 'none';

        if (unknownFaces.length === 0) {
            noFacesMessage.style.display = 'block';
            return;
        }
        
        batchActionsPanel.style.display = 'block'; // Tömeges panel mutatása

        // Tömeges és egyedi dropdown menük feltöltése
        personNames.forEach(name => {
            const option = document.createElement('option');
            option.value = name;
            option.textContent = name;
            batchNameSelect.appendChild(option.cloneNode(true));
        });

        unknownFaces.forEach(face => {
            const cardClone = template.content.cloneNode(true);
            const cardElement = cardClone.querySelector('.card');
            const cardCheckbox = cardClone.querySelector('.card-checkbox');
            
            cardElement.dataset.facePath = face.face_path; // Adatként tároljuk az útvonalat
            cardCheckbox.value = face.face_path;
            cardElement.querySelector('.face-image').src = `/${face.face_path}`;
            
            const select = cardElement.querySelector('.name-select');
            personNames.forEach(name => {
                const option = document.createElement('option');
                option.value = name;
                option.textContent = name;
                select.appendChild(option);
            });

            // Egyedi mentés gomb
            cardElement.querySelector('.save-button').addEventListener('click', async () => {
                await saveFaceName(face.face_path, select.value, cardElement);
            });

            container.appendChild(cardClone);
        });

        setupBatchActions();

    } catch (error) {
        console.error('Hiba az ismeretlen arcok betöltésekor:', error);
        loadingSpinner.innerHTML = `<p class="text-danger">Hiba történt a betöltés során.</p>`;
    }
}

function setupBatchActions() {
    const selectAllCheckbox = document.getElementById('select-all-checkbox');
    const batchSaveButton = document.getElementById('batch-save-button');
    const batchNameSelect = document.getElementById('batch-name-select');
    const allCardCheckboxes = document.querySelectorAll('.card-checkbox');

    // "Összes kijelölése" logika
    selectAllCheckbox.addEventListener('change', () => {
        allCardCheckboxes.forEach(checkbox => {
            checkbox.checked = selectAllCheckbox.checked;
        });
    });

    // Tömeges mentés logika
    batchSaveButton.addEventListener('click', async () => {
        const selectedName = batchNameSelect.value;
        if (selectedName === 'Válassz egy nevet...') {
            alert('Kérlek, válassz egy nevet a tömeges mentéshez!');
            return;
        }

        const checkedBoxes = document.querySelectorAll('.card-checkbox:checked');
        if (checkedBoxes.length === 0) {
            alert('Nincs kijelölt arc a mentéshez!');
            return;
        }

        // Párhuzamosan mentjük az összes kijelölt arcot
        const savePromises = Array.from(checkedBoxes).map(box => {
            const card = box.closest('.card');
            return saveFaceName(card.dataset.facePath, selectedName, card);
        });

        await Promise.all(savePromises);
        alert(`${checkedBoxes.length} arc sikeresen mentve!`);
    });
}


async function saveFaceName(facePath, newName, cardElement) {
    try {
        const response = await fetch('/api/update_face_name', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ face_path: facePath, new_name: newName }),
        });

        if (!response.ok) throw new Error('A mentés sikertelen.');

        const result = await response.json();
        if (result.status === 'success') {
            cardElement.parentElement.style.transition = 'opacity 0.5s ease';
            cardElement.parentElement.style.opacity = '0';
            setTimeout(() => {
                cardElement.parentElement.remove();
                if (document.getElementById('unknown-faces-container').children.length === 0) {
                    document.getElementById('no-unknown-faces').style.display = 'block';
                    document.getElementById('batch-actions-panel').style.display = 'none';
                }
            }, 500);
        } else {
            alert(`Hiba: ${result.message}`);
        }
    } catch (error) {
        console.error('Hiba az arc nevének mentésekor:', error);
        alert('Hálózati hiba történt a mentés során.');
    }
}