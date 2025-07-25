// static/admin.js - TELJES, VÉGLEGES KÓD

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

/**
 * Megjelenít egy Bootstrap Toast értesítést.
 * @param {string} message Az üzenet szövege.
 * @param {string} category A Bootstrap színkategória (success, warning, danger, stb.).
 */
function showToast(message, category = 'success') {
    const toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) return;

    const toastHTML = `
        <div class="toast align-items-center text-bg-${category} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>`;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    const newToastEl = toastContainer.lastElementChild;
    const newToast = new bootstrap.Toast(newToastEl, { delay: 3000 });
    newToast.show();
    
    newToastEl.addEventListener('hidden.bs.toast', () => {
        newToastEl.remove();
    });
}

/**
 * Betölti az ismeretlen arcokat az API-ról és megjeleníti őket.
 */
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
        
        batchActionsPanel.style.display = 'block';

        // Dropdown menük feltöltése
        batchNameSelect.innerHTML = '<option selected disabled>Válassz egy nevet...</option>'; // Alaphelyzetbe állítás
        personNames.forEach(name => {
            const option = document.createElement('option');
            option.value = name;
            option.textContent = name;
            batchNameSelect.appendChild(option);
        });

        // Arckártyák létrehozása
        container.innerHTML = ''; // Konténer kiürítése
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

/**
 * Beállítja a tömeges műveletek gombjainak eseményfigyelőit.
 */
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

        const savePromises = Array.from(selectedCards).map(card => {
            return saveFaceName(card.dataset.facePath, selectedName, card);
        });
        
        await Promise.all(savePromises);
        showToast(`${selectedCards.length} arc sikeresen mentve!`);
    });
}

/**
 * Elmenti egy arc új nevét az API-n keresztül.
 * @param {string} facePath Az arc fájljának útvonala.
 * @param {string} newName A személy új neve.
 * @param {HTMLElement} cardElement A kártya HTML eleme a felületen.
 */
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
            showToast(`Hiba: ${result.message}`, 'danger');
        }
    } catch (error) {
        console.error('Hiba az arc nevének mentésekor:', error);
        showToast('Hálózati hiba történt a mentés során.', 'danger');
    }
}