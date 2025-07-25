// ----- DIAVETÍTÉS SZEMÉLY SZŰRŐ (Choices.js keresős) -----
document.addEventListener("DOMContentLoaded", function () {
    const personsSelect = document.getElementById('persons');
    if (personsSelect) {
        const personsList = window.persons_list || [];
        const selectedPersons = window.selected_persons || [];
        personsList.forEach(name => {
            const option = document.createElement('option');
            option.value = name;
            option.textContent = name;
            if (selectedPersons.includes(name)) {
                option.selected = true;
            }
            personsSelect.appendChild(option);
        });
        new Choices(personsSelect, {
            removeItemButton: true,
            shouldSort: false,
            placeholderValue: 'Válassz személyeket...',
            searchPlaceholderValue: 'Keresés...',
            noResultsText: 'Nincs találat',
            noChoicesText: 'Nincs választható személy',
            itemSelectText: 'Kiválaszt'
        });
    }
});

// ----- KIEMELT SZEMÉLYEK FILTER BLOKK -----

async function loadHighlightPersons() {
    // persons.json beolvasása
    const resp = await fetch('/api/persons.json');
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