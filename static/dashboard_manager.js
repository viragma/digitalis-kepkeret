// static/dashboard_manager.js

document.addEventListener('DOMContentLoaded', () => {
    const dashboardTabButton = document.getElementById('v-pills-dashboard-tab');
    if (!dashboardTabButton) return;

    let isInitialized = false;

    const initDashboard = async () => {
        if (isInitialized) return;
        isInitialized = true;
        
        console.log("Műszerfal inicializálása...");

        // Eseményfigyelő a "Run Detection" gombra
        const runDetectionBtn = document.getElementById('run-detection-btn');
        runDetectionBtn.addEventListener('click', async () => {
            if (!confirm('Biztosan elindítod az arcfelismerést az összes új képen? Ez a folyamat a háttérben fog futni.')) {
                return;
            }
            
            const spinner = runDetectionBtn.querySelector('.spinner-border');
            const icon = runDetectionBtn.querySelector('.bi');
            
            spinner.classList.remove('d-none');
            icon.classList.add('d-none');
            runDetectionBtn.disabled = true;

            try {
                const response = await fetch('/api/run_face_detection', { method: 'POST' });
                const result = await response.json();
                
                if (result.status === 'success') {
                    showToast(result.message, 'success');
                } else {
                    showToast(result.message, 'danger');
                }
            } catch (error) {
                showToast('Hiba történt a script indításakor.', 'danger');
            } finally {
                setTimeout(() => {
                    spinner.classList.add('d-none');
                    icon.classList.remove('d-none');
                    runDetectionBtn.disabled = false;
                }, 5000); // 5 másodperc múlva újra engedélyezzük a gombot
            }
        });

        // Statisztikák betöltése
        try {
            const response = await fetch('/api/dashboard_stats');
            const stats = await response.json();

            document.getElementById('stat-total-images').textContent = stats.total_images;
            document.getElementById('stat-known-persons').textContent = stats.known_persons;
            document.getElementById('stat-recognized-faces').textContent = stats.recognized_faces;
            document.getElementById('stat-unknown-faces').textContent = stats.unknown_faces;

            const latestImagesContainer = document.getElementById('latest-images-container');
            if (stats.latest_images && stats.latest_images.length > 0) {
                let html = '<div class="row row-cols-3 g-2">';
                stats.latest_images.forEach(filename => {
                    html += `<div class="col"><img src="/static/images/${filename}" class="img-fluid rounded"></div>`;
                });
                html += '</div>';
                latestImagesContainer.innerHTML = html;
            } else {
                latestImagesContainer.innerHTML = '<p class="text-muted">Nincsenek feltöltött képek.</p>';
            }
        } catch (error) {
            console.error("Hiba a műszerfal statisztikáinak betöltésekor:", error);
        }
    };

    // Fülváltáskor és az oldal betöltésekor is lefut
    if (dashboardTabButton.classList.contains('active')) {
        initDashboard();
    }
    dashboardTabButton.addEventListener('shown.bs.tab', initDashboard);
});