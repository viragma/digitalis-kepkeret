// static/realistic_rain.js - ÉLETHŰ ESŐ EFFEKT

class RealisticRainDrop {
    constructor(x, y, size, speed) {
        this.x = x;
        this.y = y;
        this.size = size;
        this.speed = speed;
        this.life = 1;
        this.opacity = Math.random() * 0.6 + 0.4;
        this.trail = []; // Nyomvonal a csepp mögött
        this.maxTrailLength = Math.floor(size * 3);
        
        // Véletlenszerű irány és zavar
        this.windDrift = (Math.random() - 0.5) * 0.5;
        this.wobble = Math.random() * 0.2;
        this.wobbleOffset = Math.random() * Math.PI * 2;
    }

    update() {
        // Nyomvonal frissítése
        this.trail.unshift({ x: this.x, y: this.y, opacity: this.opacity });
        if (this.trail.length > this.maxTrailLength) {
            this.trail.pop();
        }

        // Pozíció frissítése gravitációval és széllel
        this.y += this.speed;
        this.x += this.windDrift + Math.sin(this.y * 0.01 + this.wobbleOffset) * this.wobble;
        
        // Gyorsulás (gravitáció szimulálása)
        this.speed += 0.1;
        
        // Élettartam csökkentése
        this.life -= 0.008;
        
        return this.life > 0 && this.y < window.innerHeight + 100;
    }

    draw(ctx) {
        // Nyomvonal rajzolása
        ctx.save();
        this.trail.forEach((point, index) => {
            const trailOpacity = (this.trail.length - index) / this.trail.length * point.opacity * this.life;
            const trailSize = this.size * (0.3 + (this.trail.length - index) / this.trail.length * 0.7);
            
            ctx.globalAlpha = trailOpacity * 0.3;
            ctx.fillStyle = `rgba(200, 220, 255, ${trailOpacity})`;
            ctx.beginPath();
            ctx.ellipse(point.x, point.y, trailSize * 0.3, trailSize * 1.5, 0, 0, Math.PI * 2);
            ctx.fill();
        });
        
        // Fő csepp rajzolása
        ctx.globalAlpha = this.opacity * this.life;
        
        // Gradiens a csepphez
        const gradient = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.size);
        gradient.addColorStop(0, 'rgba(255, 255, 255, 0.9)');
        gradient.addColorStop(0.4, 'rgba(200, 220, 255, 0.8)');
        gradient.addColorStop(1, 'rgba(150, 180, 255, 0.3)');
        
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.ellipse(this.x, this.y, this.size * 0.6, this.size * 1.8, 0, 0, Math.PI * 2);
        ctx.fill();
        
        // Fénytörés effekt
        ctx.globalAlpha = this.opacity * this.life * 0.5;
        ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
        ctx.beginPath();
        ctx.ellipse(this.x - this.size * 0.2, this.y - this.size * 0.3, this.size * 0.2, this.size * 0.4, 0, 0, Math.PI * 2);
        ctx.fill();
        
        ctx.restore();
    }
}

class RainStreak {
    constructor(x, y, length, speed) {
        this.x = x;
        this.y = y;
        this.length = length;
        this.speed = speed;
        this.life = 1;
        this.width = Math.random() * 0.8 + 0.2;
        this.angle = Math.random() * 0.1 - 0.05; // Enyhe szög
    }

    update() {
        this.y += this.speed;
        this.x += this.angle * this.speed;
        this.life -= 0.006;
        
        return this.life > 0 && this.y < window.innerHeight + this.length;
    }

    draw(ctx) {
        ctx.save();
        ctx.globalAlpha = this.life * 0.4;
        
        // Gradiens vonalhoz
        const gradient = ctx.createLinearGradient(this.x, this.y, this.x, this.y + this.length);
        gradient.addColorStop(0, 'rgba(200, 220, 255, 0)');
        gradient.addColorStop(0.3, 'rgba(200, 220, 255, 0.8)');
        gradient.addColorStop(1, 'rgba(150, 180, 220, 0.2)');
        
        ctx.strokeStyle = gradient;
        ctx.lineWidth = this.width;
        ctx.lineCap = 'round';
        
        ctx.beginPath();
        ctx.moveTo(this.x, this.y);
        ctx.lineTo(this.x + this.angle * this.length, this.y + this.length);
        ctx.stroke();
        
        ctx.restore();
    }
}

class WaterDroplet {
    constructor(x, y, size) {
        this.x = x;
        this.y = y;
        this.size = size;
        this.life = 1;
        this.maxSize = size;
        this.growthRate = Math.random() * 0.1 + 0.05;
        this.slideSpeed = Math.random() * 0.5 + 0.1;
        this.slideDirection = Math.random() > 0.5 ? 1 : -1;
    }

