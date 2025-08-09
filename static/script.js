// static/script.js

let config = {};
let imageList = [];
let currentIndex = 0;
let isPaused = false;
let currentAmbientTheme = 'none';
let currentEventTheme = 'none';

// DOM elemek - BIZTONSÁGOS lekérdezés
const currentImageDiv = document.getElementById('current-image');
const nextImageDiv = document.getElementById('next-image');
const clockDiv = document.getElementById('clock');
const infoContainer = document.getElementById('info-container');
const birthdayContainer = document.getElementById('birthday-container');
const currentBackgroundDiv = document.getElementById('current-background');
const nextBackgroundDiv = document.getElementById('next-background');
const upcomingBirthdaysContainer = document.getElementById('upcoming-birthdays-container');

// ÚJ: Intelligens blur számítás
function calculateOptimalBlur(imageObject) {
    const peopleCount = imageObject.people ? imageObject.people.length : 0;
    const baseBlur = config.slideshow?.blur_strength || 35;
    
    // Ha sok ember van a képen, kevesebb blur a háttérben
    const adjustedBlur = Math.max(25, baseBlur - (peopleCount * 3));
    
    return adjustedBlur;
}

async function initializeApp() {
    try {
        const [configRes, imageListRes] = await Promise.all([ fetch('/config'), fetch('/imagelist') ]);
        config = await configRes.json();
        imageList = await imageListRes.json();
        
        await checkBirthdays();
        await updateUpcomingBirthdays();
        await updateTheme();

        const transitionSpeed = (config.transition_speed || 2000) / 1000;
        if (currentImageDiv) currentImageDiv.style.transitionDuration = `${transitionSpeed}s`;
        if (nextImageDiv) nextImageDiv.style.transitionDuration = `${transitionSpeed}s`;
        if (currentBackgroundDiv) currentBackgroundDiv.style.transitionDuration = `${transitionSpeed}s`;
        if (nextBackgroundDiv) nextBackgroundDiv.style.transitionDuration = `${transitionSpeed}s`;

        if (clockDiv) {
            if (config.enable_clock) {
                clockDiv.style.display = 'block';
                clockDiv.style.fontSize = config.clock_size || '2.5rem';
            } else {
                clockDiv.style.display = 'none';
            }
        }
        startSlideshow();
    } catch (error) { console.error("Hiba az alkalmazás inicializálása során:", error); }
}

function startSlideshow() {
    if (imageList.length === 0) return;
    if (!currentImageDiv || !currentBackgroundDiv) return; // Biztonsági ellenőrzés
    
    currentIndex = 0;
    const initialImageObject = imageList[0];
    if (!initialImageObject) return;
    
    const initialImageUrl = `/static/images/${initialImageObject.file}`;
    const initialBlur = calculateOptimalBlur(initialImageObject);
    
    currentImageDiv.style.backgroundImage = `url('${initialImageUrl}')`;
    currentBackgroundDiv.style.backgroundImage = `url('${initialImageUrl}')`;
    currentBackgroundDiv.style.filter = `blur(${initialBlur}px) brightness(0.3) saturate(1.5) contrast(1.2)`;
    currentImageDiv.classList.add('visible');
    currentBackgroundDiv.classList.add('visible');
    
    updateInfo(initialImageObject);
    setTimeout(showNextImage, config.interval || 10000);
}

function showNextImage() {
    if (isPaused) { setTimeout(showNextImage, 1000); return; }
    if (!currentImageDiv || !nextImageDiv || !currentBackgroundDiv || !nextBackgroundDiv) return;

    currentIndex = (currentIndex + 1) % imageList.length;
    const imageObject = imageList[currentIndex];
    if (!imageObject) {
        setTimeout(showNextImage, 100);
        return;
    }
    
    const imageUrl = `/static/images/${imageObject.file}`;
    
    const img = new Image();
    img.src = imageUrl;
    img.onload = () => {
        updateInfo(imageObject);
        
        // FEJLESZTETT háttér blur számítás
        const optimalBlur = calculateOptimalBlur(imageObject);
        nextBackgroundDiv.style.backgroundImage = `url('${imageUrl}')`;
        nextBackgroundDiv.style.filter = `blur(${optimalBlur}px) brightness(0.3) saturate(1.5) contrast(1.2)`;
        
        nextImageDiv.style.backgroundImage = `url('${imageUrl}')`;
        nextImageDiv.style.filter = config.image_filter || 'none';

        nextImageDiv.classList.remove('ken-burns');
        if (config.zoom_enabled) {
            nextImageDiv.style.animationDuration = (config.interval || 10000) + 'ms';
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
            currentBackgroundDiv.style.filter = nextBackgroundDiv.style.filter;
        }, config.transition_speed || 2000);
        
        setTimeout(showNextImage, config.interval || 10000);
    };
    img.onerror = () => {
        console.error("Hiba a kép betöltésekor:", imageUrl);
        setTimeout(showNextImage, 100); 
    };
}

