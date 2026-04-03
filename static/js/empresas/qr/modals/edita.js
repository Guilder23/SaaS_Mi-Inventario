/* ============================================================================
   MODAL EDITAR QR
   ============================================================================ */

function inicializarModalEditarQr() {
    const input = document.getElementById('qr_imagen');
    const preview = document.getElementById('qrActual');

    if (!input || !preview) return;

    input.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.style.display = 'inline-block';
        };
        reader.readAsDataURL(file);
    });
}
