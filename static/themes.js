// static/themes.js

const themeOverlay = document.getElementById('theme-overlay');
let themeInterval;

function stopAllThemes() {
    if (themeInterval) {
        clearInterval(themeInterval);
    }
    themeOverlay.innerHTML = '';
    themeOverlay.className = '';
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