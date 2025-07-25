// static/script.js

let config = {};
let imageList = [];
let currentIndex = 0;
let isPaused = false;

const currentImageDiv = document.getElementById('current-image');
const nextImageDiv = document.getElementById('next-image');
const clockDiv = document.getElementById('clock');

async function fetchConfigAndImages() {
    try {
        const [configRes, imageListRes] = await Promise.all([
            fetch('/config'),
            fetch('/imagelist')
        ]);
        config = await configRes.json();
        imageList = await imageListRes.json();
        
        if (clockDiv) {
            if (config.enable_clock) {
                clockDiv.style.display = 'block';
                clockDiv.style.fontSize = config.clock_size || '2.5rem';
            } else {
                clockDiv.style.display = 'none';
            }
        }

        startSlideshow();
    } catch (error) {
        console.error("Hiba a konfiguráció vagy a képlista betöltésekor:", error);
    }
}

function startSlideshow() {
    if (imageList.length === 0) {
        console.log("Nincsenek képek a vetítéshez.");
        return;
    }
    currentIndex = -1; 
    showNextImage();
}

function showNextImage() {
    if (isPaused) {
        setTimeout(showNextImage, 1000);
        return;
    }

    currentIndex = (currentIndex + 1) % imageList.length;
    const imageUrl = `/static/images/${imageList[currentIndex]}`;
    
    const img = new Image();
    img.src = imageUrl;
    img.onload = () => {
        nextImageDiv.style.backgroundImage = `url('${imageUrl}')`;
        nextImageDiv.style.filter = config.image_filter || 'none';

        // Ken Burns effekt kezelése
        nextImageDiv.classList.remove('ken-burns');
        
        if (config.zoom_enabled) {
            nextImageDiv.style.animationDuration = (config.zoom_duration || 30000) + 'ms';
            
            const origins = ['top left', 'top right', 'bottom left', 'bottom right', 'center center'];
            const randomOrigin = origins[Math.floor(Math.random() * origins.length)];
            nextImageDiv.style.transformOrigin = randomOrigin;
            
            setTimeout(() => {
                nextImageDiv.classList.add('ken-burns');
            }, 50);

        } else {
            nextImageDiv.style.transform = `scale(${config.nozoom_scale || 1.1})`;
        }

        currentImageDiv.classList.remove('visible');
        nextImageDiv.classList.add('visible');

        setTimeout(() => {
            currentImageDiv.style.backgroundImage = `url('${imageUrl}')`;
            currentImageDiv.style.filter = config.image_filter || 'none';
        }, config.transition_speed || 1000);
        
        setTimeout(showNextImage, config.interval || 10000);
    };
}

function updateClock() {
    if (config.enable_clock && clockDiv) {
        const now = new Date();
        const timeString = now.toLocaleTimeString('hu-HU', { hour: '2-digit', minute: '2-digit' });
        const dateString = now.toLocaleDateString('hu-HU', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
        clockDiv.innerHTML = `${timeString}<br><span class="date">${dateString}</span>`;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    fetchConfigAndImages();
    setInterval(updateClock, 1000);
});