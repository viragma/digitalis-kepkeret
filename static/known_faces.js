// static/known_faces.js
let allPersonNames = []; // Globális változó a nevek tárolására

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

// ... (currentPage, currentPerson, stb. változatlanok) ...

async function loadPersonsGrid() {
    const grid = document.getElementById('person-selector-grid');
    const template = document.getElementById('person-card-template');
    grid.innerHTML = '<h4>Betöltés...</h4>';

    const response = await fetch('/api/persons/gallery_data');
    const persons = await response.json();
    allPersonNames = persons.map(p => p.name); // Elmentjük a neveket
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
            img.src = `https://via.placeholder.com/150/444444/FFFFFF?text=${encodeURIComponent(person.name.charAt(0))}`;
        }
        
        card.addEventListener('click', () => showPersonGallery(person.name));
        grid.appendChild(cardClone);
    });
}

// ... (showPersonGallery, showPersonGrid változatlanok) ...

async function loadFacesForPerson(isFirstLoad = false) {
    const container = document.getElementById('gallery-container');
    const template = document.getElementById('face-gallery-card-template');
    const loadMoreBtn = document.getElementById('load-more-btn');

    const response = await fetch(`/api/faces/by_person/${currentPerson}?page=${currentPage}&limit=${FACES_PER_PAGE}`);
    const data = await response.json();
    totalFaces = data.total;

    data.faces.forEach(face => {
        const cardClone = template.content.cloneNode(true);
        const cardElement = cardClone.querySelector('.face-gallery-card');
        const img = cardElement.querySelector('.card-img-top');
        const setProfileBtn = cardElement.querySelector('.set-profile-btn');
        const reassignBtn = cardElement.querySelector('.reassign-btn');
        const deleteBtn = cardElement.querySelector('.delete-btn');
        const reassignMenu = cardElement.querySelector('.reassign-menu');
        const reassignSelect = cardElement.querySelector('.reassign-select');
        const reassignSaveBtn = cardElement.querySelector('.reassign-save-btn');

        img.src = `/${face.face_path}`;
        
        // Legördülő menü feltöltése nevekkel
        allPersonNames.forEach(name => {
            const option = document.createElement('option');
            option.value = name;
            option.textContent = name;
            if (name === currentPerson) option.selected = true;
            reassignSelect.appendChild(option);
        });

        // Eseménykezelők
        setProfileBtn.addEventListener('click', () => setAsProfileImage(currentPerson, face.face_path));
        deleteBtn.addEventListener('click', () => deleteFace(face.face_path, cardElement.parentElement));
        reassignBtn.addEventListener('click', () => reassignMenu.classList.toggle('d-none'));
        reassignSaveBtn.addEventListener('click', () => reassignFace(face.face_path, reassignSelect.value, cardElement.parentElement));

        container.appendChild(cardClone);
    });

    currentPage++;
    loadMoreBtn.classList.toggle('d-none', container.children.length >= totalFaces);
    if (isFirstLoad) loadMoreBtn.onclick = () => loadFacesForPerson(false);
}

// ... (setAsProfileImage változatlan) ...

async function reassignFace(facePath, newName, cardContainer) {
    // Ez a funkció megegyezik a faces_manager.js-ben lévő saveFaceName-mel
    const response = await fetch('/api/update_face_name', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ face_path: facePath, new_name: newName }),
    });
    const result = await response.json();
    if (result.status === 'success') {
        showToast(`Arc sikeresen áthelyezve ide: ${newName}`);
        cardContainer.remove(); // Eltávolítjuk a kártyát, mert már nem ehhez a személyhez tartozik
    } else {
        showToast(result.message, 'danger');
    }
}

async function deleteFace(facePath, cardContainer) {
    if (!confirm('Biztosan törlöd ezt az arcképet? Ez a művelet nem vonható vissza.')) {
        return;
    }
    const response = await fetch('/api/faces/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ face_path: facePath }),
    });
    const result = await response.json();
    if (result.status === 'success') {
        showToast(result.message);
        cardContainer.remove();
    } else {
        showToast(result.message, 'danger');
    }
}