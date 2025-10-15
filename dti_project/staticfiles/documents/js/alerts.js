document.addEventListener('DOMContentLoaded', function() {
    const alertsContainer = document.querySelector('.alerts-container');
    const alertCloseBtn = document.getElementById('close-alert-btn');

    if (alertCloseBtn) {
        alertCloseBtn.addEventListener('click', function() {
            alertsContainer.style.display = 'none'
        })
    }
})
