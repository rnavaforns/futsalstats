document.addEventListener("DOMContentLoaded", () => {
  const partidoId = document.getElementById("partido-id").value;

  document.querySelectorAll(".action-button").forEach(button => {
    button.addEventListener("click", async () => {
      const columna = button.dataset.action;

      try {
        const response = await fetch(`/partido/${partidoId}/accion/${columna}`, {
          method: "POST"
        });

        if (!response.ok) throw new Error("Error en la petición");

        const result = await response.json();
        if (result.ok) {
          // Actualizar contador en la página (opcional: hacer otra consulta para el valor actualizado)
          const contador = document.getElementById(`${columna}-count`);
          if (contador) {
            // Incrementamos en 1 localmente para reflejar el cambio inmediato
            let current = parseInt(contador.textContent) || 0;
            contador.textContent = current + 1;
          }
        }
      } catch (error) {
        console.error("Error al actualizar acción:", error);
      }
    });
  });
});
