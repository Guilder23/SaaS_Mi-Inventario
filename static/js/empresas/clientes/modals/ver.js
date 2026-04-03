/* ============================================================================
   MODAL VER CLIENTE
   ============================================================================ */

function inicializarModalVer() {
    const botones = document.querySelectorAll('.btn-ver-cliente');
    if (!botones.length) return;

    botones.forEach((btn) => {
        btn.addEventListener('click', () => {
            document.getElementById('verClienteEmpresa').textContent = btn.dataset.empresa || '';
            document.getElementById('verClienteUsuario').textContent = btn.dataset.username || '';
            const nombre = `${btn.dataset.firstName || ''} ${btn.dataset.lastName || ''}`.trim();
            document.getElementById('verClienteNombre').textContent = nombre || '-';
            document.getElementById('verClienteCorreo').textContent = btn.dataset.email || '-';
            document.getElementById('verClienteEstado').textContent = btn.dataset.activo === 'True' ? 'Activo' : 'Inactivo';
        });
    });
}
