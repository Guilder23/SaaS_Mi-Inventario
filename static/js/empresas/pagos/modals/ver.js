/* ============================================================================
   MODAL VER PAGO
   ============================================================================ */

function inicializarModalVer() {
    const botones = document.querySelectorAll('.btn-ver-pago');
    if (!botones.length) return;

    botones.forEach((btn) => {
        btn.addEventListener('click', () => {
            document.getElementById('verPagoEmpresa').textContent = btn.dataset.pagoEmpresa || '';
            document.getElementById('verPagoMonto').textContent = `${btn.dataset.pagoMonto || ''} ${btn.dataset.pagoMoneda || ''}`.trim();
            document.getElementById('verPagoEstado').textContent = btn.dataset.pagoEstado || '';
            document.getElementById('verPagoFecha').textContent = btn.dataset.pagoFecha || '';
            const link = document.getElementById('verPagoComprobante');
            const url = btn.dataset.pagoComprobante || '';
            const preview = document.getElementById('verPagoComprobantePreview');
            const img = document.getElementById('verPagoComprobanteImg');
            if (url) {
                link.href = url;
                link.textContent = 'Ver';
                link.style.display = 'inline-block';
                if (img) {
                    img.src = url;
                    img.alt = 'Comprobante';
                }
                if (preview) {
                    preview.style.display = 'block';
                }
            } else {
                link.href = '#';
                link.textContent = 'No disponible';
                link.style.display = 'inline-block';
                if (img) {
                    img.removeAttribute('src');
                }
                if (preview) {
                    preview.style.display = 'none';
                }
            }
        });
    });
}
