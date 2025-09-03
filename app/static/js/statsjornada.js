document.addEventListener("DOMContentLoaded", () => {
    const table = document.querySelector("table");
    const headers = table.querySelectorAll("thead th");

    headers.forEach((header, index) => {
        const button = document.createElement("button");
        button.textContent = "⇅";
        button.classList.add("sort-btn");
        header.appendChild(button);

        let asc = true;

        button.addEventListener("click", () => {
            const tbody = table.querySelector("tbody");
            const rows = Array.from(tbody.querySelectorAll("tr:not(.totals-row)"));
            const totalsRow = tbody.querySelector(".totals-row");

            rows.sort((a, b) => {
                const A = a.children[index].innerText.trim();
                const B = b.children[index].innerText.trim();

                const numA = parseFloat(A);
                const numB = parseFloat(B);

                if (!isNaN(numA) && !isNaN(numB)) {
                    return asc ? numA - numB : numB - numA;
                } else {
                    return asc ? A.localeCompare(B) : B.localeCompare(A);
                }
            });

            // Reinsertar las filas ordenadas
            rows.forEach(r => tbody.appendChild(r));

            // Y siempre dejar la fila de totales al final
            if (totalsRow) {
                tbody.appendChild(totalsRow);
            }

            asc = !asc;
        });
    });
});
