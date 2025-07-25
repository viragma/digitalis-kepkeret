// static/script.js

let config = {};
let imageList = [];
let currentIndex = 0;
let isPaused = false;

// DOM elemek
const currentBackgroundDiv = document.getElementById('current-background');
const nextBackgroundDiv = document.getElementById('next-background');
const currentImageDiv = document.getElementById('current-image');
const nextImageDiv = document.getElementById('next-image');
const clockDiv = document.getElementById('clock');
// ...

async function fetchConfigAndImages() {
    try {
        const [configRes, imageListRes] = await Promise.all([
            fetch('/config'),
            fetch('/imagelist')
        ]);
        config = await configRes.json();
        imageList = await imageListRes.json();
        
       const transitionSpeed = (config.transition_speed || 1500) / 1000;
        // Az áttűnés sebességét beállítjuk mind a 4 rétegen
        currentImageDiv.style.transitionDuration = `${transitionSpeed}s`;
        nextImageDiv.style.transitionDuration = `${transitionSpeed}s`;
        currentBackgroundDiv.style.transitionDuration = `${transitionSpeed}s`;
        nextBackgroundDiv.style.transitionDuration = `${transitionSpeed}s`;

        // Óra beállításai
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
    if (imageList.length === 0) return;
    currentIndex = -1;
    // Az első kép betöltése háttérként és előtérként is, áttűnés nélkül
    const initialImageUrl = `/static/images/${imageList[0]}`;
    currentImageDiv.style.backgroundImage = `url('${initialImageUrl}')`;
    currentBackgroundDiv.style.backgroundImage = `url('${initialImageUrl}')`;
    currentBackgroundDiv.style.filter = `blur(${config.blur_strength || 20}px)`;
    currentImageDiv.classList.add('visible');
    currentBackgroundDiv.classList.add('visible');
    
    setTimeout(showNextImage, config.interval || 10000);
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
        // 1. Az új képet betöltjük a rejtett "következő" rétegekbe
        nextBackgroundDiv.style.backgroundImage = `url('${imageUrl}')`;
        nextBackgroundDiv.style.filter = `blur(${config.blur_strength || 20}px)`;
        nextImageDiv.style.backgroundImage = `url('${imageUrl}')`;
        nextImageDiv.style.filter = config.image_filter || 'none';

        // Ken Burns effekt kezelése
        nextImageDiv.classList.remove('ken-burns');
        if (config.zoom_enabled) {
            nextImageDiv.style.animationDuration = (config.zoom_duration || 30000) + 'ms';
            const origins = ['top left', 'top right', 'bottom left', 'bottom right', 'center center'];
            const randomOrigin = origins[Math.floor(Math.random() * origins.length)];
            nextImageDiv.style.transformOrigin = randomOrigin;
            setTimeout(() => nextImageDiv.classList.add('ken-burns'), 50);
        } else {
            nextImageDiv.style.transform = `scale(1.0)`;
        }

        // 2. Egyszerre láthatóvá tesszük a "következő" rétegeket és eltüntetjük az "aktuálisat"
        currentImageDiv.classList.remove('visible');
        nextImageDiv.classList.add('visible');
        currentBackgroundDiv.classList.remove('visible');
        nextBackgroundDiv.classList.add('visible');
        
        // 3. Egy kis idő után felcseréljük a szerepeket a háttérben
        setTimeout(() => {
            currentImageDiv.style.backgroundImage = nextImageDiv.style.backgroundImage;
            currentBackgroundDiv.style.backgroundImage = nextBackgroundDiv.style.backgroundImage;
        }, config.transition_speed || 1500);
        
        // 4. Időzítjük a következő váltást
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