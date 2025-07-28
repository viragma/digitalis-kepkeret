// static/themes.js

const themeOverlay = document.getElementById('theme-overlay');
let themeInterval;

function stopAllThemes() {
    if (themeInterval) {
        clearInterval(themeInterval);
    }
    if (themeOverlay) {
        themeOverlay.innerHTML = '';
        themeOverlay.className = '';
    }
}

function startSnowTheme() {
    stopAllThemes();
    themeOverlay.classList.add('theme-snow');
    for (let i = 0; i < 100; i++) {
        createSnowflake();
    }
}

function startConfettiTheme() {
    stopAllThemes();
    themeOverlay.classList.add('theme-confetti');
    for (let i = 0; i < 50; i++) {
        createConfetti();
    }
}

function startBalloonsTheme() {
    stopAllThemes();
    themeOverlay.classList.add('theme-balloons');
    themeInterval = setInterval(() => {
        if (themeOverlay.children.length < 20) {
            createBalloon();
        }
    }, 700);
}

function startFireworksTheme() {
    stopAllThemes();
    themeOverlay.classList.add('theme-fireworks');
    themeInterval = setInterval(() => {
        if (themeOverlay.children.length < 15) {
            createFirework();
        }
    }, 500);
}

function startEasterTheme() {
    stopAllThemes();
    themeOverlay.classList.add('theme-eggs');
    themeInterval = setInterval(() => {
        if (themeOverlay.children.length < 25) {
            createEgg();
        }
    }, 600);
}

function startRainTheme() {
    stopAllThemes();
    themeOverlay.classList.add('theme-rain');
    for (let i = 0; i < 100; i++) {
        createRaindrop();
    }
}

function startClearTheme() {
    stopAllThemes();
    themeOverlay.classList.add('theme-clear');
    createSunbeam();
}

function startCloudsTheme() {
    stopAllThemes();
    themeOverlay.classList.add('theme-clouds');
    // Több rétegben, különböző sebességgel és méretben hozzuk létre a felhőket
    for (let i = 0; i < 5; i++) createCloud('slow');   // Távoli, lassú felhők
    for (let i = 0; i < 5; i++) createCloud('medium'); // Középső réteg
    for (let i = 0; i < 3; i++) createCloud('fast');   // Közeli, gyors felhők
}

function startAtmosphereTheme() {
    stopAllThemes();
    themeOverlay.classList.add('theme-atmosphere');
}

function startThunderstormTheme() {
    stopAllThemes();
    startRainTheme(); // Az eső a vihar része
    themeOverlay.classList.add('theme-thunderstorm');
    createLightning();
}


// --- Napszak Témák ---
function startSunriseTheme() {
    stopAllThemes();
    document.body.style.setProperty('--sky-gradient', 'linear-gradient(to top, rgba(255, 236, 210, 0) 0%, rgba(255, 204, 188, 0.4) 100%)');
}
function startDaytimeTheme() {
    stopAllThemes();
    // Nappal nincs extra effekt, a háttér tiszta
}
function startSunsetTheme() {
    stopAllThemes();
    document.body.style.setProperty('--sky-gradient', 'linear-gradient(to top, rgba(255, 126, 95, 0) 0%, rgba(255, 107, 107, 0.4) 100%)');
}
function startNightTheme() {
    stopAllThemes();
    themeOverlay.classList.add('theme-night');
    for (let i = 0; i < 100; i++) {
        createStar();
    }
}


// --- Létrehozó segédfüggvények ---

function createSnowflake() {
    const snowflake = document.createElement('div');
    snowflake.className = 'snowflake';
    snowflake.style.left = `${Math.random() * 100}vw`;
    snowflake.style.animationDuration = `${Math.random() * 10 + 5}s`;
    snowflake.style.animationDelay = `${Math.random() * 5}s`;
    snowflake.style.opacity = Math.random();
    themeOverlay.appendChild(snowflake);
}

function createConfetti() {
    const confetti = document.createElement('div');
    confetti.className = 'confetti';
    confetti.style.left = `${Math.random() * 100}vw`;
    confetti.style.animationDuration = `${Math.random() * 3 + 2}s`;
    confetti.style.animationDelay = `${Math.random() * 3}s`;
    confetti.style.backgroundColor = `hsl(${Math.random() * 360}, 100%, 50%)`;
    themeOverlay.appendChild(confetti);
}

