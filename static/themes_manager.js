// static/themes_manager.js

document.addEventListener('DOMContentLoaded', () => {
    const themesTabButton = document.getElementById('v-pills-themes-tab');
    if (!themesTabButton) return;

    // Ez a funkció csak akkor fut le, ha a Témák fül láthatóvá válik
    const initThemesTab = () => {
        const masterSwitch = document.getElementById('themes_enabled');
        const accordion = document.getElementById('themesAccordion');

        if (!masterSwitch || !accordion) return;

        const toggleAccordionState = () => {
            const accordionButtons = accordion.querySelectorAll('.accordion-button');
            const accordionSelects = accordion.querySelectorAll('select');

            // Ha a főkapcsoló be van kapcsolva, mindent engedélyezünk
            if (masterSwitch.checked) {
                accordion.style.opacity = '1';
                accordionButtons.forEach(btn => btn.disabled = false);
                accordionSelects.forEach(sel => sel.disabled = false);
            } else { // Ha ki van kapcsolva, mindent letiltunk és kiszürkítünk
                accordion.style.opacity = '0.5';
                accordionButtons.forEach(btn => btn.disabled = true);
                accordionSelects.forEach(sel => sel.disabled = true);
            }
        };

        // Kezdő állapot beállítása a lap betöltésekor
        toggleAccordionState();

        // Figyeljük a kapcsoló változását, és frissítjük a felületet
        masterSwitch.addEventListener('change', toggleAccordionState);
    };

    // Fülváltáskor és az oldal betöltésekor is lefut
    if (themesTabButton.classList.contains('active')) {
        initThemesTab();
    }
    themesTabButton.addEventListener('shown.bs.tab', initThemesTab);
});