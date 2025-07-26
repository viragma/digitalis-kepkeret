// static/known_faces.js
let allPersonNames = [];
let currentPage = 1;
let currentPerson = '';
let totalFaces = 0;
const FACES_PER_PAGE = 30;

document.addEventListener('DOMContentLoaded', () => {
    const knownFacesTabButton = document.getElementById('v-pills-known-faces-tab');
    if (!knownFacesTabButton) return;
    let isInitialized = false;
    const init = () => {
        if (isInitialized) return;
        loadPersonsGrid();
        document.getElementById('back-to-grid-btn').addEventListener('click', showPersonGrid);
        isInitialized = true;
    };
    if (knownFacesTabButton.classList.contains('active')) init();
    knownFacesTabButton.addEventListener('show.bs.tab', init);
});

async function loadPersonsGrid() {
    const grid = document.getElementById('person-selector-grid');
    const template = document.getElementById('person-card-template');
    grid.innerHTML = '<h4>Személyek betöltése...</h4>';

    const response = await fetch('/api/persons/gallery_data');
    const persons = await response.json();
    allPersonNames = persons.map(p => p.name);
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
        
        card.addEventListener('click', (e) => {
            if (e.ctrlKey || e.metaKey) {
                card.classList.toggle('selected');
                updateActionsBar();
            } else {
                showPersonGallery(person.name);
            }
        });
        grid.appendChild(cardClone);
    });
    
    document.getElementById('batch-delete-btn').addEventListener('click', batchDeletePersons);
    document.getElementById('batch-reassign-btn').addEventListener('click', batchReassignPersons);
}

function updateActionsBar() {
    const selectedCards = document.querySelectorAll('.person-card.selected');
    const bar = document.getElementById('person-actions-bar');
    const counter = document.getElementById('selection-counter');
    const reassignSelect = document.getElementById('batch-reassign-select');
    
    if (selectedCards.length > 0) {
        counter.textContent = `${selectedCards.length} személy kijelölve`;
        bar.classList.remove('d-none');

        const selectedNames = Array.from(selectedCards).map(c => c.dataset.personName);
        reassignSelect.innerHTML = '<option selected disabled>Válassz...</option>';
        allPersonNames.forEach(name => {
            if (!selectedNames.includes(name)) {
                const option = document.createElement('option');
                option.value = name;
                option.textContent = name;
                reassignSelect.appendChild(option);
            }
        });
    } else {
        bar.classList.add('d-none');
    }
}

async function batchDeletePersons() {
    const selectedCards = document.querySelectorAll('.person-card.selected');
    const namesToDelete = Array.from(selectedCards).map(card => card.dataset.personName);
    if (namesToDelete.length === 0) return;
    if (!confirm(`Biztosan törlöd a következő ${namesToDelete.length} személyt és minden hozzájuk rendelt arcot?\n\n${namesToDelete.join(', ')}`)) return;

    const response = await fetch('/api/persons/delete_batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ names: namesToDelete }),
    });
    const result = await response.json();
    if (result.status === 'success') {
        showToast(result.message);
        loadPersonsGrid();
        updateActionsBar();
    } else { showToast(result.message, 'danger'); }
}

async function batchReassignPersons() {
    const selectedCards = document.querySelectorAll('.person-card.selected');
    const sourceNames = Array.from(selectedCards).map(card => card.dataset.personName);
    const targetName = document.getElementById('batch-reassign-select').value;

    if (sourceNames.length === 0 || !targetName || targetName === 'Válassz...') return;
    if (!confirm(`Biztosan átnevezed a következő ${sourceNames.length} személyt erre: ${targetName}?`)) return;

    const response = await fetch('/api/persons/reassign_batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source_names: sourceNames, target_name: targetName }),
    });
    const result = await response.json();
    if (result.status === 'success') {
        showToast(result.message);
        loadPersonsGrid();
        updateActionsBar();
    } else { showToast(result.message, 'danger'); }
}