function createBalloon() {
    const balloon = document.createElement('div');
    balloon.className = 'balloon';
    balloon.style.left = `${Math.random() * 90}vw`;
    balloon.style.animationDuration = `${Math.random() * 8 + 8}s`;
    balloon.style.animationDelay = `${Math.random() * 2}s`;
    const color = `hsla(${Math.random() * 360}, 100%, 60%, 0.7)`;
    balloon.style.setProperty('--balloon-color', color);
    themeOverlay.appendChild(balloon);
    setTimeout(() => balloon.remove(), (parseFloat(balloon.style.animationDuration) + parseFloat(balloon.style.animationDelay)) * 1000);
}

function createFirework() {
    const firework = document.createElement('div');
    firework.className = 'firework';
    firework.style.left = `${Math.random() * 90 + 5}vw`;
    firework.style.top = `${Math.random() * 50 + 10}vh`;
    firework.style.borderColor = `hsl(${Math.random() * 360}, 100%, 50%)`;
    themeOverlay.appendChild(firework);
    setTimeout(() => firework.remove(), 1000);
}

function createEgg() {
    const egg = document.createElement('div');
    egg.className = 'egg';
    egg.style.left = `${Math.random() * 90}vw`;
    egg.style.animationDuration = `${Math.random() * 6 + 6}s`;
    egg.style.animationDelay = `${Math.random() * 4}s`;
    egg.style.backgroundColor = `hsl(${Math.random() * 360}, 100%, 75%)`;
    themeOverlay.appendChild(egg);
}

function createRaindrop() {
    const raindrop = document.createElement('div');
    raindrop.className = 'raindrop';
    raindrop.style.left = `${Math.random() * 100}vw`;
    raindrop.style.animationDuration = `${Math.random() * 0.5 + 0.3}s`;
    raindrop.style.animationDelay = `${Math.random() * 5}s`;
    themeOverlay.appendChild(raindrop);
}

function createSunbeam() {
    const sunbeam = document.createElement('div');
    sunbeam.className = 'sunbeam';
    themeOverlay.appendChild(sunbeam);
}

function createCloud(speedTier) {
    const cloud = document.createElement('div');
    cloud.className = 'cloud';
    
    let scale, duration, opacity;
    switch (speedTier) {
        case 'fast': // Közeli felhők
            scale = Math.random() * 0.4 + 0.8; // 0.8x - 1.2x méret
            duration = Math.random() * 20 + 20; // 20-40s sebesség
            opacity = Math.random() * 0.3 + 0.5; // 0.5 - 0.8 láthatóság
            cloud.style.top = `${Math.random() * 15}vh`;
            break;
        case 'medium': // Középső réteg
            scale = Math.random() * 0.3 + 0.5; // 0.5x - 0.8x méret
            duration = Math.random() * 30 + 40; // 40-70s sebesség
            opacity = Math.random() * 0.2 + 0.3; // 0.3 - 0.5 láthatóság
            cloud.style.top = `${Math.random() * 10 + 5}vh`;
            break;
        default: // Távoli, lassú felhők
            scale = Math.random() * 0.3 + 0.2; // 0.2x - 0.5x méret
            duration = Math.random() * 40 + 70; // 70-110s sebesség
            opacity = Math.random() * 0.2 + 0.1; // 0.1 - 0.3 láthatóság
            cloud.style.top = `${Math.random() * 5 + 10}vh`;
            break;
    }
    
    cloud.style.transform = `scale(${scale})`;
    cloud.style.width = '200px'; // Fix szélesség, a scale változtatja a méretet
    cloud.style.height = '100px';
    cloud.style.animationDuration = `${duration}s`;
    cloud.style.animationDelay = `-${Math.random() * duration}s`;
    cloud.style.opacity = opacity;
    
    themeOverlay.appendChild(cloud);
}

function createLightning() {
    const lightning = document.createElement('div');
    lightning.className = 'lightning';
    themeOverlay.appendChild(lightning);
}

function createStar() {
    const star = document.createElement('div');
    star.className = 'star';
    star.style.left = `${Math.random() * 100}vw`;
    star.style.top = `${Math.random() * 100}vh`;
    star.style.width = `${Math.random() * 2 + 1}px`;
    star.style.height = star.style.width;
    star.style.animationDuration = `${Math.random() * 5 + 3}s`;
    star.style.animationDelay = `${Math.random() * 5}s`;
    themeOverlay.appendChild(star);
}