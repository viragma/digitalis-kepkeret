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
    const lightboxModal = new bootstrap.Modal(document.getElementById('lightbox-modal'));
    const lightboxImage = document.getElementById('lightbox-image');
    const lightboxPrev = document.getElementById('lightbox-prev');
    const lightboxNext = document.getElementById('lightbox-next');


    const init = () => {
        if (isInitialized) return;
        
        loadMoreBtn.addEventListener('click', () => loadImages(currentPage));
        lightboxPrev.addEventListener('click', showPrevImage);
        lightboxNext.addEventListener('click', showNextImage);

        // Billentyűzet-navigáció a lightboxban
        document.addEventListener('keydown', (e) => {
            if (document.getElementById('lightbox-modal').classList.contains('show')) {
                if (e.key === 'ArrowLeft') showPrevImage();
                if (e.key === 'ArrowRight') showNextImage();
            }
        });
        
        loadImages(currentPage);
        isInitialized = true;
    };
    
    if (allPhotosTabButton.classList.contains('active')) {
        init();
    }
    allPhotosTabButton.addEventListener('shown.bs.tab', init);

    async function loadImages(page) {
        if (!hasNextPage && page > 1) {
            console.log("Nincs több kép.");
            return;
        }
        
        loadMoreBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Töltés...';

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

    function openLightbox(index) {
        currentImageIndex = index;
        updateLightboxImage();
        lightboxModal.show();
    }
    
    function updateLightboxImage() {
        if (currentImageIndex >= 0 && currentImageIndex < allImages.length) {
            lightboxImage.src = `/static/images/${allImages[currentImageIndex]}`;
        }
    }

    function showPrevImage() {
        if (currentImageIndex > 0) {
            currentImageIndex--;
            updateLightboxImage();
        }
    }

    function showNextImage() {
        if (currentImageIndex < allImages.length - 1) {
            currentImageIndex++;
            updateLightboxImage();
        }
    }
});