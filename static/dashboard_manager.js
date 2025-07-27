// static/dashboard_manager.js

document.addEventListener('DOMContentLoaded', () => {
    const dashboardTabButton = document.getElementById('v-pills-dashboard-tab');
    if (!dashboardTabButton) return;

    let isInitialized = false;
    let systemStatsInterval; // Változó az időzítő tárolására
    let eventLogInterval;

    // Ez a funkció frissíti a gyorsan változó rendszeradatokat
    const updateSystemStats = async () => {
        try {
            const response = await fetch('/api/system_stats');
            const stats = await response.json();

            if (stats.error) {
                console.error("Hiba a rendszeradatok lekérdezésekor:", stats.error);
                // Ha hiba van, leállítjuk a további kéréseket, hogy ne terheljük a szervert
                if (systemStatsInterval) clearInterval(systemStatsInterval);
                return;
            }

            // Tárhely
            const diskProgress = document.getElementById('stat-disk-progress');
            diskProgress.style.width = `${stats.disk.percent}%`;
            diskProgress.textContent = `${stats.disk.percent}%`;
            document.getElementById('stat-disk-info').textContent = `${stats.disk.free_gb} GB szabad`;

            // Memória
            const memProgress = document.getElementById('stat-memory-progress');
            memProgress.style.width = `${stats.memory.percent}%`;
            memProgress.textContent = `${stats.memory.percent}%`;
            document.getElementById('stat-memory-info').textContent = `${stats.memory.total_gb} GB összesen`;
            
            // CPU
            const cpuProgress = document.getElementById('stat-cpu-progress');
            cpuProgress.style.width = `${stats.cpu.percent}%`;
            cpuProgress.textContent = `${stats.cpu.percent}%`;

            // Mappa méretek
            document.getElementById('stat-images-size').textContent = `${stats.images_folder_size_mb} MB`;
            document.getElementById('stat-faces-size').textContent = `${stats.faces_folder_size_mb} MB`;

        } catch (error) {
            console.error("Hiba a rendszeradatok frissítésekor:", error);
            if (systemStatsInterval) clearInterval(systemStatsInterval);
        }
    };
    
    // Ez a funkció a lassan változó, statikus adatokat tölti be
    const loadStaticDashboardData = async () => {
        try {
            const response = await fetch('/api/dashboard_stats');
            const stats = await response.json();

            // Felső statisztikai kártyák
            document.getElementById('stat-total-images').textContent = stats.total_images;
            document.getElementById('stat-known-persons').textContent = stats.known_persons;
            document.getElementById('stat-recognized-faces').textContent = stats.recognized_faces;
            document.getElementById('stat-unknown-faces').textContent = stats.unknown_faces;
            
        } catch (error) {
            console.error("Hiba a műszerfal statisztikáinak betöltésekor:", error);
        }
    };
    
    // Az eseménynaplót frissítő funkció
    const updateEventLog = async () => {
        try {
            const response = await fetch('/api/event_log');
            const logs = await response.json();
            const logContainer = document.getElementById('event-log-container');
            
            if (logs.length > 0) {
                logContainer.innerHTML = logs.join('<br>');
            } else {
                logContainer.innerHTML = '<span class="text-muted">A napló üres.</span>';
            }
        } catch (error) {
            console.error("Hiba az eseménynapló frissítésekor:", error);
        }
    };


    const initDashboard = () => {
        if (isInitialized) return;
        isInitialized = true;
        
        console.log("Műszerfal inicializálása...");

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
                    }, 5000);
                }
            });
        }

        // Adatok betöltése és időzítők indítása
        loadStaticDashboardData();
        updateSystemStats();
        updateEventLog();
        systemStatsInterval = setInterval(updateSystemStats, 2000); // 2 másodpercenként
        eventLogInterval = setInterval(updateEventLog, 10000); // 10 másodpercenként
    };
    
    const stopDashboardUpdates = () => {
        clearInterval(systemStatsInterval);
        clearInterval(eventLogInterval);
        isInitialized = false;
        console.log("Műszerfal frissítése leállítva.");
    };

    if (dashboardTabButton.classList.contains('active')) {
        initDashboard();
    }
    dashboardTabButton.addEventListener('shown.bs.tab', initDashboard);
    
    // Ha elhagyjuk a fület, leállítjuk a felesleges frissítést
    document.querySelectorAll('button[data-bs-toggle="pill"]').forEach(tab => {
        if (tab.id !== dashboardTabButton.id) {
            tab.addEventListener('shown.bs.tab', stopDashboardUpdates);
        }
    });
});