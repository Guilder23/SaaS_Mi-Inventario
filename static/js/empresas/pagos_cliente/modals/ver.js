/* ============================================================================
   MODAL VER PAGO CLIENTE
   ============================================================================ */

function inicializarModalVer() {
    const botones = document.querySelectorAll('.btn-ver-pago');
    if (!botones.length) return;

    botones.forEach((btn) => {
        btn.addEventListener('click', () => {
            document.getElementById('verPagoMonto').textContent = `${btn.dataset.pagoMonto || ''} ${btn.dataset.pagoMoneda || ''}`.trim();
            document.getElementById('verPagoEstado').textContent = btn.dataset.pagoEstado || '';
            document.getElementById('verPagoFecha').textContent = btn.dataset.pagoFecha || '';
            const link = document.getElementById('verPagoComprobante');
            const url = btn.dataset.pagoComprobante || '';
            if (url) {
                link.href = url;
                link.textContent = 'Ver';
                link.style.display = 'inline-block';
            } else {
                link.href = '#';
                link.textContent = 'No disponible';
                link.style.display = 'inline-block';
            }
        });
    });
}
