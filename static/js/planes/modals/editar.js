document.addEventListener('DOMContentLoaded', function () {
    const botones = document.querySelectorAll('.btn-editar-plan');
    const inputId = document.getElementById('editarPlanId');
    const inputCodigo = document.getElementById('editarPlanCodigo');
    const inputNombre = document.getElementById('editarPlanNombre');
    const inputMaxProductos = document.getElementById('editarPlanMaxProductos');
    const inputMaxUsuarios = document.getElementById('editarPlanMaxUsuarios');
    const inputActivo = document.getElementById('editarPlanActivo');
    const inputPermiteModoOscuro = document.getElementById('editarPlanPermiteModoOscuro');

    if (!botones.length) return;

    botones.forEach(btn => {
        btn.addEventListener('click', () => {
            inputId.value = btn.dataset.planId || '';
            inputCodigo.value = btn.dataset.planCodigo || '';
            inputNombre.value = btn.dataset.planNombre || '';
            inputMaxProductos.value = btn.dataset.planMaxProductos || '';
            inputMaxUsuarios.value = btn.dataset.planMaxUsuarios || '';
            inputActivo.checked = (btn.dataset.planActivo === 'True');
            if (inputPermiteModoOscuro) {
                inputPermiteModoOscuro.checked = (btn.dataset.planPermiteModoOscuro === 'True');
            }
        });
    });
});
