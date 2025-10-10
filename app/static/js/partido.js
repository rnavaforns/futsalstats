document.addEventListener("DOMContentLoaded", () => {
    const partidoId = document.getElementById("partido-id").value;
    let activos = [];
    let dorsalSeleccionado = null;

    // Handle dorsal buttons
    document.querySelectorAll(".dorsal-button").forEach(button => {
        button.addEventListener("click", () => {
            const dorsal = parseInt(button.dataset.dorsal);

            if (activos.includes(dorsal)) {
                activos = activos.filter(d => d !== dorsal);
                button.classList.remove("active", "selected");
                if (dorsalSeleccionado === dorsal) dorsalSeleccionado = null;
                return;
            }

            if (activos.length < 5) {
                activos.push(dorsal);
                button.classList.add("active");
                if (!dorsalSeleccionado) {
                    dorsalSeleccionado = dorsal;
                    button.classList.add("selected");
                }
            } else {
                alert("Sólo puedes tener 5 dorsales activos.");
            }
        });

        button.addEventListener("contextmenu", (ev) => {
            ev.preventDefault();
            const dorsal = parseInt(button.dataset.dorsal);
            if (!activos.includes(dorsal)) {
                alert("Primero marca el dorsal como activo.");
                return;
            }
            dorsalSeleccionado = dorsal;
            document.querySelectorAll(".dorsal-button").forEach(btn => btn.classList.remove("selected"));
            button.classList.add("selected");
        });
    });

    // Handle action buttons
    document.querySelectorAll(".action-button").forEach(button => {
        button.addEventListener("click", async () => {
            if (!dorsalSeleccionado) {
                mostrarMensaje("Selecciona un dorsal activo primero", true);
                return;
            }

            const columna = button.dataset.action;
            const dorsalesStr = activos.join(",");

            try {
                // Call first endpoint
                const response1 = await fetch(`/partido/${partidoId}/accion/${columna}/${dorsalSeleccionado}`, { method: "POST" });
                const result1 = await response1.json();
                if (!response1.ok) throw new Error(result1.detail || "Error en /partido");

                // Call second endpoint
                const response2 = await fetch(`/stats_acumulat/${columna}/${dorsalesStr}`, { method: "POST" });
                const result2 = await response2.json();
                if (!response2.ok) throw new Error(result2.detail || "Error en /stats_acumulat");

                // Show combined message
                mostrarMensaje(`/partido: ${JSON.stringify(result1)} | /stats_acumulat: ${JSON.stringify(result2)}`);

            } catch (error) {
                console.error("Error al actualizar acción:", error);
                mostrarMensaje(`Error: ${error.message}`, true);
            }
        });
    });

    function mostrarMensaje(texto, error = false) {
        const mensajeDiv = document.getElementById('mensaje');
        mensajeDiv.style.color = error ? 'red' : 'green';
        mensajeDiv.innerText = texto;
        setTimeout(() => { mensajeDiv.innerText = ''; }, 3000);
    }
});
