document.addEventListener('DOMContentLoaded', function () {
    const documentsForm = document.querySelector('.documents-form');
    const documentsFormSubmitBtn = document.querySelector('.form-progress-nav .submit-btn');
    const documentsFormDraftBtn = document.querySelector('.form-progress-nav .save-draft-btn');
    const previewModal = document.getElementById('preview-modal-container');
    const confirmBtn = previewModal?.querySelector('.confirm-btn');
    const cancelBtn = previewModal?.querySelector('.cancel-btn');

    console.log('Form elements found:', {
        documentsForm: !!documentsForm,
        documentsFormSubmitBtn: !!documentsFormSubmitBtn,
        previewModal: !!previewModal,
        confirmBtn: !!confirmBtn
    });

    // Add delegated event listener for close alert button
    document.addEventListener('click', function(e) {
        if (e.target && e.target.id === 'close-alert-btn') {
            const alertsContainer = e.target.closest('.alerts-container');
            if (alertsContainer) {
                alertsContainer.remove();
            }
        }
    });

    // Add delegated event listener for close alert button
    document.addEventListener('click', function(e) {
        if (e.target && e.target.id === 'close-alert-btn') {
            const alertsContainer = e.target.closest('.alerts-container');
            if (alertsContainer) {
                alertsContainer.remove();
            }
        }
    });

    // Helper function to show errors in the alerts container
    function showErrorInContainer(errorMessage) {
        const messagesBox = document.querySelector(".alerts-container");
        if (messagesBox) {
            messagesBox.innerHTML = `
                <div class="alerts-container error">
                    <header>
                        <i class="fa-solid fa-triangle-exclamation"></i>
                        <h4>Error!</h4>
                        <i class="fa-solid fa-xmark" id="close-alert-btn"></i>
                    </header>
                    <div class="alert alert-error">
                        ${errorMessage}
                    </div>
                </div>`;
            messagesBox.scrollIntoView({ behavior: "smooth" });
        } else {
            console.error("Messages box not found - cannot display error:", errorMessage);
        }
    }

    if (documentsForm) {
        // === SUBMIT button (shows preview or errors) ===
        documentsFormSubmitBtn.addEventListener('click', (e) => {
            e.preventDefault();
            console.log("Submit button clicked");

            const formData = new FormData(documentsForm);
            formData.append("action", "preview");
            
            console.log("Form action URL:", documentsForm.action);
            console.log("Making AJAX request...");

            fetch(documentsForm.action, {
                method: "POST",
                body: formData,
                headers: { "X-Requested-With": "XMLHttpRequest" }
            })
            .then(res => {
                console.log("Response received - status:", res.status);
                console.log("Content-Type:", res.headers.get('content-type'));
                
                return res.text().then(text => {
                    console.log("Raw response text:", text.substring(0, 500) + "...");
                    
                    try {
                        const data = JSON.parse(text);
                        return { status: res.status, data, text };
                    } catch (parseError) {
                        console.error("JSON parse error:", parseError);
                        throw { status: res.status, text, parseError };
                    }
                });
            })
            .then(({ status, data }) => {
                console.log("Parsed data:", data);
                
                if (status === 200 && data.preview_groups) {
                    // ✅ Success - show preview modal
                    console.log("Showing preview modal");
                    let html = "";
                    data.preview_groups.forEach(group => {
                        html += `<h3 class="preview-group-name">${group.name}</h3><ul class="preview-group-list">`;
                        group.fields.forEach(field => {
                            html += `<li class="preview-list-item">
                                        <strong>${field.label}:</strong> 
                                        <p>${field.value}</p>
                                    </li>`;
                        });
                        html += "</ul>";
                    });
                    
                    if (previewModal) {
                        const modalBody = previewModal.querySelector(".modal-body");
                        if (modalBody) {
                            modalBody.innerHTML = html;
                            previewModal.style.display = "flex";
                        } else {
                            console.error("Modal body not found");
                            showErrorInContainer("Error: Preview modal not properly configured.");
                        }
                    } else {
                        console.error("Preview modal not found");
                        showErrorInContainer("Error: Preview functionality is not available.");
                    }
                } else if ((status === 400 || data.status === "error") && data.messages_html) {
                    // ❌ Validation errors - show messages from Django
                    console.log("Showing validation errors from Django messages");
                    let alertsContainer = document.querySelector(".alerts-container");
                    
                    if (!alertsContainer) {
                        // Create alerts container if it doesn't exist
                        alertsContainer = document.createElement('div');
                        const targetElement = documentsForm || document.querySelector('main') || document.body;
                        targetElement.insertBefore(alertsContainer, targetElement.firstChild);
                    }
                    
                    // Replace content with Django messages HTML and scroll to it
                    alertsContainer.outerHTML = data.messages_html;
                    
                    // Re-select the container after replacement and scroll to it
                    const newAlertsContainer = document.querySelector(".alerts-container");
                    if (newAlertsContainer) {
                        newAlertsContainer.scrollIntoView({ behavior: "smooth" });
                    }
                } else if (status === 500 || data.status === "server_error") {
                    // Server error
                    console.error("Server error:", data);
                    showErrorInContainer(`Server error: ${data.message || 'An unexpected server error occurred.'}`);
                } else {
                    // Log the unexpected response for debugging
                    console.error("Unexpected response format:", data);
                    console.error("Status:", status);
                    console.error("Expected: status 200 with preview_groups OR status 400 with messages_html");
                    
                    // Show error in container instead of alert
                    const dataKeys = Object.keys(data || {}).join(', ');
                    showErrorInContainer(`Unexpected response from server. Status: ${status}${dataKeys ? `, Data: ${dataKeys}` : ''}`);
                }
            })
            .catch(error => {
                console.error("Full error object:", error);
                
                if (error.text) {
                    console.error("Server returned HTML instead of JSON:");
                    console.error(error.text.substring(0, 1000));
                    showErrorInContainer("Server error occurred. Please check the console for details or contact support.");
                } else {
                    console.error("Network or other error:", error);
                    showErrorInContainer("Request failed. Please check your connection and try again.");
                }
            });
        });

        // === CONFIRM button (actual submission) ===
        if (confirmBtn) {
            confirmBtn.addEventListener('click', () => {
                console.log("Confirm button clicked");
                previewModal.style.display = 'none';
                
                // Create hidden input for submitted action
                const actionInput = document.createElement('input');
                actionInput.type = 'hidden';
                actionInput.name = 'action';
                actionInput.value = 'submitted';
                documentsForm.appendChild(actionInput);

                // Submit the form normally (no AJAX)
                console.log("Submitting form normally");
                documentsForm.submit();
            });
        }

        // === CANCEL button in modal ===
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                console.log("Cancel button clicked");
                previewModal.style.display = 'none';
            });
        }

        // === SAVE AS DRAFT button ===
        documentsFormDraftBtn.addEventListener('click', (e) => {
            e.preventDefault();
            console.log("Save as draft clicked");
            
            const actionInput = document.createElement('input');
            actionInput.type = 'hidden';
            actionInput.name = 'action';
            actionInput.value = 'draft';
            documentsForm.appendChild(actionInput);

            // Normal form post → keeps Django messages
            documentsForm.submit();
        });
    } else {
        console.error("Documents form not found!");
    }
});