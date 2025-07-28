// static/themes.js

const themeOverlay = document.getElementById('theme-overlay');
const skyThemeContainer = document.getElementById('sky-theme-container');
let themeInterval;

function stopAllThemes() {
    if (themeInterval) {
        clearInterval(themeInterval);
    }
    if (themeOverlay) {
        themeOverlay.innerHTML = '';
        themeOverlay.className = '';
    }
    if (skyThemeContainer) {
        skyThemeContainer.innerHTML = '';
        skyThemeContainer.className = '';
    }
}

// --- Esemény Témák ---

function startSnowTheme() {
    themeOverlay.classList.add('theme-snow');
    for (let i = 0; i < 100; i++) {
        createSnowflake();
    }
}

function startConfettiTheme() {
    themeOverlay.classList.add('theme-confetti');
    for (let i = 0; i < 50; i++) {
        createConfetti();
    }
}

function startBalloonsTheme() {
    themeOverlay.classList.add('theme-balloons');
    themeInterval = setInterval(() => {
        if (themeOverlay.children.length < 20) {
            createBalloon();
        }
    }, 700);
}

function startFireworksTheme() {
    themeOverlay.classList.add('theme-fireworks');
    themeInterval = setInterval(() => {
        if (themeOverlay.children.length < 15) {
            createFirework();
        }
    }, 500);
}

function startEasterTheme() {
    themeOverlay.classList.add('theme-eggs');
    themeInterval = setInterval(() => {
        if (themeOverlay.children.length < 25) {
            createEgg();
        }
    }, 600);
}

// --- Időjárás Témák ---

function startRainTheme() {
    themeOverlay.classList.add('theme-rain');
    for (let i = 0; i < 100; i++) {
        createRaindrop();
    }
}

function startClearTheme() {
    themeOverlay.classList.add('theme-clear');
    createSunbeam();
}

function startCloudsTheme() {
    themeOverlay.classList.add('theme-clouds');
    for (let i = 0; i < 5; i++) createCloud('slow');
    for (let i = 0; i < 5; i++) createCloud('medium');
    for (let i = 0; i < 3; i++) createCloud('fast');
}

function startAtmosphereTheme() {
    themeOverlay.classList.add('theme-atmosphere');
}

function startThunderstormTheme() {
    startRainTheme();
    themeOverlay.classList.add('theme-thunderstorm');
    createLightning();
}

// --- Napszak Témák ("Élő Égbolt") ---

function startSunriseTheme() {
    skyThemeContainer.className = 'sky-sunrise';
    const gradient = document.createElement('div');
    gradient.className = 'sky-gradient';
    skyThemeContainer.appendChild(gradient);
    setTimeout(() => gradient.classList.add('visible'), 100);
}

function startDaytimeTheme() {
    // Nappal nincs extra effekt, a háttér tiszta
}

function startSunsetTheme() {
    skyThemeContainer.className = 'sky-sunset';
    const gradient = document.createElement('div');
    gradient.className = 'sky-gradient';
    skyThemeContainer.appendChild(gradient);
    setTimeout(() => gradient.classList.add('visible'), 100);
}

function startNightTheme() {
    skyThemeContainer.className = 'sky-night';
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
        case 'fast':
            scale = Math.random() * 0.4 + 0.8;
            duration = Math.random() * 20 + 20;
            opacity = Math.random() * 0.3 + 0.5;
            cloud.style.top = `${Math.random() * 15}vh`;
            break;
        case 'medium':
            scale = Math.random() * 0.3 + 0.5;
            duration = Math.random() * 30 + 40;
            opacity = Math.random() * 0.2 + 0.3;
            cloud.style.top = `${Math.random() * 10 + 5}vh`;
            break;
        default:
            scale = Math.random() * 0.3 + 0.2;
            duration = Math.random() * 40 + 70;
            opacity = Math.random() * 0.2 + 0.1;
            cloud.style.top = `${Math.random() * 5 + 10}vh`;
            break;
    }
    cloud.style.transform = `scale(${scale})`;
    cloud.style.width = '200px';
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
    star.style.setProperty('--x', Math.random());
    star.style.setProperty('--y', Math.random());
    star.style.setProperty('--o', Math.random() * 0.6 + 0.2);
    star.style.width = `${Math.random() * 2 + 1}px`;
    star.style.height = star.style.width;
    star.style.animationDuration = `${Math.random() * 5 + 3}s`;
    star.style.animationDelay = `${Math.random() * 5}s`;
    skyThemeContainer.appendChild(star);
}