/* ============================================================================
   CLIENTES.JS - Orquestador Principal
   ============================================================================ */

document.addEventListener('DOMContentLoaded', function() {
    inicializarBusquedaFrontend();
    inicializarFiltrosFrontend();

    if (typeof inicializarModalCrear === 'function') {
        inicializarModalCrear();
    }
    if (typeof inicializarModalVer === 'function') {
        inicializarModalVer();
    }
    if (typeof inicializarModalEditar === 'function') {
        inicializarModalEditar();
    }
    if (typeof inicializarModalEliminar === 'function') {
        inicializarModalEliminar();
    }
});

function inicializarBusquedaFrontend() {
    const inputBuscar = document.getElementById('buscar');
    if (!inputBuscar) return;

    let timeoutId;
    inputBuscar.addEventListener('input', function() {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
            aplicarFiltrosFrontend();
        }, 200);
    });
}

function inicializarFiltrosFrontend() {
    const filtroEstado = document.getElementById('estado');
    const filtroEmpresa = document.getElementById('empresa');

    if (filtroEstado) {
        filtroEstado.addEventListener('change', () => aplicarFiltrosFrontend());
    }
    if (filtroEmpresa) {
        filtroEmpresa.addEventListener('change', () => aplicarFiltrosFrontend());
    }
}

function aplicarFiltrosFrontend() {
    const buscar = (document.getElementById('buscar')?.value || '').toLowerCase().trim();
    const estado = document.getElementById('estado')?.value || '';
    const empresa = document.getElementById('empresa')?.value || '';

    const filas = document.querySelectorAll('.tabla-clientes tbody tr');
    let contadorVisible = 0;

    filas.forEach(fila => {
        if (fila.querySelector('td[colspan]')) {
            return;
        }

        const textoFila = fila.textContent.toLowerCase();
        const estadoFila = fila.dataset.estado || '';
        const empresaFila = fila.dataset.empresa || '';

        let mostrar = true;

        if (buscar && !textoFila.includes(buscar)) {
            mostrar = false;
        }

        if (estado && estadoFila !== estado) {
            mostrar = false;
        }

        if (empresa && empresaFila !== empresa) {
            mostrar = false;
        }

        fila.style.display = mostrar ? '' : 'none';
        if (mostrar) contadorVisible++;
    });

    mostrarMensajeSinResultados(contadorVisible, buscar, estado, empresa);
}

function mostrarMensajeSinResultados(cantidad, buscar, estado, empresa) {
    const tbody = document.querySelector('.tabla-clientes tbody');
    if (!tbody) return;

    const mensajeAnterior = tbody.querySelector('.mensaje-sin-resultados');
    if (mensajeAnterior) {
        mensajeAnterior.remove();
    }

    if (cantidad > 0) return;

    let mensaje = 'No se encontraron clientes';
    const filtros = [];

    if (buscar) {
        filtros.push(`que coincidan con "${buscar}"`);
    }
    if (estado) {
        filtros.push(`con estado "${estado}"`);
    }
    if (empresa) {
        filtros.push(`de la empresa "${empresa}"`);
    }

    if (filtros.length > 0) {
        mensaje += ' ' + filtros.join(' y ');
    }

    const filaMensaje = document.createElement('tr');
    filaMensaje.className = 'mensaje-sin-resultados';
    filaMensaje.innerHTML = `
        <td colspan="6" class="text-center py-4">
            <i class="fas fa-search fa-3x text-muted mb-2" style="display: block;"></i>
            <p class="text-muted mb-0"><strong>${mensaje}</strong></p>
            <p class="text-muted small">Intente con otros criterios de busqueda</p>
        </td>
    `;

    tbody.appendChild(filaMensaje);
}
