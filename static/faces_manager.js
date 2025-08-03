// static/faces_manager.js

document.addEventListener('DOMContentLoaded', () => {
    const facesTabButton = document.getElementById('v-pills-faces-tab');
    if (!facesTabButton) return;

    let isInitialized = false;
    let allPersonNames = [];
    let selectedFaces = new Set();

    // DOM Elemek (pontos ID-kkal)
    const grid = document.getElementById('unknown-faces-grid');
    const loadingSpinner = document.getElementById('loading-spinner');
    const noUnknownFacesMsg = document.getElementById('no-unknown-faces');
    const actionsPanel = document.getElementById('batch-actions-panel');
    const selectionCounter = document.getElementById('selection-counter-unknown');
    const batchReassignSelect = document.getElementById('batch-reassign-select-unknown');
    const batchDeleteBtn = document.getElementById('batch-delete-btn-unknown');
    const batchReassignBtn = document.getElementById('batch-reassign-btn-unknown');

    async function loadUnknownFaces() {
        if (!grid || !loadingSpinner || !noUnknownFacesMsg) {
            console.error("Ismeretlen arcok: Hiányzó HTML elemek!");
            return;
        }
        loadingSpinner.classList.remove('d-none');
        grid.innerHTML = '';
        actionsPanel.classList.add('d-none');
        selectedFaces.clear();

        try {
            const [facesRes, personsRes] = await Promise.all([
                fetch('/api/faces/unknown'),
                fetch('/api/persons')
            ]);

            if (!facesRes.ok) throw new Error(`Hiba az ismeretlen arcok lekérdezésekor. Státusz: ${facesRes.status}`);
            if (!personsRes.ok) throw new Error('Hiba a személyek lekérdezésekor.');

            const faces = await facesRes.json();
            allPersonNames = await personsRes.json();
            
            updatePersonsDropdown(allPersonNames);

            if (faces.length === 0) {
                noUnknownFacesMsg.classList.remove('d-none');
            } else {
                noUnknownFacesMsg.classList.add('d-none');
                const template = document.getElementById('face-card-template-unknown');
                faces.forEach(face => {
                    const cardClone = template.content.cloneNode(true);
                    const card = cardClone.querySelector('.face-card');
                    const img = card.querySelector('img');

                    if (face.face_path) {
                        img.src = face.face_path;
                        card.dataset.facePath = face.face_path;
                    } else {
                        img.src = "https://via.placeholder.com/150/dc3545/FFFFFF?text=HIBA";
                    }
                    
                    card.addEventListener('click', () => {
                        card.classList.toggle('selected');
                        if (card.classList.contains('selected')) {
                            selectedFaces.add(face.face_path);
                        } else {
                            selectedFaces.delete(face.face_path);
                        }
                        updateActionsBar();
                    });

                    grid.appendChild(cardClone);
                });
            }
        } catch (error) {
            console.error("Hiba az ismeretlen arcok betöltésekor:", error);
            grid.innerHTML = `<p class="text-danger">Hiba történt a betöltés közben: ${error.message}</p>`;
        } finally {
            loadingSpinner.classList.add('d-none');
        }
    }
    
    function updatePersonsDropdown(names) {
        if (!batchReassignSelect) return;
        batchReassignSelect.innerHTML = '<option selected disabled>Válassz új nevet...</option>';
        names.sort().forEach(name => {
            const option = document.createElement('option');
            option.value = name;
            option.textContent = name;
            batchReassignSelect.appendChild(option);
        });
    }

    function updateActionsBar() {
        if (!actionsPanel || !selectionCounter) return;
        actionsPanel.classList.toggle('d-none', selectedFaces.size === 0);
        selectionCounter.textContent = `${selectedFaces.size} arc kijelölve`;
    }

    async function batchReassign() {
        const targetName = batchReassignSelect.value;
        if (targetName === 'Válassz új nevet...' || selectedFaces.size === 0) return;
        
        const response = await fetch('/api/faces/reassign_batch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ face_paths: Array.from(selectedFaces), target_name: targetName })
        });
        const result = await response.json();
        if (result.status === 'success') {
            showToast(result.message);
            loadUnknownFaces();
        } else {
            showToast(result.message, 'danger');
        }
    }

    async function batchDelete() {
        if (selectedFaces.size === 0 || !confirm(`Biztosan törlöd a kijelölt ${selectedFaces.size} arcot? Ez a művelet nem vonható vissza.`)) return;

        const response = await fetch('/api/faces/delete_batch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ face_paths: Array.from(selectedFaces) })
        });
        const result = await response.json();
        if (result.status === 'success') {
            showToast(result.message);
            loadUnknownFaces();
        } else {
            showToast(result.message, 'danger');
        }
    }

    const init = () => {
        if (isInitialized) return;
        isInitialized = true;
        loadUnknownFaces();

        if (batchDeleteBtn && batchReassignBtn) {
            batchDeleteBtn.addEventListener('click', batchDelete);
            batchReassignBtn.addEventListener('click', batchReassign);
        } else {
            console.error("Hiányzó tömeges műveleti gombok!");
        }
    };
    
    if (facesTabButton.classList.contains('active')) {
        init();
    }
    facesTabButton.addEventListener('shown.bs.tab', init);
});