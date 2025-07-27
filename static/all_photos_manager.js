// static/all_photos_manager.js

document.addEventListener('DOMContentLoaded', () => {
    const allPhotosTabButton = document.getElementById('v-pills-all-photos-tab');
    if (!allPhotosTabButton) return;

    let isInitialized = false;
    let currentPage = 1;
    let hasNextPage = true;
    let allImages = [];
    let currentImageIndex = -1;

    const grid = document.getElementById('all-photos-grid');
    const loadMoreBtn = document.getElementById('load-more-photos-btn');
    const lightboxModalEl = document.getElementById('lightbox-modal');
    const lightboxModal = new bootstrap.Modal(lightboxModalEl);
    const lightboxImage = document.getElementById('lightbox-image');
    const lightboxFaceBoxContainer = document.getElementById('lightbox-face-boxes-container');
    const lightboxPrev = document.getElementById('lightbox-prev');
    const lightboxNext = document.getElementById('lightbox-next');

    const init = () => {
        if (isInitialized) return;
        
        loadMoreBtn.addEventListener('click', () => loadImages(currentPage));
        lightboxPrev.addEventListener('click', showPrevImage);
        lightboxNext.addEventListener('click', showNextImage);

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

    async function loadImages(page) {
        if (!hasNextPage && page > 1) return;
        loadMoreBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Töltés...';

        try {
            const response = await fetch(`/api/all_images?page=${page}&limit=24`);
            const data = await response.json();

            const template = document.getElementById('photo-card-template');
            
            data.images.forEach(imageFile => {
                allImages.push(imageFile);
                const clone = template.content.cloneNode(true);
                const card = clone.querySelector('.photo-card');
                const img = card.querySelector('img');
                img.src = `/static/images/${imageFile}`;
                
                const index = allImages.length - 1;
                card.addEventListener('click', () => openLightbox(index));
                
                grid.appendChild(clone);
            });

            currentPage++;
            hasNextPage = data.has_next;
            loadMoreBtn.classList.toggle('d-none', !hasNextPage);

        } catch (error) {
            console.error("Hiba a képek betöltésekor:", error);
        } finally {
            loadMoreBtn.innerHTML = 'További képek betöltése';
        }
    }

    async function openLightbox(index) {
        currentImageIndex = index;
        await updateLightboxContent();
        lightboxModal.show();
    }
    
    async function updateLightboxContent() {
        if (currentImageIndex < 0 || currentImageIndex >= allImages.length) return;

        const filename = allImages[currentImageIndex];
        lightboxImage.src = `/static/images/${filename}`;
        
        // Először töröljük a régi kereteket
        lightboxFaceBoxContainer.innerHTML = '';

        // Lekérjük az új arc adatokat
        const response = await fetch(`/api/image_details/${filename}`);
        const faces = await response.json();

        // Várunk, amíg az új kép betöltődik, hogy tudjuk a méreteit
        await new Promise(resolve => {
            if (lightboxImage.complete) {
                resolve();
            } else {
                lightboxImage.onload = resolve;
            }
        });

        drawFaceBoxes(faces);
    }
    
    function drawFaceBoxes(faces) {
        const naturalWidth = lightboxImage.naturalWidth;
        const naturalHeight = lightboxImage.naturalHeight;
        const displayWidth = lightboxImage.clientWidth;
        const displayHeight = lightboxImage.clientHeight;

        const widthRatio = displayWidth / naturalWidth;
        const heightRatio = displayHeight / naturalHeight;

        faces.forEach(face => {
            if (!face.face_location) return;
            const [top, right, bottom, left] = face.face_location;

            const box = document.createElement('div');
            box.className = 'face-box';
            box.style.top = `${top * heightRatio}px`;
            box.style.left = `${left * widthRatio}px`;
            box.style.width = `${(right - left) * widthRatio}px`;
            box.style.height = `${(bottom - top) * heightRatio}px`;

            const label = document.createElement('div');
            label.className = 'face-label';
            label.textContent = face.name || 'Ismeretlen';
            box.appendChild(label);

            lightboxFaceBoxContainer.appendChild(box);
        });
    }

    async function showPrevImage() {
        if (currentImageIndex > 0) {
            currentImageIndex--;
            await updateLightboxContent();
        }
    }

    async function showNextImage() {
        if (currentImageIndex < allImages.length - 1) {
            currentImageIndex++;
            await updateLightboxContent();
        }
    }
});