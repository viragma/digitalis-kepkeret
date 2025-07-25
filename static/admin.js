// static/admin.js - TOAST ÉRTESÍTÉSEKKEL

document.addEventListener('DOMContentLoaded', function() {
    // ... (ez a rész változatlan)
});

// ÚJ: Segédfüggvény az értesítések megjelenítéséhez
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
    // Automatikusan eltávolítjuk a HTML-ből, miután eltűnt
    newToastEl.addEventListener('hidden.bs.toast', () => {
        newToastEl.remove();
    });
}


async function loadUnknownFaces() { /* ... (változatlan) ... */ }

function setupBatchActions() {
    // ... (a gombok definíciója változatlan) ...

    batchSaveBtn.addEventListener('click', async () => {
        const selectedName = batchNameSelect.value;
        if (selectedName === 'Válassz egy nevet...') {
            showToast('Kérlek, válassz egy nevet a tömeges mentéshez!', 'warning'); // alert helyett
            return;
        }

        const selectedCards = document.querySelectorAll('.face-card.selected');
        if (selectedCards.length === 0) {
            showToast('Nincs kijelölt arc a mentéshez!', 'warning'); // alert helyett
            return;
        }

        const savePromises = Array.from(selectedCards).map(card => {
            return saveFaceName(card.dataset.facePath, selectedName, card);
        });
        
        await Promise.all(savePromises);
        // VÁLTOZÁS: alert() helyett az új showToast() függvényt hívjuk
        showToast(`${selectedCards.length} arc sikeresen mentve!`);
    });
}

async function saveFaceName(facePath, newName, cardElement) {
    try {
        // ... (fetch rész változatlan) ...
        if (result.status === 'success') {
            // ... (eltüntetés változatlan) ...
        } else {
            // VÁLTOZÁS: alert() helyett
            showToast(`Hiba: ${result.message}`, 'danger');
        }
    } catch (error) {
        // VÁLTOZÁS: alert() helyett
        console.error('Hiba az arc nevének mentésekor:', error);
        showToast('Hálózati hiba történt a mentés során.', 'danger');
    }
}