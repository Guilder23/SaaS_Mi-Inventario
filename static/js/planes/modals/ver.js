document.addEventListener('DOMContentLoaded', function () {
    const botones = document.querySelectorAll('.btn-ver-plan');
    const inputCodigo = document.getElementById('verPlanCodigo');
    const inputNombre = document.getElementById('verPlanNombre');
    const inputEstado = document.getElementById('verPlanEstado');
    const inputMaxProductos = document.getElementById('verPlanMaxProductos');
    const inputMaxUsuarios = document.getElementById('verPlanMaxUsuarios');

    if (!botones.length) return;

    botones.forEach(btn => {
        btn.addEventListener('click', () => {
            const activo = (btn.dataset.planActivo === 'True');

            inputCodigo.value = btn.dataset.planCodigo || '';
            inputNombre.value = btn.dataset.planNombre || '';
            inputEstado.value = activo ? 'Activo' : 'Inactivo';

            const mp = (btn.dataset.planMaxProductos || '').trim();
            const mu = (btn.dataset.planMaxUsuarios || '').trim();
            inputMaxProductos.value = mp ? mp : 'Ilimitado';
            inputMaxUsuarios.value = mu ? mu : 'Ilimitado';

            const rolesSpans = document.querySelectorAll('[id^="verRole__"]');
            rolesSpans.forEach(span => {
                const rol = span.id.replace('verRole__', '');
                const valor = (btn.getAttribute('data-role-' + rol) || '').trim();
                span.textContent = valor ? valor : 'Ilimitado';
            });
        });
    });
});
