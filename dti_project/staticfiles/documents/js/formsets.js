document.addEventListener('DOMContentLoaded', function () {
    // Debug: Check what data-label values are being generated
    console.log('Available formsets:', document.querySelectorAll("fieldset[data-label]"));
    document.querySelectorAll("fieldset[data-label]").forEach(fieldset => {
        console.log('Fieldset data-label:', fieldset.dataset.label);
        
        // Check if management form exists
        const managementForm = fieldset.querySelector("input[name$='-TOTAL_FORMS']");
        console.log('Management form found:', managementForm);
        if (managementForm) {
            console.log('Management form name:', managementForm.name);
        }
    });

    document.querySelectorAll("fieldset[data-label]").forEach(fieldset => {
        const addButton = fieldset.querySelector(".add-btn");
        const formGrid = fieldset.querySelector(".step-grid");
        const previewList = document.querySelector(`#${fieldset.dataset.label}-preview-list`);
        const managementForm = fieldset.querySelector("input[name$='-TOTAL_FORMS']");
        const formsetPrefix = fieldset.dataset.label.replace('-', '_'); // Convert to underscore format
        
        // Get the current form count from existing items
        let formCount = parseInt(managementForm.value) || 0;

        function updateTotalForms() {
            managementForm.value = formCount;
        }

        function extractFieldName(templateName) {
            // Remove 'template_' prefix
            // e.g., 'template_employer' -> 'employer'
            return templateName.replace('template_', '');
        }

        function createHiddenFormset(formData, index) {
            const hiddenContainer = document.createElement("div");
            hiddenContainer.classList.add("hidden-formset");
            hiddenContainer.style.display = "none";
            
            // Get the field names from the template inputs
            const templateInputs = formGrid.querySelectorAll("input, select, textarea");
            
            templateInputs.forEach(input => {
                const fieldName = extractFieldName(input.name);
                const value = formData[input.name] || '';
                
                // Create hidden input for ALL fields (even empty ones)
                const hiddenInput = document.createElement("input");
                hiddenInput.type = "hidden";
                hiddenInput.name = `${formsetPrefix}-${index}-${fieldName}`;
                hiddenInput.value = value;
                hiddenContainer.appendChild(hiddenInput);
            });
            
            // Add the ID field for Django formset (required for proper form handling)
            const idInput = document.createElement("input");
            idInput.type = "hidden";
            idInput.name = `${formsetPrefix}-${index}-id`;
            idInput.value = ""; // Empty for new records
            hiddenContainer.appendChild(idInput);
            
            // Add DELETE field (required for Django formset)
            const deleteInput = document.createElement("input");
            deleteInput.type = "hidden";
            deleteInput.name = `${formsetPrefix}-${index}-DELETE`;
            deleteInput.value = ""; // Empty means don't delete
            hiddenContainer.appendChild(deleteInput);
            
            return hiddenContainer;
        }

        function addToPreview() {
            const formData = {};
            const inputs = formGrid.querySelectorAll("input, select, textarea");
            
            // Check if at least one field has a value
            let hasValue = false;
            inputs.forEach(input => {
                const value = input.value.trim();
                if (value) {
                    hasValue = true;
                }
                formData[input.name] = value;
            });
            
            if (!hasValue) {
                alert("Please fill in at least one field before adding.");
                return;
            }

            const previewItem = document.createElement("li");
            previewItem.classList.add("preview-item");
            previewItem.dataset.formIndex = formCount;

            // Create display content based on form data
            const values = Object.values(formData).filter(val => val.trim());
            
            // Try to create a meaningful title from the first two non-empty values
            const titleText = values.length >= 2 ? `${values[1]} - ${values[0]}` : values[0] || 'New Item';
            const titleElement = document.createElement("strong");
            titleElement.textContent = titleText;
            previewItem.appendChild(titleElement);

            // Try to create period from what might be date fields
            if (values.length >= 3) {
                const startDate = values[2];
                const endDate = values[3] || "Present";
                const periodElement = document.createElement("p");
                periodElement.classList.add("period");
                periodElement.textContent = `(${startDate} - ${endDate})`;
                previewItem.appendChild(periodElement);
            }

            // Create hidden formset inputs
            const hiddenFormset = createHiddenFormset(formData, formCount);
            previewItem.appendChild(hiddenFormset);

            // Remove button
            const removeButton = document.createElement("button");
            removeButton.type = "button";
            removeButton.classList.add("remove-btn");
            const icon = document.createElement("div");
            icon.className = "fa-solid fa-xmark";
            removeButton.appendChild(icon);
            
            removeButton.addEventListener("click", function() {
                previewItem.remove();
                updateFormIndices();
            });
            
            previewItem.appendChild(removeButton);

            // Append the preview item to the preview list
            previewList.appendChild(previewItem);

            // Clear form inputs
            inputs.forEach(input => input.value = "");
            
            formCount++;
            console.log('Total Forms: ', formCount);
            updateTotalForms();
        }

        function updateFormIndices() {
            const previewItems = previewList.querySelectorAll(".preview-item");
            formCount = 0;
            
            previewItems.forEach((item, index) => {
                item.dataset.formIndex = index;
                
                // Update hidden input names
                const hiddenInputs = item.querySelectorAll("input[type='hidden']");
                hiddenInputs.forEach(input => {
                    const nameParts = input.name.split('-');
                    if (nameParts.length >= 3) {
                        nameParts[1] = index; // Update the form index
                        input.name = nameParts.join('-');
                    }
                });
                
                formCount++;
            });
            
            updateTotalForms();
        }

        // Handle removal of existing items
        previewList.addEventListener("click", function(e) {
            if (e.target.classList.contains("remove-btn") || e.target.closest(".remove-btn")) {
                const previewItem = e.target.closest(".preview-item");
                
                // If this is an existing item (has an ID), mark it for deletion
                const idInput = previewItem.querySelector("input[name$='-id']");
                if (idInput && idInput.value) {
                    const deleteInput = previewItem.querySelector("input[name$='-DELETE']");
                    if (deleteInput) {
                        deleteInput.value = "on";
                        previewItem.style.display = "none";
                    } else {
                        // Create delete input if it doesn't exist
                        const deleteInput = document.createElement("input");
                        deleteInput.type = "hidden";
                        deleteInput.name = idInput.name.replace('-id', '-DELETE');
                        deleteInput.value = "on";
                        previewItem.appendChild(deleteInput);
                        previewItem.style.display = "none";
                    }
                } else {
                    // New item, can be completely removed
                    previewItem.remove();
                    updateFormIndices();
                }
            }
        });

        addButton.addEventListener("click", addToPreview);

        formGrid.addEventListener("keydown", (e) => {
            if (e.key === "Enter") {
                e.preventDefault();
                addToPreview();
            }
        });
    });
})