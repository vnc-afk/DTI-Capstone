document.addEventListener('DOMContentLoaded', function() {
    const collapseBtn = document.getElementById('collapse-nav-btn');
    const sideNavbar = document.querySelector('.side-navbar');
    const collapseIcon = collapseBtn.querySelector('i');
    
    // Toggle sidebar
    collapseBtn.addEventListener('click', function() {
        sideNavbar.classList.toggle('extended');
        
        // Update icon direction
        if (sideNavbar.classList.contains('extended')) {
            collapseIcon.className = 'fa-solid fa-angle-left';
        } else {
            collapseIcon.className = 'fa-solid fa-angle-right';
        }
    });

    // Handle dropdown toggles
    const dropdownBtns = document.querySelectorAll('.nav-dropdown-btn');
    dropdownBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Ensure dropdown only works when sidebar is extended
            if (sideNavbar.classList.contains('extended')) {
                const dropdownItem = this.closest('.nav-item.dropdown');
                dropdownItem.classList.toggle('active');
            }

        });
    });

    // Close dropdowns when sidebar collapses
    collapseBtn.addEventListener('click', function() {
        if (!sideNavbar.classList.contains('extended')) {
            const activeDropdowns = document.querySelectorAll('.nav-item.dropdown.active');
            activeDropdowns.forEach(dropdown => {
                dropdown.classList.remove('active');
            });
        }
    });
});