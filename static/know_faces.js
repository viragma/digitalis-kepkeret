// static/known_faces.js
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
    
    // Kezdőbetöltés, ha ez az aktív fül
    if (knownFacesTabButton.classList.contains('active')) {
        init();
    }
    // Eseményfigyelő a fülre kattintáshoz
    knownFacesTabButton.addEventListener('show.bs.tab', init);
});

let currentPage = 1;
let currentPerson = '';
let totalFaces = 0;
const FACES_PER_PAGE = 30;

async function loadPersonsGrid() {
    const grid = document.getElementById('person-selector-grid');
    const template = document.getElementById('person-card-template');
    grid.innerHTML = '<h4>Betöltés...</h4>';

    const response = await fetch('/api/persons/gallery_data');
    const persons = await response.json();
    grid.innerHTML = '';

    persons.forEach(person => {
        const cardClone = template.content.cloneNode(true);
        const card = cardClone.querySelector('.person-card');
        const img = card.querySelector('.profile-image');
        const nameEl = card.querySelector('.person-name');

        nameEl.textContent = person.name;
        if (person.data.profile_image) {
            img.src = `/${person.data.profile_image}`;
        } else {
            img.src = `https://via.placeholder.com/150/444444/FFFFFF?text=${person.name.charAt(0)}`;
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

    const response = await fetch(`/api/faces/by_person/${currentPerson}?page=${currentPage}&limit=${FACES_PER_PAGE}`);
    const data = await response.json();
    
    totalFaces = data.total;

    data.faces.forEach(face => {
        const cardClone = template.content.cloneNode(true);
        const img = cardClone.querySelector('.card-img-top');
        const setProfileBtn = cardClone.querySelector('.set-profile-btn');

        img.src = `/${face.face_path}`;
        setProfileBtn.addEventListener('click', () => setAsProfileImage(currentPerson, face.face_path));
        container.appendChild(cardClone);
    });

    currentPage++;
    if (container.children.length >= totalFaces) {
        loadMoreBtn.classList.add('d-none');
    } else {
        loadMoreBtn.classList.remove('d-none');
    }

    if (isFirstLoad) {
        loadMoreBtn.onclick = () => loadFacesForPerson(false);
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
        // Frissítsük a profilképet a rácson is
        const grid = document.getElementById('person-selector-grid');
        grid.querySelectorAll('.person-card').forEach(card => {
            if (card.querySelector('.person-name').textContent === personName) {
                card.querySelector('.profile-image').src = `/${facePath}`;
            }
        });
    } else {
        showToast(result.message, 'danger');
    }
}