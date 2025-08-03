// static/known_faces.js

document.addEventListener('DOMContentLoaded', () => {
    const knownFacesTabButton = document.getElementById('v-pills-known-faces-tab');
    if (!knownFacesTabButton) return;

    let isInitialized = false;
    let currentPage = 1;
    let currentPerson = '';
    let totalFaces = 0;
    let allPersonNames = [];
    const FACES_PER_PAGE = 30;

    const grid = document.getElementById('person-selector-grid');
    const gallerySection = document.getElementById('person-gallery-section');
    const galleryTitle = document.getElementById('gallery-title');
    const galleryContainer = document.getElementById('gallery-container');
    const loadMoreBtn = document.getElementById('load-more-btn');
    const backBtn = document.getElementById('back-to-grid-btn');
    const actionsBar = document.getElementById('face-actions-bar');
    const selectionCounter = document.getElementById('face-selection-counter');
    const reassignSelect = document.getElementById('batch-reassign-select');
    const batchDeleteBtn = document.getElementById('batch-delete-btn');
    const batchReassignBtn = document.getElementById('batch-reassign-btn');

    async function loadPersonsGrid() {
        const template = document.getElementById('person-card-template');
        grid.innerHTML = '<h4>Személyek betöltése...</h4>';

        const response = await fetch('/api/persons/gallery_data');
        const persons = await response.json();
        allPersonNames = persons.map(p => p.name).sort();
        grid.innerHTML = '';

        persons.forEach(person => {
            const cardClone = template.content.cloneNode(true);
            const card = cardClone.querySelector('.person-card');
            card.dataset.personName = person.name;
            card.querySelector('.person-name').textContent = person.name;
            card.querySelector('.photo-count').textContent = `${person.face_count} kép`;
            
            const img = card.querySelector('.profile-image');
            if (person.data.profile_image) {
                img.src = `/${person.data.profile_image}`;
            } else {
                img.src = `https://via.placeholder.com/150/444444/FFFFFF?text=${encodeURIComponent(person.name.charAt(0))}`;
            }
            
            card.addEventListener('click', () => showPersonGallery(person.name));
            grid.appendChild(cardClone);
        });
    }

    function showPersonGallery(name) {
        grid.classList.add('d-none');
        gallerySection.classList.remove('d-none');
        galleryTitle.textContent = `${name} arcképei`;
        
        currentPerson = name;
        currentPage = 1;
        galleryContainer.innerHTML = '';
        
        loadMoreBtn.onclick = () => loadFacesForPerson(false);
        
        loadFacesForPerson(true);
        setupFaceGalleryActions();
    }

    function showPersonGrid() {
        grid.classList.remove('d-none');
        gallerySection.classList.add('d-none');
        if(actionsBar) actionsBar.classList.add('d-none');
    }

    async function loadFacesForPerson(isFirstLoad = false) {
        const template = document.getElementById('face-gallery-card-template');

        try {
            const response = await fetch(`/api/faces/by_person/${currentPerson}?page=${currentPage}&limit=${FACES_PER_PAGE}`);
            const data = await response.json();
            totalFaces = data.total;

            if(data.faces.length === 0 && isFirstLoad) {
                galleryContainer.innerHTML = `<p class="text-muted">Nincsenek ehhez a személyhez rendelt arcképek.</p>`;
            }

            data.faces.forEach(face => {
                const cardClone = template.content.cloneNode(true);
                const cardContainer = cardClone.querySelector('.col');
                const cardElement = cardContainer.querySelector('.face-gallery-card');
                cardElement.dataset.facePath = face.face_path;
                cardElement.querySelector('.card-img-top').src = `/${face.face_path}`;
                
                cardElement.addEventListener('click', (e) => {
                    if (!e.target.closest('button')) {
                        cardElement.classList.toggle('selected');
                        updateFaceActionsBar();
                    }
                });

                cardElement.querySelector('.set-profile-btn').addEventListener('click', () => setAsProfileImage(currentPerson, face.face_path));
                galleryContainer.appendChild(cardClone);
            });

            currentPage++;
            loadMoreBtn.classList.toggle('d-none', galleryContainer.children.length >= totalFaces);
        } catch (error) {
            console.error(`Hiba a(z) ${currentPerson} arcképeinek betöltésekor:`, error);
        }
    }

    function setupFaceGalleryActions() {
        reassignSelect.innerHTML = '<option selected disabled>Válassz...</option>';
        allPersonNames.forEach(name => {
            if (name !== currentPerson) {
                const option = document.createElement('option');
                option.value = name;
                option.textContent = name;
                reassignSelect.appendChild(option);
            }
        });
        batchDeleteBtn.addEventListener('click', batchDeleteFaces);
        batchReassignBtn.addEventListener('click', batchReassignFaces);
    }

    function updateFaceActionsBar() {
        const selected = document.querySelectorAll('.face-gallery-card.selected');
        actionsBar.classList.toggle('d-none', selected.length === 0);
        if (selected.length > 0) {
            selectionCounter.textContent = `${selected.length} arc kijelölve`;
        }
    }
    
    async function batchDeleteFaces() {
        const selectedCards = document.querySelectorAll('.face-gallery-card.selected');
        const facePaths = Array.from(selectedCards).map(card => card.dataset.facePath);
        if (facePaths.length === 0 || !confirm(`Biztosan törlöd a kijelölt ${facePaths.length} arcot?`)) return;

        const response = await fetch('/api/faces/delete_batch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ face_paths: facePaths }),
        });
        const result = await response.json();
        if (result.status === 'success') {
            showToast(result.message);
            selectedCards.forEach(card => card.parentElement.remove());
            updateFaceActionsBar();
        } else { showToast(result.message, 'danger'); }
    }

    async function batchReassignFaces() {
        const selectedCards = document.querySelectorAll('.face-gallery-card.selected');
        const facePaths = Array.from(selectedCards).map(card => card.dataset.facePath);
        const targetName = reassignSelect.value;
        if (facePaths.length === 0 || !targetName || targetName === 'Válassz...') return;

        const response = await fetch('/api/faces/reassign_batch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ face_paths: facePaths, target_name: targetName }),
        });
        const result = await response.json();
        if (result.status === 'success') {
            showToast(result.message);
            selectedCards.forEach(card => card.parentElement.remove());
            updateFaceActionsBar();
        } else { showToast(result.message, 'danger'); }
    }
    
    async function setAsProfileImage(personName, facePath) {
        const response = await fetch('/api/persons/set_profile_image', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: personName, face_path: facePath }),
        });
        const result = await response.json();
        if (result.status === 'success') {
            showToast(result.message);
            document.querySelectorAll('.person-card').forEach(card => {
                if (card.querySelector('.person-name').textContent === personName) {
                    card.querySelector('.profile-image').src = `/${facePath}`;
                }
            });
        } else {
            showToast(result.message, 'danger');
        }
    }
    
    // --- INICIALIZÁLÁS ---
    const init = () => {
        if (isInitialized) return;
        loadPersonsGrid();
        backBtn.addEventListener('click', showPersonGrid);
        isInitialized = true;
    };
    
    if (knownFacesTabButton.classList.contains('active')) {
        init();
    }
    knownFacesTabButton.addEventListener('shown.bs.tab', init);
});