function showPersonGallery(name) {
    document.getElementById('person-selector-grid').classList.add('d-none');
    document.getElementById('person-actions-bar').classList.add('d-none');
    document.getElementById('person-gallery-section').classList.remove('d-none');
    document.getElementById('gallery-title').textContent = `${name} arcképei`;
    
    currentPerson = name;
    currentPage = 1;
    document.getElementById('gallery-container').innerHTML = '';
    
    const loadMoreBtn = document.getElementById('load-more-btn');
    loadMoreBtn.onclick = () => loadFacesForPerson(false);
    
    loadFacesForPerson(true);
}

function showPersonGrid() {
    document.getElementById('person-selector-grid').classList.remove('d-none');
    document.getElementById('person-gallery-section').classList.add('d-none');
}

async function loadFacesForPerson(isFirstLoad = false) {
    const container = document.getElementById('gallery-container');
    const template = document.getElementById('face-gallery-card-template');
    const loadMoreBtn = document.getElementById('load-more-btn');

    try {
        const response = await fetch(`/api/faces/by_person/${currentPerson}?page=${currentPage}&limit=${FACES_PER_PAGE}`);
        const data = await response.json();
        totalFaces = data.total;

        if(data.faces.length === 0 && isFirstLoad) {
            container.innerHTML = `<p class="text-muted">Nincsenek ehhez a személyhez rendelt arcképek.</p>`;
        }

        data.faces.forEach(face => {
            const cardClone = template.content.cloneNode(true);
            const cardContainer = cardClone.querySelector('.col');
            const img = cardContainer.querySelector('.card-img-top');
            const setProfileBtn = cardContainer.querySelector('.set-profile-btn');
            const reassignBtn = cardContainer.querySelector('.reassign-btn');
            const deleteBtn = cardContainer.querySelector('.delete-btn');
            const reassignMenu = cardContainer.querySelector('.reassign-menu');
            const reassignSelect = cardContainer.querySelector('.reassign-select');
            const reassignSaveBtn = cardContainer.querySelector('.reassign-save-btn');

            img.src = `/${face.face_path}`;
            
            allPersonNames.forEach(name => {
                const option = document.createElement('option');
                option.value = name;
                option.textContent = name;
                if (name === currentPerson) option.selected = true;
                reassignSelect.appendChild(option);
            });

            setProfileBtn.addEventListener('click', () => setAsProfileImage(currentPerson, face.face_path));
            deleteBtn.addEventListener('click', () => deleteFace(face.face_path, cardContainer));
            reassignBtn.addEventListener('click', () => reassignMenu.classList.toggle('d-none'));
            reassignSaveBtn.addEventListener('click', () => reassignFace(face.face_path, reassignSelect.value, cardContainer));

            container.appendChild(cardClone);
        });

        currentPage++;
        loadMoreBtn.classList.toggle('d-none', container.children.length >= totalFaces);
    } catch (error) {
        console.error(`Hiba a(z) ${currentPerson} arcképeinek betöltésekor:`, error);
    }
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
    } else { showToast(result.message, 'danger'); }
}

async function reassignFace(facePath, newName, cardContainer) {
    const response = await fetch('/api/update_face_name', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ face_path: facePath, new_name: newName }),
    });
    const result = await response.json();
    if (result.status === 'success') {
        showToast(`Arc sikeresen áthelyezve ide: ${newName}`);
        cardContainer.remove();
    } else { showToast(result.message, 'danger'); }
}

async function deleteFace(facePath, cardContainer) {
    if (!confirm('Biztosan törlöd ezt az arcképet? Ez a művelet nem vonható vissza.')) return;
    
    const response = await fetch('/api/faces/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ face_path: facePath }),
    });
    const result = await response.json();
    if (result.status === 'success') {
        showToast(result.message);
        cardContainer.remove();
    } else { showToast(result.message, 'danger'); }
}