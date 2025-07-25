let imageList = [];
let currentIndex = 0;
let showingFirst = true;
let showingBg1 = true;

let interval = 30000;
let enableZoom = true;

const img1 = document.getElementById('image1');
const img2 = document.getElementById('image2');
const bg1 = document.getElementById('background1');
const bg2 = document.getElementById('background2');

// Konfiguráció betöltése
async function fetchConfig() {
  try {
    const res = await fetch('/config');
    const config = await res.json();

    interval = config.interval || interval;
    enableZoom = config.zoom_enabled ?? enableZoom;

    document.documentElement.style.setProperty('--zoom-duration', `${config.zoom_duration || interval}ms`);
    document.documentElement.style.setProperty('--blur-strength', `${config.blur_strength ?? 10}px`);
    document.documentElement.style.setProperty('--nozoom-scale', `${config.nozoom_scale ?? 1.6}`);
    document.documentElement.style.setProperty('--transition-speed', `${config.transition_speed ?? 3000}ms`);
    document.documentElement.style.setProperty('--image-blend-mode', config.image_blend_mode || 'normal');
    document.documentElement.style.setProperty('--image-filter', config.image_filter || 'none');
    document.documentElement.style.setProperty('--background-opacity', config.background_opacity ?? 0.4);

    const overlay = document.getElementById('overlay');
    const vignette = document.getElementById('vignette');
    const clock = document.getElementById('clock');
    const date = document.getElementById('date');

    if (overlay) overlay.style.display = config.enable_overlay ? 'block' : 'none';
    if (vignette) vignette.style.display = config.enable_vignette ? 'block' : 'none';
    if (clock) clock.style.display = config.enable_clock ? 'block' : 'none';
    if (date) date.style.display = config.enable_clock ? 'block' : 'none';
  } catch (e) {
    console.error("Nem sikerült a config betöltése:", e);
  }
}

// Képek betöltése
async function fetchImageList() {
  try {
    const res = await fetch('/imagelist');
    const list = await res.json();
    if (JSON.stringify(list) !== JSON.stringify(imageList)) {
      imageList = list;
      currentIndex = 0;
    }
  } catch (e) {
    console.error("Nem sikerült betölteni a képlistát:", e);
  }
}

// Születésnap ellenőrzés
async function checkBirthday() {
  try {
    const res = await fetch('/static/birthdays.json');
    const data = await res.json();
    const now = new Date();
    const today = `${(now.getMonth() + 1).toString().padStart(2, '0')}-${now.getDate().toString().padStart(2, '0')}`;

    const matches = data.filter(entry => entry.date === today);
    const banner = document.getElementById('birthday-banner');

    if (matches.length > 0) {
      banner.textContent = `Boldog születésnapot: ${matches.map(e => e.name).join(', ')}!`;
      banner.style.display = 'block';
    } else {
      banner.style.display = 'none';
    }
  } catch (e) {
    console.error("Nem sikerült betölteni a születésnapokat:", e);
  }
}

// Képváltás
function updateImage() {
  if (imageList.length === 0) return;

  const filename = imageList[currentIndex];
  const fullPath = `/static/images/${filename}`;

  const nextImg = showingFirst ? img2 : img1;
  const currentImg = showingFirst ? img1 : img2;

  const nextBg = showingBg1 ? bg2 : bg1;
  const currentBg = showingBg1 ? bg1 : bg2;

  const preload = new Image();
  preload.onload = () => {
    nextBg.style.backgroundImage = `url('${fullPath}')`;
    nextImg.src = fullPath;

    currentImg.classList.remove('visible');
    nextImg.classList.remove('visible', 'zoom-effect', 'nozoom-scale');

    if (enableZoom) {
      void nextImg.offsetWidth;
      nextImg.classList.add('zoom-effect');
    } else {
      nextImg.classList.add('nozoom-scale');
    }

    void nextImg.offsetWidth;
    nextImg.classList.add('visible');
    nextBg.classList.add('visible');
    currentBg.classList.remove('visible');

    showingFirst = !showingFirst;
    showingBg1 = !showingBg1;
  };

  preload.src = fullPath;
  currentIndex = (currentIndex + 1) % imageList.length;
}

// Indítás
fetchConfig().then(() => {
  fetchImageList().then(() => {
    updateImage();
    setInterval(updateImage, interval);
    setInterval(fetchImageList, 60 * 60 * 1000);
    setInterval(checkBirthday, 60 * 60 * 1000);
    checkBirthday();
  });
});

// Óra és dátum frissítés
setInterval(() => {
  const now = new Date();
  const clock = document.getElementById('clock');
  const date = document.getElementById('date');

  if (clock) {
    const h = now.getHours().toString().padStart(2, '0');
    const m = now.getMinutes().toString().padStart(2, '0');
    clock.textContent = `${h}:${m}`;
  }

  if (date) {
    const y = now.getFullYear();
    const mo = (now.getMonth() + 1).toString().padStart(2, '0');
    const d = now.getDate().toString().padStart(2, '0');
    date.textContent = `${y}.${mo}.${d}`;
  }
}, 1000);
