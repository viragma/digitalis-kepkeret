// static/admin.js - ÁLTALÁNOS FUNKCIÓK

/**
 * Megjelenít egy Bootstrap Toast értesítést.
 * @param {string} message Az üzenet szövege.
 * @param {string} category A Bootstrap színkategória (success, warning, danger, stb.).
 */
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
