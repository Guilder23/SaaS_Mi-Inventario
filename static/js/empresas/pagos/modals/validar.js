/* ============================================================================
   MODAL VALIDAR PAGO
   ============================================================================ */

function inicializarModalValidar() {
    const botones = document.querySelectorAll('.btn-validar-pago');
    if (!botones.length) return;

    botones.forEach((btn) => {
        btn.addEventListener('click', () => {
            const action = btn.dataset.action || '';
            const empresa = btn.dataset.pagoEmpresa || '';
            const texto = action === 'aprobar_pago'
                ? `Se aprobara el pago de ${empresa}.`
                : `Se rechazara el pago de ${empresa}.`;

            document.getElementById('validarPagoAction').value = action;
            document.getElementById('validarPagoId').value = btn.dataset.pagoId || '';
            document.getElementById('validarPagoTexto').textContent = texto;
            document.getElementById('validarPagoBtn').textContent = action === 'aprobar_pago' ? 'Aprobar' : 'Rechazar';
        });
    });
}
