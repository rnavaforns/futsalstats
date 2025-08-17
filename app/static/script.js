document.addEventListener("DOMContentLoaded", () => {
  const partidoId = document.getElementById("partido-id").value;
  let activos = [];             // up to 4
  let dorsalSeleccionado = null; // target for next action

  // Handle dorsal buttons
  document.querySelectorAll(".dorsal-button").forEach(button => {
    button.addEventListener("click", () => {
      const dorsal = parseInt(button.dataset.dorsal);

      // If already active -> deselect
      if (activos.includes(dorsal)) {
        activos = activos.filter(d => d !== dorsal);
        button.classList.remove("active", "selected");
        if (dorsalSeleccionado === dorsal) {
          dorsalSeleccionado = null;
        }
        return;
      }

      // If not active and less than 4 -> activate
      if (activos.length < 4) {
        activos.push(dorsal);
        button.classList.add("active");

        // Make it the selected one automatically
        if (!dorsalSeleccionado) {
          dorsalSeleccionado = dorsal;
          button.classList.add("selected");
        }
      } else {
        alert("Sólo puedes tener 4 dorsales activos.");
      }
    });

    // Right-click to set as selected (among active)
    button.addEventListener("contextmenu", (ev) => {
      ev.preventDefault();
      const dorsal = parseInt(button.dataset.dorsal);
      if (!activos.includes(dorsal)) {
        alert("Primero marca el dorsal como activo.");
        return;
      }
      dorsalSeleccionado = dorsal;

      // Remove selection highlight from others
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

      try {
        const response = await fetch(`/partido/${partidoId}/accion/${columna}/${dorsalSeleccionado}`, {
          method: "POST"
        });

        if (!response.ok) throw new Error("Error en la petición");

        const result = await response.json();
        if (result.ok) {
          mostrarMensaje(`+1 en ${columna} (Dorsal ${dorsalSeleccionado})`);
        }
      } catch (error) {
        console.error("Error al actualizar acción:", error);
        mostrarMensaje("Error al actualizar", true);
      }
    });
  });

  function mostrarMensaje(texto, error = false) {
    const mensajeDiv = document.getElementById('mensaje');
    mensajeDiv.style.color = error ? 'red' : 'green';
    mensajeDiv.innerText = texto;
    setTimeout(() => {
      mensajeDiv.innerText = '';
    }, 2000);
  }
});
