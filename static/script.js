// static/script.js

document.addEventListener('DOMContentLoaded', () => {
    let config = {};
    let imageList = [];
    let currentIndex = 0;
    let slideInterval;
    let startTime;
    let currentAmbientTheme = 'none';
    let currentEventTheme = 'none';

    // DOM Elemek
    const currentImage = document.getElementById('current-image');
    const nextImage = document.getElementById('next-image');
    const currentBackground = document.getElementById('current-background');
    const nextBackground = document.getElementById('next-background');
    const progressFill = document.getElementById('progress-fill');
    const timeDisplay = document.getElementById('time-display');
    const infoPanel = document.getElementById('info-panel');
    const timeEl = document.getElementById('time');
    const dateEl = document.getElementById('date');
    const birthdayNotification = document.getElementById('birthday-notification');
    const birthdayNameEl = document.getElementById('birthday-name');
    const birthdayTitleEl = document.getElementById('birthday-title');
    const upcomingPanel = document.getElementById('upcoming-panel');
    const upcomingList = document.getElementById('upcoming-list');
    
    // --- FŐ INICIALIZÁLÓ FUNKCIÓ ---
    async function initializeApp() {
        try {
            const [configRes, imageListRes] = await Promise.all([fetch('/config'), fetch('/imagelist')]);
            config = await configRes.json();
            imageList = await imageListRes.json();
            
            slideInterval = config.interval || 10000;

            if (imageList.length > 0) {
                preloadImages();
                changeImage(true);
                setInterval(changeImage, slideInterval);
            }

            // UI frissítők
            updateClock();
            checkBirthdays();
            updateUpcomingBirthdays();
            updateTheme();
            
            setInterval(updateClock, 1000);
            setInterval(updateProgress, 100);
            setInterval(checkBirthdays, 3600000);
            setInterval(updateUpcomingBirthdays, 1800000); // 30 percenként
            setInterval(updateTheme, 60000);

            timeDisplay.classList.add('visible'); // Óra mindig látszik
        } catch (error) {
            console.error("Hiba az alkalmazás inicializálása során:", error);
        }
    }

    // --- KÉPKEZELÉS ---
    function preloadImages() {
        imageList.forEach(imgObject => {
            const img = new Image();
            img.src = `/static/images/${imgObject.file}`;
        });
    }

    function changeImage(isFirst = false) {
        if (imageList.length === 0) return;
        
        const nextIndex = isFirst ? 0 : (currentIndex + 1) % imageList.length;
        const imageObject = imageList[nextIndex];
        const imageUrl = `/static/images/${imageObject.file}`;
        
        // Háttér és fő kép beállítása
        nextImage.style.backgroundImage = `url('${imageUrl}')`;
        nextBackground.style.backgroundImage = `url('${imageUrl}')`;
        nextBackground.style.filter = `blur(${config.blur_strength || 20}px)`;
        
        if (isFirst) {
            currentImage.style.backgroundImage = `url('${imageUrl}')`;
            currentBackground.style.backgroundImage = `url('${imageUrl}')`;
            currentBackground.style.filter = `blur(${config.blur_strength || 20}px)`;
            currentBackground.classList.add('visible');
        } else {
            nextImage.classList.add('active');
            currentImage.classList.remove('active');
            nextBackground.classList.add('visible');
            currentBackground.classList.remove('visible');
        }
        
        setTimeout(() => {
            currentImage.style.backgroundImage = nextImage.style.backgroundImage;
            currentBackground.style.backgroundImage = nextBackground.style.backgroundImage;
            currentImage.classList.add('active');
            nextImage.classList.remove('active');
            currentBackground.classList.add('visible');
            nextBackground.classList.remove('visible');
            currentIndex = nextIndex;
            updateInfoPanel(imageObject);
        }, isFirst ? 0 : 3000);

        startTime = Date.now();
    }

    // --- UI FRISSÍTŐ FUNKCIÓK ---
    function updateClock() {
        const now = new Date();
        const timeString = now.toLocaleTimeString('hu-HU', { hour: '2-digit', minute: '2-digit', hour12: false });
        const dateString = now.toLocaleDateString('hu-HU', { month: 'long', day: 'numeric', weekday: 'long' });
        timeEl.textContent = timeString;
        dateEl.textContent = dateString;
    }

    function updateProgress() {
        if (!startTime) return;
        const elapsed = Date.now() - startTime;
        const progress = (elapsed / slideInterval) * 100;
        progressFill.style.width = `${Math.min(progress, 100)}%`;
        if (progress >= 100) {
            progressFill.style.transition = 'none';
            progressFill.style.width = '0%';
            setTimeout(() => {
                progressFill.style.transition = 'width 0.1s linear';
            }, 50);
        }
    }
    
    function updateInfoPanel(imageObject) {
        let infoText = '';
        if (imageObject.people && imageObject.people.length > 0) infoText += imageObject.people.join(' & ');
        if (imageObject.date) infoText += (infoText ? ` - ${imageObject.date}` : imageObject.date);
        infoPanel.textContent = infoText;
        
        infoPanel.classList.add('visible');
        setTimeout(() => {
            infoPanel.classList.remove('visible');
        }, (slideInterval * (config.info_panel_duration_ratio || 50)) / 100);
    }

    async function checkBirthdays() {
        try {
            const response = await fetch('/api/birthday_info');
            const birthdayData = await response.json();
            if (birthdayData && birthdayData.name) {
                showBirthdayNotification(birthdayData);
            }
        } catch (error) { console.error("Hiba a születésnapok lekérdezésekor:", error); }
    }

    async function updateUpcomingBirthdays() {
        if (!config.show_upcoming_birthdays) {
            upcomingList.innerHTML = ''; return;
        }
        try {
            const response = await fetch('/api/upcoming_birthdays');
            const upcoming = await response.json();
            upcomingList.innerHTML = '';
            if (upcoming.length > 0) {
                upcoming.forEach(person => {
                    const li = document.createElement('li');
                    li.className = 'upcoming-item';
                    let dayText = person.days_left === 0 ? 'Ma!' : (person.days_left === 1 ? 'Holnap!' : `${person.days_left} nap múlva`);
                    li.textContent = `${person.name} - ${dayText}`;
                    upcomingList.appendChild(li);
                });
                showUpcomingPanel();
            }
        } catch (error) { console.error("Hiba a közelgő születésnapok lekérdezésekor:", error); }
    }

    function showUpcomingPanel() {
        if(upcomingList.children.length === 0) return;
        upcomingPanel.classList.add('slide-in');
        setTimeout(() => {
            upcomingPanel.classList.remove('slide-in');
        }, (config.upcoming_panel_duration || 12) * 1000);
    }

    function showBirthdayNotification(birthdayData) {
        birthdayTitleEl.textContent = birthdayData.message;
        birthdayNameEl.textContent = `${birthdayData.name} (${birthdayData.age})`;
        birthdayNotification.classList.add('show');
        setTimeout(() => {
            birthdayNotification.classList.remove('show');
        }, (config.birthday_notification_duration || 8) * 1000);
    }

    // --- TÉMA MOTOR ---
    async function updateTheme() {
        try {
            const response = await fetch('/api/active_theme');
            const themes = await response.json();

            if (themes.event_theme.name !== currentEventTheme) {
                currentEventTheme = themes.event_theme.name;
                applyEventTheme(themes.event_theme);
            }

            if (themes.ambient_theme !== currentAmbientTheme) {
                currentAmbientTheme = themes.ambient_theme;
                applyAmbientTheme(themes.ambient_theme);
            }
        } catch (error) {
            console.error("Hiba a téma frissítésekor:", error);
        }
    }    
    function applyEventTheme(theme) {
        if (typeof stopAllThemes === 'function') stopAllThemes();
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
            case 'rain':
            case 'drizzle':
                startRainTheme();
                break;
            case 'snow':
                startSnowTheme();
                break;
            case 'clear':
                startClearTheme();
                break;
            case 'clouds':
                startCloudsTheme();
                break;
            case 'atmosphere':
                startAtmosphereTheme();
                break;
            case 'thunderstorm':
                startThunderstormTheme();
                break;
            case 'none':
            default:
                break;
        }
    }

    function applyAmbientTheme(themeName) {
        if (skyThemeContainer) skyThemeContainer.innerHTML = '';
        switch (themeName) {
            case 'sunrise': startSunriseTheme(); break;
            case 'daytime': startDaytimeTheme(); break;
            case 'sunset': startSunsetTheme(); break;
            case 'night': startNightTheme(); break;
        }
    }

    // Indítás
    initializeApp();
});