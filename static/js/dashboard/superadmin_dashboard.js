/* ============================================================================
   Dashboard Superadmin (SaaS)
   - Gráficas (Chart.js)
    - Scroll fade (alertas / actividad)
   ============================================================================ */

function cssVar(name, fallback) {
    const value = getComputedStyle(document.documentElement).getPropertyValue(name);
    return (value || '').trim() || fallback;
}

function getSaasData() {
    const el = document.getElementById('saasDashboardData');
    if (!el) return null;
    try {
        return JSON.parse(el.textContent);
    } catch (e) {
        console.error('No se pudo parsear saasDashboardData:', e);
        return null;
    }
}

function initCharts() {
    const data = getSaasData();
    if (!data || typeof Chart === 'undefined') return;

    const primary = cssVar('--color-primario', '#1e3a8a');
    const secondary = cssVar('--color-secundario', '#065f46');
    const info = cssVar('--color-info', '#0891b2');
    const warning = cssVar('--color-advertencia', '#d97706');
    const danger = cssVar('--color-peligro', '#dc2626');
    const text = cssVar('--color-texto', '#1f2937');
    const grid = cssVar('--color-borde', '#e5e7eb');

    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: { color: text }
            }
        },
        scales: {
            x: {
                ticks: { color: text },
                grid: { color: grid }
            },
            y: {
                ticks: { color: text },
                grid: { color: grid }
            }
        }
    };

    // A. Crecimiento de empresas (línea)
    const ctxEmp = document.getElementById('chartEmpresas');
    if (ctxEmp) {
        new Chart(ctxEmp, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Empresas',
                    data: data.empresas,
                    borderColor: primary,
                    backgroundColor: 'rgba(30, 58, 138, 0.12)',
                    fill: true,
                    tension: 0.35,
                    pointRadius: 3,
                }]
            },
            options: {
                ...commonOptions,
                scales: {
                    x: commonOptions.scales.x,
                    y: { ...commonOptions.scales.y, beginAtZero: true, ticks: { ...commonOptions.scales.y.ticks, precision: 0 } }
                }
            }
        });
    }

    // B. Ingresos por mes (barras)
    const ctxIng = document.getElementById('chartIngresos');
    if (ctxIng) {
        new Chart(ctxIng, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Ingresos (BOB)',
                    data: data.ingresos,
                    backgroundColor: info,
                }]
            },
            options: {
                ...commonOptions,
                scales: {
                    x: commonOptions.scales.x,
                    y: { ...commonOptions.scales.y, beginAtZero: true }
                }
            }
        });
    }

    // C. Distribución de planes (pie)
    const ctxPlanes = document.getElementById('chartPlanes');
    if (ctxPlanes) {
        new Chart(ctxPlanes, {
            type: 'doughnut',
            data: {
                labels: (data.planes && data.planes.labels) || [],
                datasets: [{
                    data: (data.planes && data.planes.values) || [],
                    backgroundColor: [primary, secondary, warning, danger, info],
                    borderColor: cssVar('--color-blanco', '#ffffff'),
                    borderWidth: 2,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { color: text } }
                }
            }
        });
    }

    // D. Usuarios por empresa (Top 5) - barras horizontales
    const ctxTopU = document.getElementById('chartTopUsuarios');
    if (ctxTopU) {
        new Chart(ctxTopU, {
            type: 'bar',
            data: {
                labels: (data.topUsuarios && data.topUsuarios.labels) || [],
                datasets: [{
                    label: 'Usuarios',
                    data: (data.topUsuarios && data.topUsuarios.values) || [],
                    backgroundColor: secondary,
                }]
            },
            options: {
                ...commonOptions,
                indexAxis: 'y',
                scales: {
                    x: { ...commonOptions.scales.x, beginAtZero: true, ticks: { ...commonOptions.scales.x.ticks, precision: 0 } },
                    y: commonOptions.scales.y
                }
            }
        });
    }

    // E. Productos por empresa (barras verticales)
    const ctxTopP = document.getElementById('chartTopProductos');
    if (ctxTopP) {
        new Chart(ctxTopP, {
            type: 'bar',
            data: {
                labels: (data.topProductos && data.topProductos.labels) || [],
                datasets: [{
                    label: 'Productos',
                    data: (data.topProductos && data.topProductos.values) || [],
                    backgroundColor: warning,
                }]
            },
            options: {
                ...commonOptions,
                scales: {
                    x: commonOptions.scales.x,
                    y: { ...commonOptions.scales.y, beginAtZero: true, ticks: { ...commonOptions.scales.y.ticks, precision: 0 } }
                }
            }
        });
    }

    // Ajustar altura de contenedores para Chart.js
    document.querySelectorAll('#chartEmpresas, #chartIngresos, #chartPlanes, #chartTopUsuarios, #chartTopProductos')
        .forEach((canvas) => {
            const parent = canvas.parentElement;
            if (parent) parent.style.height = '280px';
        });
}

function initScrollFade() {
    const nodes = document.querySelectorAll('[data-scroll-fade]');
    if (!nodes.length) return;

    const update = (node) => {
        const canScroll = node.scrollHeight > (node.clientHeight + 1);
        if (!canScroll) {
            node.classList.add('is-no-scroll');
            node.classList.add('is-bottom');
            return;
        }

        node.classList.remove('is-no-scroll');

        const atBottom = (node.scrollTop + node.clientHeight) >= (node.scrollHeight - 1);
        if (atBottom) node.classList.add('is-bottom');
        else node.classList.remove('is-bottom');
    };

    nodes.forEach((node) => {
        update(node);
        node.addEventListener('scroll', () => update(node), { passive: true });
    });

    window.addEventListener('resize', () => {
        nodes.forEach((node) => update(node));
    });
}

function markPendientesEnSinPago() {
    const ul = document.getElementById('empresasSinPagoList');
    if (!ul) return;

    const pendientesRaw = ul.getAttribute('data-pendientes');
    if (!pendientesRaw) return;

    let pendientes = [];
    try {
        pendientes = JSON.parse(pendientesRaw);
    } catch {
        return;
    }

    ul.querySelectorAll('[data-empresa-id]').forEach((span) => {
        const id = parseInt(span.getAttribute('data-empresa-id'), 10);
        if (pendientes.includes(id)) {
            span.textContent = 'Pago pendiente';
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    initCharts();
    markPendientesEnSinPago();
    initScrollFade();
});