    update() {
        // Csepp növekedése
        if (this.size < this.maxSize) {
            this.size += this.growthRate;
        }
        
        // Lecsúszás
        this.y += this.slideSpeed;
        this.x += (Math.random() - 0.5) * 0.1; // Enyhe oldalirányú mozgás
        
        this.life -= 0.003;
        
        return this.life > 0 && this.y < window.innerHeight;
    }

    draw(ctx) {
        ctx.save();
        ctx.globalAlpha = this.life * 0.7;
        
        // Csepp alakja
        const gradient = ctx.createRadialGradient(
            this.x - this.size * 0.2, 
            this.y - this.size * 0.2, 
            0,
            this.x, 
            this.y, 
            this.size
        );
        gradient.addColorStop(0, 'rgba(255, 255, 255, 0.9)');
        gradient.addColorStop(0.3, 'rgba(200, 220, 255, 0.7)');
        gradient.addColorStop(0.7, 'rgba(150, 180, 220, 0.4)');
        gradient.addColorStop(1, 'rgba(100, 150, 200, 0.1)');
        
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
        
        // Fénytörés
        ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
        ctx.beginPath();
        ctx.arc(this.x - this.size * 0.3, this.y - this.size * 0.3, this.size * 0.2, 0, Math.PI * 2);
        ctx.fill();
        
        ctx.restore();
    }
}

class RealisticRain {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.rainDrops = [];
        this.rainStreaks = [];
        this.waterDroplets = [];
        this.animationId = null;
        
        this.intensity = 0.7; // Eső intenzitása (0-1)
        this.windStrength = 0.3; // Szél erőssége
        
        this.resizeCanvas();
        window.addEventListener('resize', () => this.resizeCanvas());
    }

    resizeCanvas() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    start() {
        this.animate();
    }

    stop() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.rainDrops = [];
        this.rainStreaks = [];
        this.waterDroplets = [];
    }

    createRainDrop() {
        const size = Math.random() * 1.5 + 0.5;
        const speed = Math.random() * 8 + 12;
        const x = Math.random() * (this.canvas.width + 200) - 100;
        
        return new RealisticRainDrop(x, -20, size, speed);
    }

    createRainStreak() {
        const length = Math.random() * 150 + 50;
        const speed = Math.random() * 15 + 20;
        const x = Math.random() * (this.canvas.width + 100) - 50;
        
        return new RainStreak(x, -length, length, speed);
    }

    createWaterDroplet() {
        const size = Math.random() * 3 + 1;
        const x = Math.random() * this.canvas.width;
        const y = Math.random() * this.canvas.height * 0.3; // Felső rész
        
        return new WaterDroplet(x, y, size);
    }

    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Új elemek hozzáadása
        if (Math.random() < this.intensity * 0.3) {
            this.rainDrops.push(this.createRainDrop());
        }
        
        if (Math.random() < this.intensity * 0.4) {
            this.rainStreaks.push(this.createRainStreak());
        }
        
        if (Math.random() < this.intensity * 0.1) {
            this.waterDroplets.push(this.createWaterDroplet());
        }

        // Eső cseppek frissítése és rajzolása
        this.rainDrops = this.rainDrops.filter(drop => {
            drop.update();
            drop.draw(this.ctx);
            return drop.life > 0 && drop.y < this.canvas.height + 100;
        });

        // Eső vonalak frissítése és rajzolása
        this.rainStreaks = this.rainStreaks.filter(streak => {
            streak.update();
            streak.draw(this.ctx);
            return streak.life > 0 && streak.y < this.canvas.height + streak.length;
        });

        // Víz cseppek frissítése és rajzolása
        this.waterDroplets = this.waterDroplets.filter(droplet => {
            droplet.update();
            droplet.draw(this.ctx);
            return droplet.life > 0 && droplet.y < this.canvas.height;
        });

        this.animationId = requestAnimationFrame(() => this.animate());
    }
}

// Globális változók
let realisticRain = null;

function startRealisticRain() {
    const canvas = document.getElementById('rain-canvas');
    if (!canvas) {
        console.error('Rain canvas nem található!');
        return;
    }
    
    if (realisticRain) {
        realisticRain.stop();
    }
    
    realisticRain = new RealisticRain(canvas);
    realisticRain.start();
    
    console.log('Élethű eső elindítva');
}

function stopRealisticRain() {
    if (realisticRain) {
        realisticRain.stop();
        realisticRain = null;
        console.log('Élethű eső leállítva');
    }
}