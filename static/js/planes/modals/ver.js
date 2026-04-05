document.addEventListener('DOMContentLoaded', function () {
    const botones = document.querySelectorAll('.btn-ver-plan');
    const inputCodigo = document.getElementById('verPlanCodigo');
    const inputNombre = document.getElementById('verPlanNombre');
    const inputEstado = document.getElementById('verPlanEstado');
    const inputMaxProductos = document.getElementById('verPlanMaxProductos');
    const inputMaxUsuarios = document.getElementById('verPlanMaxUsuarios');
    const inputPrecioMensual = document.getElementById('verPlanPrecioMensual');
    const inputMoneda = document.getElementById('verPlanMoneda');
    const inputDescuentoPorcentaje = document.getElementById('verPlanDescuentoPorcentaje');
    const inputDescuentoMeses = document.getElementById('verPlanDescuentoMeses');

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

            if (inputPrecioMensual) {
                const pm = (btn.dataset.planPrecioMensual || '').trim();
                inputPrecioMensual.value = pm ? pm : 'No configurado';
            }
            if (inputMoneda) {
                inputMoneda.value = (btn.dataset.planMoneda || 'BOB').trim() || 'BOB';
            }
            if (inputDescuentoPorcentaje) {
                const dp = (btn.dataset.planDescuentoPorcentaje || '').trim();
                inputDescuentoPorcentaje.value = dp ? dp : '0';
            }
            if (inputDescuentoMeses) {
                const dm = (btn.dataset.planDescuentoMeses || '').trim();
                inputDescuentoMeses.value = dm ? dm : '-';
            }

            const rolesSpans = document.querySelectorAll('[id^="verRole__"]');
            rolesSpans.forEach(span => {
                const rol = span.id.replace('verRole__', '');
                const valor = (btn.getAttribute('data-role-' + rol) || '').trim();
                span.textContent = valor ? valor : 'Ilimitado';
            });
        });
    });
});
