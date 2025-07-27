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
        if (runDetectionBtn) {
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
        }

        // Statisztikák betöltése
        try {
            const response = await fetch('/api/dashboard_stats');
            const stats = await response.json();

            // Felső statisztikai kártyák
            document.getElementById('stat-total-images').textContent = stats.total_images;
            document.getElementById('stat-known-persons').textContent = stats.known_persons;
            document.getElementById('stat-recognized-faces').textContent = stats.recognized_faces;
            document.getElementById('stat-unknown-faces').textContent = stats.unknown_faces;

            // Rendszerinformációs panel
            if (stats.server_stats) {
                // Tárhely
                const diskProgress = document.getElementById('stat-disk-progress');
                diskProgress.style.width = `${stats.server_stats.disk.percent}%`;
                diskProgress.textContent = `${stats.server_stats.disk.percent}%`;
                document.getElementById('stat-disk-info').textContent = `${stats.server_stats.disk.free_gb} GB szabad`;

                // Memória
                const memProgress = document.getElementById('stat-memory-progress');
                memProgress.style.width = `${stats.server_stats.memory.percent}%`;
                memProgress.textContent = `${stats.server_stats.memory.percent}%`;
                document.getElementById('stat-memory-info').textContent = `${stats.server_stats.memory.total_gb} GB összesen`;
                
                // CPU
                const cpuProgress = document.getElementById('stat-cpu-progress');
                cpuProgress.style.width = `${stats.server_stats.cpu.percent}%`;
                cpuProgress.textContent = `${stats.server_stats.cpu.percent}%`;
            }

            // Legutóbbi képek
            const latestImagesContainer = document.getElementById('latest-images-container');
            if (stats.latest_images && stats.latest_images.length > 0) {
                let html = '<div class="row row-cols-5 g-2">'; // 5 oszlopos rács
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