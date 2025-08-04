// static/dashboard_manager.js

document.addEventListener('DOMContentLoaded', () => {
    const dashboardTabButton = document.getElementById('v-pills-dashboard-tab');
    if (!dashboardTabButton) return;

    let isInitialized = false;
    let systemStatsInterval;
    let eventLogInterval;

    const updateSystemStats = async () => {
        try {
            const response = await fetch('/api/system_stats');
            const stats = await response.json();
            if (stats.error) {
                if (systemStatsInterval) clearInterval(systemStatsInterval);
                return;
            }
            const diskProgress = document.getElementById('stat-disk-progress');
            diskProgress.style.width = `${stats.disk.percent}%`;
            diskProgress.textContent = `${stats.disk.percent}%`;
            document.getElementById('stat-disk-info').textContent = `${stats.disk.free_gb} GB szabad`;
            const memProgress = document.getElementById('stat-memory-progress');
            memProgress.style.width = `${stats.memory.percent}%`;
            memProgress.textContent = `${stats.memory.percent}%`;
            document.getElementById('stat-memory-info').textContent = `${stats.memory.total_gb} GB összesen`;
            const cpuProgress = document.getElementById('stat-cpu-progress');
            cpuProgress.style.width = `${stats.cpu.percent}%`;
            cpuProgress.textContent = `${stats.cpu.percent}%`;
            document.getElementById('stat-images-size').textContent = `${stats.images_folder_size_mb} MB`;
            document.getElementById('stat-faces-size').textContent = `${stats.faces_folder_size_mb} MB`;
        } catch (error) {
            console.error("Hiba a rendszeradatok frissítésekor:", error);
            if (systemStatsInterval) clearInterval(systemStatsInterval);
        }
    };
    
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

    const loadStaticDashboardData = async () => {
        try {
            const response = await fetch('/api/dashboard_stats');
            const stats = await response.json();

            document.getElementById('stat-total-images').textContent = stats.total_images;
            document.getElementById('stat-known-persons').textContent = stats.known_persons;
            document.getElementById('stat-recognized-faces').textContent = stats.recognized_faces;
            document.getElementById('stat-unknown-faces').textContent = stats.unknown_faces;

            const latestImagesContainer = document.getElementById('latest-images-container');
            if (latestImagesContainer) {
                if (stats.latest_images && stats.latest_images.length > 0) {
                    let html = '<div class="row row-cols-5 g-2">';
                    stats.latest_images.forEach(filename => {
                        html += `<div class="col"><img src="/static/images/${filename}" class="img-fluid rounded"></div>`;
                    });
                    html += '</div>';
                    latestImagesContainer.innerHTML = html;
                } else {
                    latestImagesContainer.innerHTML = '<p class="text-muted">Nincsenek feltöltött képek.</p>';
                }
            }

            if (stats.model_stats) {
                const trainingStatsList = document.getElementById('model-training-stats');
                const confidenceList = document.getElementById('model-confidence-list');

                if (trainingStatsList) {
                    let retrainStatusHTML = stats.model_stats.retrain_needed 
                        ? '<span class="badge bg-danger">Újratanítás szükséges</span>' 
                        : '<span class="badge bg-success">Naprakész</span>';

                    trainingStatsList.innerHTML = `
                        <li class="list-group-item bg-transparent d-flex justify-content-between align-items-center">Modell állapota: ${retrainStatusHTML}</li>
                        <li class="list-group-item bg-transparent d-flex justify-content-between align-items-center">Ismert személyek száma: <span class="badge bg-primary rounded-pill">${stats.known_persons}</span></li>
                        <li class="list-group-item bg-transparent d-flex justify-content-between align-items-center">Összes tanítókép: <span class="badge bg-primary rounded-pill">${stats.model_stats.total_training_images}</span></li>
                        <li class="list-group-item bg-transparent d-flex justify-content-between align-items-center">Utolsó tanítás: <span class="badge bg-secondary rounded-pill">${stats.model_stats.last_training_time || 'Soha'}</span></li>
                    `;
                }

                if (confidenceList) {
                    if (stats.model_stats.confidence_data.length > 0) {
                        let confidenceHTML = '';
                        stats.model_stats.confidence_data.forEach(person => {
                            let barClass = 'low';
                            if (person.confidence > 85) barClass = 'good';
                            else if (person.confidence > 70) barClass = 'medium';
                            
                            confidenceHTML += `
                                <div class="mb-2">
                                    <div class="d-flex justify-content-between">
                                        <span>${person.name}</span>
                                        <span class="fw-bold">${person.confidence}%</span>
                                    </div>
                                    <div class="confidence-bar">
                                        <div class="confidence-bar-inner ${barClass}" style="width: ${person.confidence}%;"></div>
                                    </div>
                                    <small class="text-muted">${person.face_count} felismert arc alapján</small>
                                </div>
                            `;
                        });
                        confidenceList.innerHTML = confidenceHTML;
                    } else {
                        confidenceList.innerHTML = '<p class="text-muted">Még nincsenek adatok a felismerési pontosságról. Futtasd az arcfelismerést a statisztikák generálásához.</p>';
                    }
                }
            }
            
        } catch (error) {
            console.error("Hiba a műszerfal statisztikáinak betöltésekor:", error);
        }
    };

    const initDashboard = () => {
        if (isInitialized) return;
        isInitialized = true;
        
        const runDetectionBtn = document.getElementById('run-detection-btn');
        const retrainBtn = document.getElementById('retrain-model-btn');
        
        if (runDetectionBtn) {
            runDetectionBtn.addEventListener('click', () => handleScriptRun(runDetectionBtn, '/api/run_face_detection', 'Biztosan elindítod az arcfelismerést az összes új képen?'));
        }
        if (retrainBtn) {
            retrainBtn.addEventListener('click', () => handleScriptRun(retrainBtn, '/api/retrain_model', 'Biztosan újraépíted a tanítási adatbázist? Ez eltarthat egy ideig.'));
        }

        loadStaticDashboardData();
        updateSystemStats();
        updateEventLog();
        systemStatsInterval = setInterval(updateSystemStats, 2000);
        eventLogInterval = setInterval(updateEventLog, 10000);
    };
    
    async function handleScriptRun(button, endpoint, confirmMessage) {
        if (!confirm(confirmMessage)) return;
        
        const spinner = button.querySelector('.spinner-border');
        const icon = button.querySelector('.bi');
        spinner.classList.remove('d-none');
        icon.classList.add('d-none');
        button.disabled = true;

        try {
            const response = await fetch(endpoint, { method: 'POST' });
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
                button.disabled = false;
            }, 5000);
        }
    }

    const stopDashboardUpdates = () => {
        clearInterval(systemStatsInterval);
        clearInterval(eventLogInterval);
        isInitialized = false;
    };

    if (dashboardTabButton.classList.contains('active')) {
        initDashboard();
    }
    dashboardTabButton.addEventListener('shown.bs.tab', initDashboard);
    
    document.querySelectorAll('button[data-bs-toggle="pill"]').forEach(tab => {
        if (tab.id !== dashboardTabButton.id) {
            tab.addEventListener('shown.bs.tab', stopDashboardUpdates);
        }
    });
});