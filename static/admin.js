// static/admin.js

document.addEventListener('DOMContentLoaded', () => {
    const settingsTabButton = document.getElementById('v-pills-settings-tab');
    if (settingsTabButton) {
        const initSettingsTab = () => {
            const reloadBtn = document.getElementById('force-reload-btn');
            if (reloadBtn) {
                // Hogy ne adjuk hozzá többször az eseményfigyelőt, lecseréljük a gombot a klónjára
                const newReloadBtn = reloadBtn.cloneNode(true);
                reloadBtn.parentNode.replaceChild(newReloadBtn, reloadBtn);
                
                newReloadBtn.addEventListener('click', async () => {
                    showToast('Frissítési parancs küldése...', 'info');
                    try {
                        const response = await fetch('/api/force_reload', { method: 'POST' });
                        const result = await response.json();
                        if (result.status === 'success') {
                            showToast(result.message);
                        } else {
                            showToast(result.message, 'danger');
                        }
                    } catch (err) {
                        showToast('Hiba a parancs küldésekor.', 'danger');
                    }
                });
            }
        };

        settingsTabButton.addEventListener('shown.bs.tab', initSettingsTab);
        if (settingsTabButton.classList.contains('active')) {
            initSettingsTab();
        }
    }
});

function showToast(message, category = 'success') {
    const toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) return;

    const toastHTML = `
        <div class="toast align-items-center text-bg-${category} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>`;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    const newToastEl = toastContainer.lastElementChild;
    const newToast = new bootstrap.Toast(newToastEl, { delay: 3000 });
    newToast.show();
    
    newToastEl.addEventListener('hidden.bs.toast', () => {
        newToastEl.remove();
    });
}