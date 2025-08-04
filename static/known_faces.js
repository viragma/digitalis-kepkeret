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
    knownFacesTabButton.addEventListener('shown.bs.tab', init);
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
            img.src = person.data.profile_image;
        } else {
            img.src = `https://via.placeholder.com/150/444444/FFFFFF?text=${encodeURIComponent(person.name.charAt(0))}`;
        }
        
        card.addEventListener('click', () => showPersonGallery(person.name));
        grid.appendChild(cardClone);
    });
}

function showPersonGallery(name) {
    document.getElementById('person-selector-grid').classList.add('d-none');
    document.getElementById('person-gallery-section').classList.remove('d-none');
    document.getElementById('gallery-title').textContent = `${name} arcképei`;
    
    currentPerson = name;
    currentPage = 1;
    document.getElementById('gallery-container').innerHTML = '';
    
    const loadMoreBtn = document.getElementById('load-more-btn');
    loadMoreBtn.onclick = () => loadFacesForPerson(false);
    
    loadFacesForPerson(true);
    setupFaceGalleryActions();
}

function showPersonGrid() {
    document.getElementById('person-selector-grid').classList.remove('d-none');
    document.getElementById('person-gallery-section').classList.add('d-none');
    document.getElementById('face-actions-bar').classList.add('d-none');
}

async function loadFacesForPerson(isFirstLoad = false) {
    const container = document.getElementById('gallery-container');
    const template = document.getElementById('face-gallery-card-template');
    const loadMoreBtn = document.getElementById('load-more-btn');

    const response = await fetch(`/api/faces/by_person/${currentPerson}?page=${currentPage}&limit=${FACES_PER_PAGE}`);
    const data = await response.json();
    totalFaces = data.total;

    data.faces.forEach(face => {
        const cardClone = template.content.cloneNode(true);
        const cardContainer = cardClone.querySelector('.col');
        const cardElement = cardContainer.querySelector('.face-gallery-card');
        const img = cardElement.querySelector('img');
        const scoreDiv = cardElement.querySelector('.confidence-score');
        
        img.src = face.face_path;
        cardElement.dataset.facePath = face.face_path;
        
        if (face.distance !== null && face.distance !== undefined) {
            const confidence = Math.max(0, Math.round((1 - (face.distance / 0.7)) * 100));
            scoreDiv.textContent = `${confidence}%`;
            if (confidence > 85) {
                scoreDiv.dataset.level = 'good';
            } else if (confidence > 60) {
                scoreDiv.dataset.level = 'medium';
            } else {
                scoreDiv.dataset.level = 'low';
            }
        }
        
        const setProfileBtn = cardContainer.querySelector('.set-profile-btn');
        setProfileBtn.addEventListener('click', () => setAsProfileImage(currentPerson, face.face_path));
        
        cardElement.addEventListener('click', (e) => {
            if (!e.target.closest('button')) {
                e.currentTarget.classList.toggle('selected');
                updateFaceActionsBar();
            }
        });
        
        container.appendChild(cardClone);
    });

    currentPage++;
    loadMoreBtn.classList.toggle('d-none', container.children.length >= totalFaces);
}

function setupFaceGalleryActions() {
    const reassignSelect = document.getElementById('batch-reassign-select');
    reassignSelect.innerHTML = '<option selected disabled>Válassz...</option>';
    allPersonNames.forEach(name => {
        if (name !== currentPerson) {
            const option = document.createElement('option');
            option.value = name;
            option.textContent = name;
            reassignSelect.appendChild(option);
        }
    });
    document.getElementById('batch-delete-btn').addEventListener('click', batchDeleteFaces);
    document.getElementById('batch-reassign-btn').addEventListener('click', batchReassignFaces);
}

function updateFaceActionsBar() {
    const selected = document.querySelectorAll('.face-gallery-card.selected');
    const bar = document.getElementById('face-actions-bar');
    const counter = document.getElementById('face-selection-counter');
    bar.classList.toggle('d-none', selected.length === 0);
    if (selected.length > 0) {
        counter.textContent = `${selected.length} arc kijelölve`;
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
    const targetName = document.getElementById('batch-reassign-select').value;
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
                card.querySelector('.profile-image').src = facePath;
            }
        });
    } else {
        showToast(result.message, 'danger');
    }
}