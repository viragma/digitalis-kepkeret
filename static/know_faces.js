// static/known_faces.js

document.addEventListener('DOMContentLoaded', () => {
    console.log('known_faces.js: DOM betöltődött.');
    
    const knownFacesTabButton = document.getElementById('v-pills-known-faces-tab');
    if (!knownFacesTabButton) {
        console.error('Hiba: A "v-pills-known-faces-tab" ID-val rendelkező fül gomb nem található!');
        return;
    }
    console.log('known_faces.js: A fül gombja ("v-pills-known-faces-tab") megtalálva.');

    let isInitialized = false;

    const init = () => {
        console.log('known_faces.js: init() funkció meghívva.');
        if (isInitialized) {
            console.log('known_faces.js: Már inicializálva, nem fut le újra.');
            return;
        }
        loadPersonsGrid();
        
        const backBtn = document.getElementById('back-to-grid-btn');
        if(backBtn) {
            backBtn.addEventListener('click', showPersonGrid);
        } else {
            console.error('Hiba: A "back-to-grid-btn" gomb nem található!');
        }

        isInitialized = true;
        console.log('known_faces.js: Inicializálás befejezve.');
    };
    
    if (knownFacesTabButton.classList.contains('active')) {
        console.log('known_faces.js: Az "Ismert Arcok" fül aktív, indítom az inicializálást.');
        init();
    }
    
    knownFacesTabButton.addEventListener('show.bs.tab', init);
});

let currentPage = 1;
let currentPerson = '';
let totalFaces = 0;
const FACES_PER_PAGE = 30;

async function loadPersonsGrid() {
    console.log('known_faces.js: loadPersonsGrid() elindult.');
    const grid = document.getElementById('person-selector-grid');
    const template = document.getElementById('person-card-template');
    if (!grid || !template) {
        console.error('Hiba: A "#person-selector-grid" vagy a "#person-card-template" nem található!');
        return;
    }
    grid.innerHTML = '<h4>Személyek betöltése...</h4>';

    try {
        const response = await fetch('/api/persons/gallery_data');
        const persons = await response.json();
        console.log('known_faces.js: Személyek adatai megérkeztek a szerverről:', persons);
        grid.innerHTML = '';

        if (persons.length === 0) {
            grid.innerHTML = '<p class="text-muted">Nincsenek ismert személyek az adatbázisban.</p>';
            return;
        }

        persons.forEach(person => {
            console.log(`known_faces.js: Kártya létrehozása a következő személynek: ${person.name}`);
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
    } catch (error) {
        console.error('Hiba a személyek rácsának betöltésekor:', error);
        grid.innerHTML = '<p class="text-danger">Hiba történt a személyek betöltése közben.</p>';
    }
}

function showPersonGallery(name) {
    console.log(`known_faces.js: showPersonGallery() meghívva a következővel: ${name}`);
    document.getElementById('person-selector-grid').classList.add('d-none');
    document.getElementById('person-gallery-section').classList.remove('d-none');
    document.getElementById('gallery-title').textContent = `${name} arcképei`;
    
    currentPerson = name;
    currentPage = 1;
    document.getElementById('gallery-container').innerHTML = '';
    
    const loadMoreBtn = document.getElementById('load-more-btn');
    loadMoreBtn.classList.remove('d-none'); // Biztosítjuk, hogy a gomb látható
    loadMoreBtn.onclick = () => loadFacesForPerson(false); // Eseménykezelő beállítása
    
    loadFacesForPerson(true);
}

function showPersonGrid() {
    document.getElementById('person-selector-grid').classList.remove('d-none');
    document.getElementById('person-gallery-section').classList.add('d-none');
}

async function loadFacesForPerson(isFirstLoad = false) {
    console.log(`known_faces.js: Arcképek betöltése ehhez: ${currentPerson}, oldal: ${currentPage}`);
    const container = document.getElementById('gallery-container');
    const template = document.getElementById('face-gallery-card-template');
    const loadMoreBtn = document.getElementById('load-more-btn');

    try {
        const response = await fetch(`/api/faces/by_person/${currentPerson}?page=${currentPage}&limit=${FACES_PER_PAGE}`);
        const data = await response.json();
        console.log('known_faces.js: Arcképek adatai megérkeztek:', data);
        
        totalFaces = data.total;

        if(data.faces.length === 0 && isFirstLoad) {
            container.innerHTML = `<p class="text-muted">Nincsenek ehhez a személyhez rendelt arcképek.</p>`;
        }

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
    } catch (error) {
        console.error(`Hiba a(z) ${currentPerson} arcképeinek betöltésekor:`, error);
    }
}

async function setAsProfileImage(personName, facePath) {
    console.log(`known_faces.js: Profilkép beállítása... Személy: ${personName}, Kép: ${facePath}`);
    try {
        const response = await fetch('/api/persons/set_profile_image', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: personName, face_path: facePath }),
        });
        const result = await response.json();
        if (result.status === 'success') {
            showToast(result.message);
            const grid = document.getElementById('person-selector-grid');
            grid.querySelectorAll('.person-card').forEach(card => {
                if (card.querySelector('.person-name').textContent === personName) {
                    card.querySelector('.profile-image').src = `/${facePath}`;
                }
            });
        } else {
            showToast(result.message, 'danger');
        }
    } catch (error) {
        console.error("Hiba a profilkép beállításakor:", error);
        showToast("Hálózati hiba a profilkép beállításakor.", "danger");
    }
}