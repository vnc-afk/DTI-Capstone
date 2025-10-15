document.addEventListener('click', function() {
    const coverageChoices = document.querySelectorAll('.coverage-choice');
    const textInputs = document.querySelectorAll('.coverage-text-inputs');

    coverageChoices.forEach(choice => {
        choice.addEventListener('click', function () {
            // Uncheck all and remove 'selected' from all
            coverageChoices.forEach(c => {
                c.classList.remove('selected');
                const rb = c.querySelector('input[type="radio"]');
                if (rb) rb.checked = false;
            });

            // Check this one and add 'selected'
            const radioBtn = choice.querySelector('input[type="radio"]');
            if (radioBtn) {
                radioBtn.checked = true;
                choice.classList.add('selected');
            }

            // Hide all text input groups and clear their values
            textInputs.forEach(inputGroup => {
                // Clear all inputs inside the inputGroup
                const inputs = inputGroup.querySelectorAll('input, textarea, select');
                inputs.forEach(input => {
                    input.value = '';  // Clear value
                    if (input.type === 'checkbox' || input.type === 'radio') {
                        input.checked = false;  // Uncheck if any
                    }
                });

                inputGroup.style.display = 'none';
            });

            // Show the one that matches the selected radio's value (if any)
            const selectedValue = radioBtn ? radioBtn.value : null;
            if (selectedValue) {
                const correspondingInputs = document.getElementById(`id_${selectedValue}`);
                if (correspondingInputs) {
                    correspondingInputs.style.display = 'flex';
                }
            }

        });
    });
})