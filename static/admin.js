// --- Arc mentése gomb ---
function saveFace(faceId, imageName, index) {
  const select = document.getElementById(`select_${index}`);
  const newInput = document.getElementById(`newname_${index}`);
  let selectedName = select.value;

  if (newInput.value.trim() !== '') {
    selectedName = newInput.value.trim();
  }

  if (!selectedName) {
    alert('Kérlek válassz vagy adj meg egy nevet.');
    return;
  }

  fetch('/admin/save_face', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      face_id: faceId,
      image: imageName,
      name: selectedName
    })
  })
  .then(response => response.json())
  .then(data => {
    alert(data.message);
    location.reload();
  })
  .catch(err => {
    alert('Hiba történt a mentés során.');
    console.error(err);
  });
}

// --- Interaktív visszajelzés betöltéskor ---
document.addEventListener('DOMContentLoaded', () => {
  const faceCount = document.querySelectorAll('.face-box').length;
  if (faceCount > 0) {
    console.log(`📸 Összes arc feldolgozva az oldalon: ${faceCount}`);
  } else {
    console.log('ℹ️ Nincsenek felismerendő arcok jelenleg.');
  }
});
