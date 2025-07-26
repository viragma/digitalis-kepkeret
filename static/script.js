// static/script.js

let config = {};
let imageList = [];
let currentIndex = 0;
let isPaused = false;

// DOM elemek
const currentImageDiv = document.getElementById('current-image');
const nextImageDiv = document.getElementById('next-image');
const clockDiv = document.getElementById('clock');
const infoContainer = document.getElementById('info-container');
const birthdayContainer = document.getElementById('birthday-container');
const currentBackgroundDiv = document.getElementById('current-background');
const nextBackgroundDiv = document.getElementById('next-background');
const upcomingBirthdaysContainer = document.getElementById('upcoming-birthdays-container');

async function initializeApp() {
    try {
        const [configRes, imageListRes] = await Promise.all([
            fetch('/config'),
            fetch('/imagelist')
        ]);
        config = await configRes.json();
        imageList = await imageListRes.json();
        
        await checkBirthdays();
        await updateUpcomingBirthdays();

        const transitionSpeed = (config.transition_speed || 1500) / 1000;
        currentImageDiv.style.transitionDuration = `${transitionSpeed}s`;
        nextImageDiv.style.transitionDuration = `${transitionSpeed}s`;
        currentBackgroundDiv.style.transitionDuration = `${transitionSpeed}s`;
        nextBackgroundDiv.style.transitionDuration = `${transitionSpeed}s`;

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
        console.error("Hiba az alkalmazás inicializálása során:", error); 
    }
}

function startSlideshow() {
    if (imageList.length === 0) return;
    currentIndex = 0;
    const initialImageObject = imageList[0];
    if (!initialImageObject) return;
    const initialImageUrl = `/static/images/${initialImageObject.file}`;
    currentImageDiv.style.backgroundImage = `url('${initialImageUrl}')`;
    currentBackgroundDiv.style.backgroundImage = `url('${initialImageUrl}')`;
    currentBackgroundDiv.style.filter = `blur(${config.blur_strength || 20}px)`;
    currentImageDiv.classList.add('visible');
    currentBackgroundDiv.classList.add('visible');
    
    // Az első képhez tartozó infókat is megjelenítjük
    let infoText = '';
    if (initialImageObject.people && initialImageObject.people.length > 0) infoText += initialImageObject.people.join(' & ');
    if (initialImageObject.date) infoText += (infoText ? ` - ${initialImageObject.date}` : initialImageObject.date);
    infoContainer.textContent = infoText;
    infoContainer.classList.add('visible');
    setTimeout(() => { infoContainer.classList.remove('visible'); }, (config.interval || 10000) - (config.transition_speed || 1500));

    setTimeout(showNextImage, config.interval || 10000);
}

function showNextImage() {
    if (isPaused) { setTimeout(showNextImage, 1000); return; }

    currentIndex = (currentIndex + 1) % imageList.length;
    const imageObject = imageList[currentIndex];
    const imageUrl = `/static/images/${imageObject.file}`;
    
    const img = new Image();
    img.src = imageUrl;
    img.onload = () => {
        let infoText = '';
        if (imageObject.people && imageObject.people.length > 0) infoText += imageObject.people.join(' & ');
        if (imageObject.date) infoText += (infoText ? ` - ${imageObject.date}` : imageObject.date);
        infoContainer.textContent = infoText;
        infoContainer.classList.add('visible');
        
        nextBackgroundDiv.style.backgroundImage = `url('${imageUrl}')`;
        nextBackgroundDiv.style.filter = `blur(${config.blur_strength || 20}px)`;
        nextImageDiv.style.backgroundImage = `url('${imageUrl}')`;
        nextImageDiv.style.filter = config.image_filter || 'none';

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

        currentImageDiv.classList.remove('visible');
        nextImageDiv.classList.add('visible');
        currentBackgroundDiv.classList.remove('visible');
        nextBackgroundDiv.classList.add('visible');
        
        setTimeout(() => {
            currentImageDiv.style.backgroundImage = nextImageDiv.style.backgroundImage;
            currentBackgroundDiv.style.backgroundImage = nextBackgroundDiv.style.backgroundImage;
        }, config.transition_speed || 1500);
        
        setTimeout(() => { infoContainer.classList.remove('visible'); }, (config.interval || 10000) - (config.transition_speed || 1500));
        setTimeout(showNextImage, config.interval || 10000);
    };
}

async function checkBirthdays() {
    try {
        const response = await fetch('/api/birthday_info');
        const birthdayData = await response.json();
        if (birthdayData && birthdayData.name) {
            birthdayContainer.innerHTML = `${birthdayData.message}<br><span class="birthday-name">${birthdayData.name} (${birthdayData.age})</span>`;
            birthdayContainer.classList.add('visible');
        } else {
            birthdayContainer.classList.remove('visible');
        }
    } catch (error) { console.error("Hiba a születésnapok lekérdezésekor:", error); }
}

async function updateUpcomingBirthdays() {
    if (!config.show_upcoming_birthdays) {
        if (upcomingBirthdaysContainer) upcomingBirthdaysContainer.innerHTML = '';
        return;
    }
    try {
        const response = await fetch('/api/upcoming_birthdays');
        const upcoming = await response.json();
        if (upcoming.length > 0) {
            let html = '<h5>Közelgő Szülinapok</h5><ul>';
            upcoming.forEach(person => {
                let dayText = person.days_left === 0 ? 'Ma!' : (person.days_left === 1 ? 'Holnap!' : `${person.days_left} nap múlva`);
                html += `<li>🎂 ${person.name} - ${dayText}</li>`;
            });
            html += '</ul>';
            upcomingBirthdaysContainer.innerHTML = html;
        } else {
            upcomingBirthdaysContainer.innerHTML = '';
        }
    } catch (error) {
        console.error("Hiba a közelgő születésnapok lekérdezésekor:", error);
    }
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
    initializeApp();
    setInterval(updateClock, 1000);
    setInterval(checkBirthdays, 3600000); 
    setInterval(updateUpcomingBirthdays, 6 * 3600000); 
});