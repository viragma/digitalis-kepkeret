// static/rain_effect.js

class RainDrop {
    constructor(x, y, vy, size) {
        this.x = x;
        this.y = y;
        this.vy = vy;
        this.size = size;
        this.life = 1;
    }

    draw(ctx) {
        ctx.fillStyle = `rgba(200, 200, 220, ${0.5 * this.life})`;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
    }

    update() {
        this.y += this.vy;
        this.life -= 0.01;
        return this.life > 0;
    }
}

class RainStreak {
    constructor(x, y, vy, length) {
        this.x = x;
        this.y = y;
        this.vy = vy;
        this.length = length;
        this.life = 1;
    }

    draw(ctx) {
        ctx.strokeStyle = `rgba(200, 200, 220, ${0.3 * this.life})`;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(this.x, this.y);
        ctx.lineTo(this.x, this.y + this.length);
        ctx.stroke();
    }

    update() {
        this.y += this.vy;
        this.life -= 0.005;
        return this.y < window.innerHeight && this.life > 0;
    }
}


const rainCanvas = document.getElementById('rain-canvas');
const rainCtx = rainCanvas.getContext('2d');
let rainDrops = [];
let rainStreaks = [];
let animationFrameId;

function resizeRainCanvas() {
    rainCanvas.width = window.innerWidth;
    rainCanvas.height = window.innerHeight;
}

function animateRain() {
    rainCtx.clearRect(0, 0, rainCanvas.width, rainCanvas.height);

    if (Math.random() > 0.95) {
        rainStreaks.push(new RainStreak(
            Math.random() * rainCanvas.width,
            -20,
            Math.random() * 10 + 10,
            Math.random() * 20 + 10
        ));
    }
    if (Math.random() > 0.8) {
         rainDrops.push(new RainDrop(
            Math.random() * rainCanvas.width,
            Math.random() * rainCanvas.height,
            Math.random() * 0.5 + 0.2,
            Math.random() * 1.5 + 1
        ));
    }

    rainDrops = rainDrops.filter(drop => drop.update());
    rainStreaks = rainStreaks.filter(streak => streak.update());

    [...rainDrops, ...rainStreaks].forEach(item => item.draw(rainCtx));

    animationFrameId = requestAnimationFrame(animateRain);
}

function startRealisticRain() {
    resizeRainCanvas();
    window.addEventListener('resize', resizeRainCanvas);
    
    rainDrops = [];
    rainStreaks = [];
    
    if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
    }
    animateRain();
}

function stopRealisticRain() {
    if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
    }
    window.removeEventListener('resize', resizeRainCanvas);
    rainCtx.clearRect(0, 0, rainCanvas.width, rainCanvas.height);
}