document.addEventListener('DOMContentLoaded', function () {
    const botones = document.querySelectorAll('.btn-toggle-plan');

    const inputId = document.getElementById('desactivarPlanId');
    const spanCodigo = document.getElementById('desactivarPlanCodigo');
    const spanTitulo = document.getElementById('desactivarPlanTitulo');
    const spanAccionLower = document.getElementById('desactivarPlanAccionLower');
    const btnConfirmar = document.getElementById('desactivarPlanConfirmar');

    if (!botones.length) return;

    botones.forEach(btn => {
        btn.addEventListener('click', () => {
            const activo = (btn.dataset.planActivo === 'True');
            const planId = btn.dataset.planId || '';
            const codigo = btn.dataset.planCodigo || '';
            const accion = activo ? 'Desactivar' : 'Activar';
            const accionLower = activo ? 'desactivar' : 'activar';

            inputId.value = planId;
            spanCodigo.textContent = codigo;

            spanTitulo.textContent = accion + ' plan';
            btnConfirmar.textContent = accion;
            if (spanAccionLower) {
                spanAccionLower.textContent = accionLower;
            }
        });
    });
});