async function updateTheme() {
    try {
        const response = await fetch('/api/active_theme');
        const themes = await response.json();

        if (themes.event_theme.name !== currentEventTheme) {
            console.log(`Esemény téma váltás: ${currentEventTheme} -> ${themes.event_theme.name}`);
            currentEventTheme = themes.event_theme.name;
            applyTheme(themes.event_theme);
        }

        if (themes.ambient_theme !== currentAmbientTheme) {
            console.log(`Napszak téma váltás: ${currentAmbientTheme} -> ${themes.ambient_theme}`);
            currentAmbientTheme = themes.ambient_theme;
            applyAmbientTheme(themes.ambient_theme);
        }

    } catch (error) {
        console.error("Hiba a téma frissítésekor:", error);
    }
}

function applyTheme(theme) {
    stopAllThemes();
    switch (theme.name) {
        case 'birthday':
            if (theme.settings.animation === 'confetti') startConfettiTheme();
            else if (theme.settings.animation === 'balloons') startBalloonsTheme();
            break;
        case 'christmas':
            if (theme.settings.animation === 'snow') startSnowTheme();
            break;
        case 'new_year_eve':
            if (theme.settings.animation === 'fireworks') startFireworksTheme();
            break;
        case 'easter':
            if (theme.settings.animation === 'eggs') startEasterTheme();
            break;
        case 'rain': case 'drizzle': startRainTheme(); break;
        case 'snow': startSnowTheme(); break;
        case 'clear': startClearTheme(); break;
        case 'clouds': startCloudsTheme(); break;
        case 'atmosphere': startAtmosphereTheme(); break;
        case 'thunderstorm': startThunderstormTheme(); break;
        case 'none': default: break;
    }
}

function applyAmbientTheme(themeName) {
    // A napszak témák a skyThemeContainer-t használják, nem törlik a többit
    const skyThemeContainer = document.getElementById('sky-theme-container');
    if (skyThemeContainer) skyThemeContainer.innerHTML = '';
    
    switch (themeName) {
        case 'sunrise': if (typeof startSunriseTheme === 'function') startSunriseTheme(); break;
        case 'daytime': if (typeof startDaytimeTheme === 'function') startDaytimeTheme(); break;
        case 'sunset': if (typeof startSunsetTheme === 'function') startSunsetTheme(); break;
        case 'night': if (typeof startNightTheme === 'function') startNightTheme(); break;
        default: break;
    }
}

function updateInfo(imageObject) {
    if (!infoContainer) return; // Biztonsági ellenőrzés
    
    let infoText = '';
    if (imageObject.people && imageObject.people.length > 0) { 
        infoText += imageObject.people.join(' & '); 
    }
    if (imageObject.date) { 
        infoText += (infoText ? ` - ${imageObject.date}` : imageObject.date); 
    }
    
    infoContainer.textContent = infoText;
    infoContainer.classList.add('visible');
    setTimeout(() => { 
        if (infoContainer) infoContainer.classList.remove('visible'); 
    }, (config.interval || 10000) - (config.transition_speed || 2000));
}

async function checkBirthdays() {
    if (!birthdayContainer) return; // Biztonsági ellenőrzés
    
    try {
        const response = await fetch('/api/birthday_info');
        const birthdayData = await response.json();
        if (birthdayData && birthdayData.name) {
            birthdayContainer.innerHTML = `${birthdayData.message}<br><span class="birthday-name">${birthdayData.name} (${birthdayData.age})</span>`;
            birthdayContainer.classList.add('visible');
        } else {
            birthdayContainer.classList.remove('visible');
        }
    } catch (error) { 
        console.error("Hiba a születésnapok lekérdezésekor:", error); 
    }
}

async function updateUpcomingBirthdays() {
    if (!upcomingBirthdaysContainer) return; // Biztonsági ellenőrzés
    
    if (config.show_upcoming_birthdays === false) {
        upcomingBirthdaysContainer.innerHTML = '';
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
    setInterval(updateTheme, 60000);

    // Socket.IO kapcsolat - ellenőrzéssel
    if (typeof io !== 'undefined') {
        const socket = io();
        socket.on('reload_clients', (data) => {
            console.log('FRISSÍTÉSI PARANCS FOGADVA:', data.message);
            location.reload(true);
        });
    }
});