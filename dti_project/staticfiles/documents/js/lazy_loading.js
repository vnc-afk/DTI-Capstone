document.addEventListener('DOMContentLoaded', function() {
    const tabItems = document.querySelectorAll('.tab-item');
    const tabContents = document.querySelectorAll('.tab-content');

    tabItems.forEach(tab => {
        tab.addEventListener('click', function() {
            const target = tab.getAttribute('data-tab-target');

            // Remove active class from all tabs and contents
            tabItems.forEach(i => i.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            // Activate clicked tab and corresponding content
            tab.classList.add('active')

            const targetContent = document.querySelector(`.tab-content[data-tab-content="${target}"]`)
            if (targetContent) {
                targetContent.classList.add('active')
            }
        })
    })
    
    const tabsSection = document.querySelector('.tabs-section');
    const enableLazyLoading = tabsSection.dataset.lazyLoading === 'true';
    
    if (!enableLazyLoading) {
        // Initialize regular tabs without lazy loading
        initializeTabs();
        return;
    }
    
    // Initialize lazy loading tabs
    initializeLazyTabs();
    
    function initializeTabs() {
        const tabItems = document.querySelectorAll('.tab-item');
        const tabContents = document.querySelectorAll('.tab-content');
        
        tabItems.forEach(item => {
            item.addEventListener('click', function() {
                const targetId = this.dataset.tabTarget;
                
                // Remove active class from all tabs and contents
                tabItems.forEach(tab => tab.classList.remove('active'));
                tabContents.forEach(content => content.classList.remove('active'));
                
                // Add active class to clicked tab and corresponding content
                this.classList.add('active');
                document.querySelector(`[data-tab-content="${targetId}"]`).classList.add('active');
            });
        });
    }
    
    function initializeLazyTabs() {
        const tabItems = document.querySelectorAll('.tab-item');
        const tabContents = document.querySelectorAll('.tab-content');
        
        tabItems.forEach(item => {
            item.addEventListener('click', function() {
                const targetId = this.dataset.tabTarget;
                const isLazyLoad = this.dataset.lazyLoad === 'true';
                const targetContent = document.querySelector(`[data-tab-content="${targetId}"]`);
                const isLoaded = targetContent.dataset.loaded === 'true';
                
                // Remove active class from all tabs and contents
                tabItems.forEach(tab => {
                    tab.classList.remove('active');
                    const loadingIndicator = tab.querySelector('.loading-indicator');
                    if (loadingIndicator) {
                        loadingIndicator.style.display = 'none';
                    }
                });
                tabContents.forEach(content => content.classList.remove('active'));
                
                // Add active class to clicked tab
                this.classList.add('active');
                targetContent.classList.add('active');
                
                // Load content if needed
                if (isLazyLoad && !isLoaded) {
                    loadTabContent(targetId, this);
                }
            });
        });
    }
    
    function loadTabContent(tabId, tabElement) {
        const loadingIndicator = tabElement.querySelector('.loading-indicator');
        const targetContent = document.querySelector(`[data-tab-content="${tabId}"]`);
        
        // Show loading indicator
        if (loadingIndicator) {
            loadingIndicator.style.display = 'inline';
        }
        
        // Make AJAX request
        fetch(`${window.location.pathname}?load_tab=${tabId}`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.html) {
                targetContent.innerHTML = data.html;
                targetContent.dataset.loaded = 'true';
                
                // Update count in tab
                const countElement = tabElement.querySelector('.object-count');
                if (countElement) {
                    countElement.textContent = `(${data.count})`;
                }
            }
        })
        .catch(error => {
            console.error('Error loading tab content:', error);
            targetContent.innerHTML = '<div class="error-state"><p>Error loading content. Please try again.</p></div>';
        })
        .finally(() => {
            // Hide loading indicator
            if (loadingIndicator) {
                loadingIndicator.style.display = 'none';
            }
        });
    }
});