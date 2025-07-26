// static/birthdays_manager.js
document.addEventListener('DOMContentLoaded', () => {
    const birthdayTabButton = document.getElementById('v-pills-birthdays-tab');
    if (!birthdayTabButton) return;
    
    // Ez a funkció beállítja a gombok eseménykezelőit
    const initBirthdayTab = () => {
        // Törlés megerősítése
        document.querySelectorAll('#birthday-list .delete-person-btn').forEach(btn => {
            // Hogy ne adjuk hozzá többször ugyanazt az eseményt, előbb eltávolítjuk a régit
            const newBtn = btn.cloneNode(true);
            btn.parentNode.replaceChild(newBtn, btn);
            newBtn.addEventListener('click', function(event) {
                if (!confirm('Biztosan törlöd ezt a személyt?')) {
                    event.preventDefault();
                }
            });
        });

        // Szerkesztés gombok
        document.querySelectorAll('#birthday-list .edit-birthday-btn').forEach(btn => {
            const newBtn = btn.cloneNode(true);
            btn.parentNode.replaceChild(newBtn, btn);
            newBtn.addEventListener('click', handleEditClick);
        });

        // Mégse gombok
        document.querySelectorAll('#birthday-list .cancel-birthday-btn').forEach(btn => {
            const newBtn = btn.cloneNode(true);
            btn.parentNode.replaceChild(newBtn, btn);
            newBtn.addEventListener('click', handleCancelClick);
        });

        // Mentés gombok
        document.querySelectorAll('#birthday-list .save-birthday-btn').forEach(btn => {
            const newBtn = btn.cloneNode(true);
            btn.parentNode.replaceChild(newBtn, btn);
            newBtn.addEventListener('click', handleSaveClick);
        });
    };

    birthdayTabButton.addEventListener('shown.bs.tab', initBirthdayTab);
    if (birthdayTabButton.classList.contains('active')) initBirthdayTab();
});

function toggleEditMode(listItem, isEditing) {
    listItem.querySelector('.birthday-text').classList.toggle('d-none', isEditing);
    listItem.querySelector('.birthday-input').classList.toggle('d-none', !isEditing);
    listItem.querySelector('.edit-birthday-btn').classList.toggle('d-none', isEditing);
    listItem.querySelector('.save-birthday-btn').classList.toggle('d-none', !isEditing);
    listItem.querySelector('.cancel-birthday-btn').classList.toggle('d-none', !isEditing);
}

function handleEditClick(event) {
    const listItem = event.target.closest('.list-group-item');
    toggleEditMode(listItem, true);
}

function handleCancelClick(event) {
    const listItem = event.target.closest('.list-group-item');
    const textValue = listItem.querySelector('.birthday-text').textContent;
    listItem.querySelector('.birthday-input').value = textValue === 'Nincs megadva' ? '' : textValue.replace(/\./g, '-');
    toggleEditMode(listItem, false);
}

async function handleSaveClick(event) {
    const listItem = event.target.closest('.list-group-item');
    const personName = listItem.dataset.personName;
    const birthdayInput = listItem.querySelector('.birthday-input');
    const newBirthday = birthdayInput.value;

    try {
        const response = await fetch('/api/person/update_birthday', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: personName, birthday: newBirthday }),
        });
        const result = await response.json();

        if (result.status === 'success') {
            showToast(result.message);
            const textEl = listItem.querySelector('.birthday-text');
            textEl.textContent = newBirthday ? newBirthday.replace(/-/g, '.') : 'Nincs megadva';
            toggleEditMode(listItem, false);
            // Az oldal újratöltése frissíti a kort is
            setTimeout(() => { window.location.reload(); }, 1000);
        } else {
            showToast(result.message, 'danger');
        }
    } catch(err) {
        showToast('Hálózati hiba történt.', 'danger');
    }
}