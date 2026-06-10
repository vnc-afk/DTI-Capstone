// From-To Field Validation
document.addEventListener('DOMContentLoaded', function() {
    // Define the from/to field pairs based on your Django form
    const fieldPairs = [
        {
            checkbox: 'id_change_territorial_scope',
            from: 'id_territorial_scope_from',
            to: 'id_territorial_scope_to',
            isSelect: true
        },
        {
            checkbox: 'id_change_owner_name',
            from: 'id_owner_name_from',
            to: 'id_owner_name_to',
            isSelect: false
        },
        {
            checkbox: 'id_change_business_address',
            from: 'id_business_address_from',
            to: 'id_business_address_to',
            isSelect: false
        },
        {
            checkbox: 'id_change_owner_address',
            from: 'id_owner_address_from',
            to: 'id_owner_address_to',
            isSelect: false
        }
    ];

    // Function to check if a field has content
    function hasContent(field) {
        if (!field) return false;
        const value = field.value.trim();
        return value.length > 0;
    }

    // Function to add helper text to label
    function addHelperText(toField) {
        if (!toField) return;
        
        // Find the label for this field
        const label = toField.parentElement.querySelector('label');
        if (!label) return;
        
        // Check if helper text already exists
        const existingHelper = label.querySelector('.fill-from-first-text');
        if (existingHelper) return;
        
        // Create helper text element
        const helperText = document.createElement('span');
        helperText.className = 'fill-from-first-text';
        helperText.style.color = '#ff6b6b';
        helperText.style.fontSize = '0.85em';
        helperText.style.fontWeight = 'normal';
        helperText.style.fontStyle = 'italic';
        helperText.style.marginLeft = '0.5rem';
        helperText.textContent = '(Fill "From" field first)';
        
        // Append to label
        label.appendChild(helperText);
    }

    // Function to remove helper text
    function removeHelperText(toField) {
        if (!toField) return;
        const label = toField.parentElement.querySelector('label');
        if (!label) return;
        
        const helperText = label.querySelector('.fill-from-first-text');
        if (helperText) {
            helperText.remove();
        }
    }

    // Function to disable selected option in "to" select field
    function disableMatchingOption(fromField, toField) {
        if (!toField || toField.tagName !== 'SELECT') return;
        
        const selectedValue = fromField.value;
        
        // Re-enable all options first
        Array.from(toField.options).forEach(option => {
            option.disabled = false;
            option.style.color = '';
        });
        
        // Disable the matching option
        if (selectedValue) {
            Array.from(toField.options).forEach(option => {
                if (option.value === selectedValue) {
                    option.disabled = true;
                    option.style.color = '#ccc';
                }
            });
            
            // If the "to" field currently has the same value selected, clear it
            if (toField.value === selectedValue) {
                toField.value = '';
            }
        }
    }

    // Function to update checkbox state based on from/to fields
    function updateCheckboxState(checkboxField, fromField, toField) {
        if (!checkboxField) return;
        
        const fromValue = fromField.value.trim();
        const toValue = toField.value.trim();
        
        // Check both fields are filled
        if (fromValue && toValue) {
            checkboxField.checked = true;
        } else {
            checkboxField.checked = false;
        }
    }

    // Function to disable/enable the "to" field
    function updateToFieldState(fromField, toField, isSelect, checkboxField) {
        if (!toField) return;
        
        if (hasContent(fromField)) {
            // Enable the "to" field
            toField.disabled = false;
            toField.style.backgroundColor = '';
            toField.style.cursor = '';
            removeHelperText(toField);
            
            // For select fields, disable the matching option
            if (isSelect) {
                disableMatchingOption(fromField, toField);
            }
        } else {
            // Disable the "to" field and clear its value
            toField.disabled = true;
            toField.value = '';
            toField.style.backgroundColor = '#f5f5f5';
            toField.style.cursor = 'not-allowed';
            addHelperText(toField);
        }
        
        // Update checkbox state
        updateCheckboxState(checkboxField, fromField, toField);
    }

    // Initialize all field pairs
    fieldPairs.forEach(pair => {
        const checkboxField = document.getElementById(pair.checkbox);
        const fromField = document.getElementById(pair.from);
        const toField = document.getElementById(pair.to);

        if (fromField && toField) {
            // Set initial state
            updateToFieldState(fromField, toField, pair.isSelect, checkboxField);

            // Add event listeners to the "from" field
            fromField.addEventListener('input', function() {
                updateToFieldState(fromField, toField, pair.isSelect, checkboxField);
            });

            fromField.addEventListener('change', function() {
                updateToFieldState(fromField, toField, pair.isSelect, checkboxField);
            });

            // Add event listeners to the "to" field to update checkbox
            toField.addEventListener('input', function() {
                updateCheckboxState(checkboxField, fromField, toField);
            });

            toField.addEventListener('change', function() {
                updateCheckboxState(checkboxField, fromField, toField);
            });

            // Prevent interaction with disabled "to" field
            toField.addEventListener('focus', function(e) {
                if (!hasContent(fromField)) {
                    e.preventDefault();
                    fromField.focus();
                    
                    // Optional: Show a brief visual feedback
                    fromField.style.border = '2px solid #ff6b6b';
                    setTimeout(() => {
                        fromField.style.border = '';
                    }, 1000);
                }
            });
        }
    });

    // Prevent negative numbers in no_of_copies field
    const noOfCopiesField = document.getElementById('id_no_of_copies');
    if (noOfCopiesField) {
        // Prevent typing minus sign and 'e' (scientific notation)
        noOfCopiesField.addEventListener('keydown', function(e) {
            if (e.key === '-' || e.key === 'e' || e.key === 'E' || e.key === '+') {
                e.preventDefault();
            }
        });

        // Remove negative values on paste or input
        noOfCopiesField.addEventListener('input', function(e) {
            if (this.value < 0) {
                this.value = '';
            }
            // Remove leading zeros
            if (this.value.length > 1 && this.value.startsWith('0')) {
                this.value = parseInt(this.value, 10) || '';
            }
        });

        // Ensure minimum value on blur
        noOfCopiesField.addEventListener('blur', function(e) {
            if (this.value && parseInt(this.value, 10) < 0) {
                this.value = '';
            }
        });
    }

    // Validate TRN code - only letters and numbers
    const trnField = document.getElementById('id_trn_code');
    if (trnField) {
        // Prevent typing special characters
        trnField.addEventListener('keydown', function(e) {
            // Allow: backspace, delete, tab, escape, enter, arrows
            const allowedKeys = ['Backspace', 'Delete', 'Tab', 'Escape', 'Enter', 
                               'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'];
            
            // Allow Ctrl/Cmd shortcuts (Ctrl+A, Ctrl+C, Ctrl+V, etc.)
            if (e.ctrlKey || e.metaKey) {
                return;
            }
            
            // Allow if it's a special key
            if (allowedKeys.includes(e.key)) {
                return;
            }
            
            // Check if the key is alphanumeric
            const isAlphanumeric = /^[a-zA-Z0-9]$/.test(e.key);
            
            if (!isAlphanumeric) {
                e.preventDefault();
            }
        });

        // Remove non-alphanumeric characters on paste or input
        trnField.addEventListener('input', function(e) {
            // Remove any character that's not a letter or number
            this.value = this.value.replace(/[^a-zA-Z0-9]/g, '');
        });

        // Final validation on blur
        trnField.addEventListener('blur', function(e) {
            this.value = this.value.replace(/[^a-zA-Z0-9]/g, '');
        });
    }
});