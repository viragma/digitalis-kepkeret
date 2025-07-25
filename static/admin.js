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
// Feltölti a személylistát és betölti az aktuális filtert
async function loadHighlightPersons() {
    // persons.json beolvasása
    const resp = await fetch('/static/data/persons.json');
    const persons = await resp.json();
    const select = document.getElementById('highlight-persons');
    select.innerHTML = '';
    Object.keys(persons).forEach(name => {
        const opt = document.createElement('option');
        opt.value = name;
        opt.textContent = name;
        select.appendChild(opt);
    });

    // Aktuális filter betöltése
    const filterResp = await fetch('/api/highlight_filter');
    const filter = await filterResp.json();
    [...select.options].forEach(opt => {
        opt.selected = filter.names && filter.names.includes(opt.value);
    });
    document.getElementById('highlight-text').value = filter.custom_text || "";
}

document.getElementById('highlight-filter-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const select = document.getElementById('highlight-persons');
    const names = [...select.selectedOptions].map(opt => opt.value);
    const custom_text = document.getElementById('highlight-text').value;
    await fetch('/api/highlight_filter', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({names, custom_text}),
    });
    const msg = document.getElementById('highlight-saved-msg');
    msg.style.display = 'inline';
    setTimeout(() => msg.style.display = 'none', 1500);
});

document.getElementById('highlight-reset-btn').addEventListener('click', async function() {
    await fetch('/api/highlight_filter', {method: 'DELETE'});
    await loadHighlightPersons();
});

window.addEventListener('DOMContentLoaded', loadHighlightPersons);