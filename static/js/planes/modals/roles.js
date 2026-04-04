document.addEventListener('DOMContentLoaded', function () {
    const botones = document.querySelectorAll('.btn-roles-plan');
    const inputPlanId = document.getElementById('rolesPlanId');
    const labelPlan = document.getElementById('rolesPlanCodigo');

    if (!botones.length) return;

    botones.forEach(btn => {
        btn.addEventListener('click', () => {
            const planId = btn.dataset.planId || '';
            const planCodigo = btn.dataset.planCodigo || '';

            inputPlanId.value = planId;
            labelPlan.textContent = planCodigo;

            const rolesInputs = document.querySelectorAll('[id^="roleLimit__"]');
            rolesInputs.forEach(input => {
                const rol = input.id.replace('roleLimit__', '');
                const valor = btn.getAttribute('data-role-' + rol) || '';
                input.value = valor;
            });
        });
    });
});
