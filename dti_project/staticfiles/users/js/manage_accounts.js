document.addEventListener('DOMContentLoaded', function() {

    // Select all checkboxes
    document.getElementById('select-all-checkbox').addEventListener('change', function() {
        const checked = this.checked;
        document.querySelectorAll('input[name="staffs"]').forEach(cb => {
            cb.checked = checked;
        });
    });

    const userRows = document.querySelectorAll('.user-value-row');

    // Make rows clickable except when clicking checkbox
    userRows.forEach(row => {
        row.addEventListener('click', function(e) {
            if (e.target.type !== 'checkbox') {
                const url = this.getAttribute('data-href');
                if (url) {
                    window.location.href = url;
                }
            }
        })
    })

    // Select all checkboxes
    document.getElementById('select-all-checkbox').addEventListener('change', function() {
        const checked = this.checked;
        const checkboxUserType = this.getAttribute('name')

        document.querySelectorAll('input[type="checkbox"][name]').forEach(cb => {
            cb.checked = checked;
        });
    })

})