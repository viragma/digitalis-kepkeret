// static/faces_manager.js

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

    if (!container || !template) return;

    try {
        const [personsResponse, facesResponse] = await Promise.all([
            fetch('/api/persons'),
            fetch('/api/faces/unknown')
        ]);

        if (!personsResponse.ok || !facesResponse.ok) throw new Error('Hiba a szerverrel való kommunikáció során.');

        const personNames = await personsResponse.json();
        const unknownFaces = await facesResponse.json();
        
        loadingSpinner.style.display = 'none';
        if (unknownFaces.length === 0) {
            noFacesMessage.style.display = 'block';
            return;
        }
        
        batchActionsPanel.style.display = 'block';

        batchNameSelect.innerHTML = '<option selected disabled>Válassz egy nevet...</option>';
        personNames.forEach(name => {
            const option = document.createElement('option');
            option.value = name;
            option.textContent = name;
            batchNameSelect.appendChild(option);
        });

        container.innerHTML = '';
        unknownFaces.forEach(face => {
            const cardClone = template.content.cloneNode(true);
            const cardElement = cardClone.querySelector('.face-card');
            
            cardElement.dataset.facePath = face.face_path;
            cardElement.querySelector('.face-image').src = `/${face.face_path}`;
            
            cardElement.addEventListener('click', (event) => {
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
                event.stopPropagation();
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
        if (selectedName === 'Válassz egy nevet...') {
            showToast('Kérlek, válassz egy nevet a tömeges mentéshez!', 'warning');
            return;
        }

        const selectedCards = document.querySelectorAll('.face-card.selected');
        if (selectedCards.length === 0) {
            showToast('Nincs kijelölt arc a mentéshez!', 'warning');
            return;
        }

        const updates = Array.from(selectedCards).map(card => ({
            face_path: card.dataset.facePath,
            new_name: selectedName
        }));

        try {
            const response = await fetch('/api/update_faces_batch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updates),
            });

            if (!response.ok) throw new Error('A szerver hibát adott.');
            
            const result = await response.json();
            if (result.status === 'success') {
                showToast(result.message);
                selectedCards.forEach(card => {
                    card.parentElement.style.transition = 'opacity 0.5s ease';
                    card.parentElement.style.opacity = '0';
                    setTimeout(() => card.parentElement.remove(), 500);
                });
            } else {
                showToast(result.message, 'danger');
            }
        } catch (error) {
            console.error('Hiba a tömeges mentés során:', error);
            showToast('Hálózati hiba történt a mentés során.', 'danger');
        }
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
                if (document.getElementById('unknown-faces-container').children.length === 0) {
                    document.getElementById('no-unknown-faces').style.display = 'block';
                    document.getElementById('batch-actions-panel').style.display = 'none';
                }
            }, 500);
        } else {
            showToast(`Hiba: ${result.message}`, 'danger');
        }
    } catch (error) {
        console.error('Hiba az arc nevének mentésekor:', error);
        showToast('Hálózati hiba történt a mentés során.', 'danger');
    }
}