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
document.addEventListener('DOMContentLoaded', () => {
    const birthdayTab = document.getElementById('v-pills-birthdays-tab');
    if (birthdayTab) {
        // Figyeljük, mikor lesz a fül aktív
        birthdayTab.addEventListener('shown.bs.tab', () => {
            document.querySelectorAll('.delete-person-btn').forEach(button => {
                button.addEventListener('click', function(event) {
                    if (!confirm('Biztosan törlöd ezt a személyt? Ezzel az összes adatát (születésnap, profilkép) véglegesen eltávolítod.')) {
                        event.preventDefault(); // Megállítja a törlést, ha a felhasználó a "Mégse"-re kattint
                    }
                });
            });
        });
    }
});