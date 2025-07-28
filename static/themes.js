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
    // Időzítve hozzuk létre a lufikat, hogy ne egyszerre induljanak
    themeInterval = setInterval(() => {
        if (themeOverlay.children.length < 20) { // Limitáljuk a lufik számát
            createBalloon();
        }
    }, 700);
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

    setTimeout(() => {
        balloon.remove();
    }, (parseFloat(balloon.style.animationDuration) + parseFloat(balloon.style.animationDelay)) * 1000);
}