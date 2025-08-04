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
        
        await loadPersonList();
    };

    async function loadPersonList() {
        personListContainer.innerHTML = '<div class="text-center"><div class="spinner-border spinner-border-sm" role="status"></div></div>';
        try {
            const response = await fetch('/api/trainer/persons');
            const persons = await response.json();

            personListContainer.innerHTML = '';
            persons.forEach(person => {
                const personLink = document.createElement('a');
                personLink.href = "#";
                personLink.className = 'list-group-item list-group-item-action d-flex align-items-center';
                
                const img = document.createElement('img');
                img.src = person.profile_image || `https://via.placeholder.com/30/444444/FFFFFF?text=${encodeURIComponent(person.name.charAt(0))}`;
                img.className = 'rounded-circle me-2';
                img.width = 30;
                img.height = 30;
                img.style.objectFit = 'cover';

                personLink.appendChild(img);
                personLink.append(person.name);

                personLink.addEventListener('click', (e) => {
                    e.preventDefault();
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
        
        knownFacesGrid.innerHTML = '<div class="col-12 text-center"><div class="spinner-border" role="status"></div></div>';
        averageFaceContainer.innerHTML = '<div class="spinner-border spinner-border-sm"></div>';
        suggestionsList.innerHTML = '';
        newFacesGrid.innerHTML = '';

        try {
            const response = await fetch(`/api/trainer/person_details/${name}`);
            const details = await response.json();

            if (details.average_face_image) {
                averageFaceContainer.innerHTML = `<img src="${details.average_face_image}?t=${new Date().getTime()}" class="img-fluid rounded" alt="Átlag-arc">`;
            } else {
                averageFaceContainer.innerHTML = '<div class="p-3 text-center text-muted small">Nincs elég tanítókép a fantomkép generálásához.</div>';
            }

            knownFacesGrid.innerHTML = '';
            const template = document.getElementById('trainer-face-card-template');
            if (details.training_images && details.training_images.length > 0) {
                details.training_images.forEach(imgData => {
                    const cardClone = template.content.cloneNode(true);
                    cardClone.querySelector('img').src = imgData.path;
                    
                    const qualityInfo = cardClone.querySelector('.quality-info');
                    
                    if (imgData && imgData.analysis) {
                        if (imgData.analysis.error) {
                            qualityInfo.innerHTML = `<span class="text-danger" title="${imgData.analysis.error}">Hiba</span>`;
                        } else {
                            const sharpness = imgData.analysis.sharpness;
                            const sharpClass = sharpness < 50 ? 'text-danger' : (sharpness < 100 ? 'text-warning' : 'text-success');
                            const brightness = imgData.analysis.brightness;
                            const brightClass = brightness < 70 || brightness > 200 ? 'text-danger' : 'text-success';

                            qualityInfo.innerHTML = `
                                <span class="${sharpClass}" title="Élesség: ${sharpness}">🌫️</span>
                                <span class="${brightClass}" title="Fényerő: ${brightness}">☀️</span>
                            `;
                        }
                    } else {
                        qualityInfo.innerHTML = `<span class="text-danger" title="Hiányzó elemzési adatok.">N/A</span>`;
                        console.warn("Hiányzó 'analysis' adat a képhez:", imgData);
                    }

                    knownFacesGrid.appendChild(cardClone);
                });
            } else {
                knownFacesGrid.innerHTML = '<div class="col-12"><p class="text-muted">Ehhez a személyhez nincsenek tanítóképek.</p></div>';
            }
            
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