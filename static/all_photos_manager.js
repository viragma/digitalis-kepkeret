// static/all_photos_manager.js

document.addEventListener('DOMContentLoaded', () => {
    const allPhotosTabButton = document.getElementById('v-pills-all-photos-tab');
    if (!allPhotosTabButton) return;

    let isInitialized = false;
    let currentPage = 1;
    let hasNextPage = true;
    let allImages = [];
    let currentImageIndex = -1;
    let allPersonNames = [];

    // DOM elemek
    const grid = document.getElementById('all-photos-grid');
    const loadMoreBtn = document.getElementById('load-more-photos-btn');
    const lightboxModalEl = document.getElementById('lightbox-modal');
    const lightboxModal = new bootstrap.Modal(lightboxModalEl);
    const lightboxImage = document.getElementById('lightbox-image');
    const lightboxWrapper = document.getElementById('lightbox-content-wrapper');
    const lightboxFaceBoxContainer = document.getElementById('lightbox-face-boxes-container');
    const lightboxPrev = document.getElementById('lightbox-prev');
    const lightboxNext = document.getElementById('lightbox-next');
    const addFaceBtn = document.getElementById('add-face-btn');

    // Manuális rajzoláshoz
    let isDrawing = false;
    let startX, startY;
    const drawingBox = document.getElementById('drawing-box');

    const init = async () => {
        if (isInitialized) return;
        
        const personsRes = await fetch('/api/persons');
        allPersonNames = await personsRes.json();

        loadMoreBtn.addEventListener('click', () => loadImages(currentPage));
        lightboxPrev.addEventListener('click', showPrevImage);
        lightboxNext.addEventListener('click', showNextImage);
        addFaceBtn.addEventListener('click', toggleDrawingMode);

        lightboxWrapper.addEventListener('mousedown', startDrawing);
        lightboxWrapper.addEventListener('mousemove', draw);
        lightboxWrapper.addEventListener('mouseup', endDrawing);
        lightboxWrapper.addEventListener('mouseleave', endDrawing);

        document.addEventListener('keydown', (e) => {
            if (lightboxModalEl.classList.contains('show')) {
                if (e.key === 'ArrowLeft') showPrevImage();
                if (e.key === 'ArrowRight') showNextImage();
            }
        });
        
        loadImages(currentPage);
        isInitialized = true;
    };
    
    if (allPhotosTabButton.classList.contains('active')) init();
    allPhotosTabButton.addEventListener('shown.bs.tab', init);

    async function loadImages(page) { /* ... Változatlan ... */ }
    async function openLightbox(index) { /* ... Változatlan ... */ }
    async function updateLightboxContent() { /* ... Változatlan ... */ }
    
    function drawFaceBoxes(faces) {
        const naturalWidth = lightboxImage.naturalWidth;
        const naturalHeight = lightboxImage.naturalHeight;
        const displayWidth = lightboxImage.clientWidth;
        const displayHeight = lightboxImage.clientHeight;

        const widthRatio = displayWidth / naturalWidth;
        const heightRatio = displayHeight / naturalHeight;

        const template = document.getElementById('face-box-template');
        lightboxFaceBoxContainer.innerHTML = ''; // Előző keretek törlése

        faces.forEach(face => {
            if (!face.face_location) return;
            const [top, right, bottom, left] = face.face_location;

            const clone = template.content.cloneNode(true);
            const box = clone.querySelector('.face-box-interactive');
            box.style.top = `${top * heightRatio}px`;
            box.style.left = `${left * widthRatio}px`;
            box.style.width = `${(right - left) * widthRatio}px`;
            box.style.height = `${(bottom - top) * heightRatio}px`;

            // ... A keret többi logikája (szerkesztés, mentés) változatlan ...
            
            lightboxFaceBoxContainer.appendChild(clone);
        });
    }

    async function showPrevImage() { /* ... Változatlan ... */ }
    async function showNextImage() { /* ... Változatlan ... */ }

    // --- ÚJ FUNKCIÓK A MANUÁLIS CÍMKÉZÉSHEZ ---

    function toggleDrawingMode() {
        lightboxWrapper.classList.toggle('drawing-mode');
        if (lightboxWrapper.classList.contains('drawing-mode')) {
            addFaceBtn.classList.remove('btn-success');
            addFaceBtn.classList.add('btn-danger');
            addFaceBtn.innerHTML = '<i class="bi bi-x-circle"></i> Mégse';
        } else {
            addFaceBtn.classList.add('btn-success');
            addFaceBtn.classList.remove('btn-danger');
            addFaceBtn.innerHTML = '<i class="bi bi-plus-square-dotted"></i> Új arc hozzáadása';
        }
    }

    function startDrawing(e) {
        if (!lightboxWrapper.classList.contains('drawing-mode')) return;
        e.preventDefault();
        isDrawing = true;
        startX = e.offsetX;
        startY = e.offsetY;
        drawingBox.style.left = `${startX}px`;
        drawingBox.style.top = `${startY}px`;
        drawingBox.style.width = '0px';
        drawingBox.style.height = '0px';
    }

    function draw(e) {
        if (!isDrawing) return;
        const currentX = e.offsetX;
        const currentY = e.offsetY;
        const width = currentX - startX;
        const height = currentY - startY;
        
        drawingBox.style.width = `${Math.abs(width)}px`;
        drawingBox.style.height = `${Math.abs(height)}px`;
        drawingBox.style.left = `${width > 0 ? startX : currentX}px`;
        drawingBox.style.top = `${height > 0 ? startY : currentY}px`;
    }

    function endDrawing(e) {
        if (!isDrawing) return;
        isDrawing = false;
        
        const rect = {
            left: parseInt(drawingBox.style.left, 10),
            top: parseInt(drawingBox.style.top, 10),
            width: parseInt(drawingBox.style.width, 10),
            height: parseInt(drawingBox.style.height, 10)
        };

        // Csak akkor kezeljük, ha a doboz nagyobb, mint egy minimális méret
        if (rect.width > 20 && rect.height > 20) {
            showNewFaceMenu(rect);
        }
        drawingBox.style.width = '0px';
        drawingBox.style.height = '0px';
    }

    function showNewFaceMenu(rect) {
        // Eltávolítjuk a korábbi menüt, ha volt
        const existingMenu = document.getElementById('new-face-menu');
        if (existingMenu) existingMenu.remove();

        const menu = document.createElement('div');
        menu.id = 'new-face-menu';
        menu.className = 'new-face-menu';
        menu.style.left = `${rect.left}px`;
        menu.style.top = `${rect.top + rect.height + 5}px`;

        let selectHTML = '<select class="form-select form-select-sm"><option selected disabled>Válassz...</option>';
        allPersonNames.forEach(name => {
            selectHTML += `<option value="${name}">${name}</option>`;
        });
        selectHTML += '</select>';

        menu.innerHTML = `
            <div class="input-group">
                ${selectHTML}
                <button class="btn btn-sm btn-success">✔️</button>
            </div>
        `;
        
        lightboxFaceBoxContainer.appendChild(menu);

        menu.querySelector('button').addEventListener('click', async () => {
            const selectedName = menu.querySelector('select').value;
            if (selectedName === 'Válassz...') return;

            const coordsPercent = {
                left: rect.left / lightboxImage.clientWidth,
                top: rect.top / lightboxImage.clientHeight,
                width: rect.width / lightboxImage.clientWidth,
                height: rect.height / lightboxImage.clientHeight,
            };
            
            const response = await fetch('/api/faces/add_manual', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    filename: allImages[currentImageIndex],
                    name: selectedName,
                    coords: coordsPercent
                })
            });
            const result = await response.json();
            if (result.status === 'success') {
                showToast(result.message);
                drawFaceBoxes([result.new_face]); // Csak az új keretet rajzoljuk hozzá
            } else {
                showToast(result.message, 'danger');
            }
            menu.remove();
            toggleDrawingMode(); // Kilépünk a rajzoló módból
        });
    }
});