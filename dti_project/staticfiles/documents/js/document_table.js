document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".document-value-row").forEach(row => {
        row.addEventListener("click", (e) => {
            if (e.target.type == 'checkbox') {
                e.stopPropagation();
                return
            } else {
                window.location = row.dataset.href;
            }
        });
    });

    const selectAllCheckbox = document.getElementById('select-all-checkbox');
    const documentTableCheckboxes = document.querySelectorAll('.document-value-row input[type="checkbox"]');

    selectAllCheckbox.addEventListener('click', function() {
        documentTableCheckboxes.forEach(cb => {
            cb.checked = selectAllCheckbox.checked;
        });
    });

    // Update select-all when individual checkboxes change
    documentTableCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const allChecked = Array.from(documentTableCheckboxes).every(cb => cb.checked);
            selectAllCheckbox.checked = allChecked;
        });
    });
});