// static/trainer_manager.js

document.addEventListener('DOMContentLoaded', () => {
    const trainerTabButton = document.getElementById('v-pills-trainer-tab');
    if (!trainerTabButton) return;

    let isInitialized = false;

    // DOM Elemek
    const personListContainer = document.getElementById('trainer-person-list');
    const detailsView = document.getElementById('trainer-details-view');
    const welcomeMessage = document.getElementById('trainer-welcome-message');
    const personNameTitle = document.getElementById('trainer-person-name');
    const averageFaceContainer = document.getElementById('trainer-average-face');
    const suggestionsList = document.getElementById('trainer-suggestions');
    const knownFacesGrid = document.getElementById('trainer-known-faces-grid');
    const newFacesGrid = document.getElementById('trainer-new-faces-grid');

    const initTrainerTab = async () => {
        if (isInitialized) return;
        isInitialized = true;
        
        console.log("Tanító Adatbázis inicializálása...");
        await loadPersonList();
    };

    async function loadPersonList() {
        personListContainer.innerHTML = '<div class="text-center"><div class="spinner-border spinner-border-sm" role="status"></div></div>';
        try {
            const response = await fetch('/api/trainer/persons');
            const persons = await response.json();

            personListContainer.innerHTML = ''; // Töröljük a töltés jelzőt
            persons.forEach(person => {
                const personLink = document.createElement('a');
                personLink.href = "#";
                personLink.className = 'list-group-item list-group-item-action';
                personLink.textContent = person.name;
                personLink.addEventListener('click', (e) => {
                    e.preventDefault();
                    // Aktív állapot beállítása a listában
                    document.querySelectorAll('#trainer-person-list .list-group-item-action').forEach(link => link.classList.remove('active'));
                    personLink.classList.add('active');
                    
                    loadPersonDetails(person.name);
                });
                personListContainer.appendChild(personLink);
            });

        } catch (error) {
            console.error("Hiba a személyek listájának betöltésekor:", error);
            personListContainer.innerHTML = '<div class="list-group-item text-danger">Hiba a betöltéskor.</div>';
        }
    }

    async function loadPersonDetails(name) {
        welcomeMessage.classList.add('d-none');
        detailsView.classList.remove('d-none');
        personNameTitle.textContent = name;
        
        // Ürítjük a konténereket a betöltés előtt
        knownFacesGrid.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div></div>';
        suggestionsList.innerHTML = '';
        newFacesGrid.innerHTML = '';

        try {
            const response = await fetch(`/api/trainer/person_details/${name}`);
            const details = await response.json();

            // Tanítóképek megjelenítése
            knownFacesGrid.innerHTML = '';
            const template = document.getElementById('trainer-face-card-template');
            if (details.training_images && details.training_images.length > 0) {
                details.training_images.forEach(imgPath => {
                    const cardClone = template.content.cloneNode(true);
                    cardClone.querySelector('img').src = imgPath;
                    cardClone.querySelector('.quality-info').textContent = "Elemzés..."; // Placeholder
                    knownFacesGrid.appendChild(cardClone);
                });
            } else {
                knownFacesGrid.innerHTML = '<div class="col-12"><p class="text-muted">Ehhez a személyhez nincsenek tanítóképek.</p></div>';
            }
            
            // Javaslatok megjelenítése
            if (details.suggestions && details.suggestions.length > 0) {
                details.suggestions.forEach(suggestion => {
                    const listItem = document.createElement('li');
                    listItem.className = 'list-group-item';
                    listItem.textContent = suggestion;
                    suggestionsList.appendChild(listItem);
                });
            }

        } catch (error) {
            console.error(`Hiba a(z) ${name} részleteinek betöltésekor:`, error);
            knownFacesGrid.innerHTML = '<div class="col-12"><p class="text-danger">Hiba a részletek betöltésekor.</p></div>';
        }
    }


    if (trainerTabButton.classList.contains('active')) {
        initTrainerTab();
    }
    trainerTabButton.addEventListener('shown.bs.tab', initTrainerTab);
});