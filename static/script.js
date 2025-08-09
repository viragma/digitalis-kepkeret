// static/script.js - JAVÍTOTT VERZIÓ

let config = {};
let imageList = [];
let currentIndex = 0;
let isPaused = false;
let currentAmbientTheme = 'none';
let currentEventTheme = 'none';

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
        const [configRes, imageListRes] = await Promise.all([ fetch('/config'), fetch('/imagelist') ]);
        config = await configRes.json();
        imageList = await imageListRes.json();
        
        // JAVÍTÁS: Inicializáljuk az órát és a közelgő születésnapokat rögtön az elején
        initializeClock();
        await checkBirthdays();
        await updateUpcomingBirthdays();
        await updateTheme();

        const transitionSpeed = (config.transition_speed || 1500) / 1000;
        currentImageDiv.style.transitionDuration = `${transitionSpeed}s`;
        nextImageDiv.style.transitionDuration = `${transitionSpeed}s`;
        currentBackgroundDiv.style.transitionDuration = `${transitionSpeed}s`;
        nextBackgroundDiv.style.transitionDuration = `${transitionSpeed}s`;

        startSlideshow();
    } catch (error) { 
        console.error("Hiba az alkalmazás inicializálása során:", error); 
    }
}

// JAVÍTÁS: Külön függvény az óra inicializálásához
function initializeClock() {
    console.log("Óra inicializálása...", config); // Debug log
    
    if (clockDiv) {
        if (config.enable_clock) {
            clockDiv.style.display = 'block';
            clockDiv.style.fontSize = config.clock_size || '2.5rem';
            console.log("Óra engedélyezve, méret:", config.clock_size); // Debug log
            updateClock(); // Azonnal frissítjük
        } else {
            clockDiv.style.display = 'none';
            console.log("Óra letiltva"); // Debug log
        }
    } else {
        console.error("Clock div nem található! Ellenőrizd az index.html-t."); // Debug log
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
    
    updateInfo(initialImageObject);
    setTimeout(showNextImage, config.interval || 10000);
}

function showNextImage() {
    if (isPaused) { setTimeout(showNextImage, 1000); return; }

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
        
        nextBackgroundDiv.style.backgroundImage = `url('${imageUrl}')`;
        nextBackgroundDiv.style.filter = `blur(${config.blur_strength || 20}px)`;
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
        }, config.transition_speed || 1500);
        
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
    if (skyThemeContainer) skyThemeContainer.innerHTML = '';
    
    switch (themeName) {
        case 'sunrise': startSunriseTheme(); break;
        case 'daytime': startDaytimeTheme(); break;
        case 'sunset': startSunsetTheme(); break;
        case 'night': startNightTheme(); break;
        default: break;
    }
}

function updateInfo(imageObject) {
    if (!infoContainer) {
        console.error("Info container nem található!");
        return;
    }
    
    let infoText = '';
    if (imageObject.people && imageObject.people.length > 0) { infoText += imageObject.people.join(' & '); }
    if (imageObject.date) { infoText += (infoText ? ` - ${imageObject.date}` : imageObject.date); }
    infoContainer.textContent = infoText;
    infoContainer.classList.add('visible');
    setTimeout(() => { infoContainer.classList.remove('visible'); }, (config.interval || 10000) - (config.transition_speed || 1500));
}

async function checkBirthdays() {
    if (!birthdayContainer) {
        console.error("Birthday container nem található!");
        return;
    }
    
    try {
        const response = await fetch('/api/birthday_info');
        const birthdayData = await response.json();
        
        console.log("Születésnap adat:", birthdayData); // Debug log
        
        if (birthdayData && birthdayData.name) {
            birthdayContainer.innerHTML = `${birthdayData.message}<br><span class="birthday-name">${birthdayData.name} (${birthdayData.age})</span>`;
            birthdayContainer.classList.add('visible');
            console.log("Születésnap megjelenítve"); // Debug log
        } else {
            birthdayContainer.classList.remove('visible');
            console.log("Nincs mai születésnap"); // Debug log
        }
    } catch (error) { 
        console.error("Hiba a születésnapok lekérdezésekor:", error); 
    }
}

async function updateUpcomingBirthdays() {
    if (!upcomingBirthdaysContainer) {
        console.error("Upcoming birthdays container nem található!");
        return;
    }
    
    console.log("Közelgő születésnapok frissítése..."); // Debug log
    
    // JAVÍTÁS: Ellenőrizzük, hogy a config már betöltődött-e
    if (!config.hasOwnProperty('show_upcoming_birthdays')) {
        console.log("Config még nem töltődött be, várakozás..."); // Debug log
        setTimeout(updateUpcomingBirthdays, 1000);
        return;
    }
    
    if (config.show_upcoming_birthdays === false) {
        upcomingBirthdaysContainer.innerHTML = '';
        console.log("Közelgő születésnapok letiltva"); // Debug log
        return;
    }
    
    try {
        const response = await fetch('/api/upcoming_birthdays');
        const upcoming = await response.json();
        
        console.log("Közelgő születésnapok:", upcoming); // Debug log
        
        if (upcoming.length > 0) {
            let html = '<h5>Közelgő Szülinapok</h5><ul>';
            upcoming.forEach(person => {
                let dayText = person.days_left === 0 ? 'Ma!' : (person.days_left === 1 ? 'Holnap!' : `${person.days_left} nap múlva`);
                html += `<li>🎂 ${person.name} - ${dayText}</li>`;
            });
            html += '</ul>';
            upcomingBirthdaysContainer.innerHTML = html;
            console.log("Közelgő születésnapok megjelenítve"); // Debug log
        } else {
            upcomingBirthdaysContainer.innerHTML = '';
            console.log("Nincs közelgő születésnap"); // Debug log
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
    } else if (!clockDiv) {
        console.error("Clock div nem található az updateClock függvényben!");
    }
}

document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM betöltődött, alkalmazás indítása..."); // Debug log
    
    initializeApp();
    
    // JAVÍTÁS: Az óra frissítését azonnal elindítjuk
    updateClock();
    setInterval(updateClock, 1000);
    
    // JAVÍTÁS: Gyakrabban ellenőrizzük a születésnapokat
    setInterval(checkBirthdays, 1800000); // 30 perc
    setInterval(updateUpcomingBirthdays, 3600000); // 1 óra
    setInterval(updateTheme, 60000);

    const socket = io();
    socket.on('reload_clients', (data) => {
        console.log('FRISSÍTÉSI PARANCS FOGADVA:', data.message);
        location.reload(true);
    });
});