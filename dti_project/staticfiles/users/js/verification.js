document.addEventListener('DOMContentLoaded', function() { 
    const form = document.querySelector('#register-form')
    const step3 = document.getElementById("step3"); 
    const maskedOutput = document.getElementById("maskedOutput"); 
    const codeInputs = document.querySelectorAll('.code-input');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const formData = new FormData(form)
        
        // Debug: Log form data
        console.log("=== FORM DATA ===");
        for (let [key, value] of formData.entries()) {
            console.log(`${key}: ${value}`);
        }

        try {
            const response = await fetch(form.action, {
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": getCSRFToken(),
                }
            });

            console.log("Response status:", response.status);
            const data = await response.json();
            console.log("Response data:", data);

            if (data.success) {
                // Show modal for OTP
                const verificationContainer = document.querySelector('.verification-container');
                if (verificationContainer) {
                    verificationContainer.style.display = "flex";
                }
                if (maskedOutput) {
                    maskedOutput.textContent = data.masked_email;
                }
                startCountdown(30);

                const modalCodeInputs = document.querySelectorAll('.code-input');
                modalCodeInputs.forEach((input) => (input.value = ""));
                if (modalCodeInputs.length > 0) {
                    modalCodeInputs[0].focus();
                }
            } else {
                if (data.messages_html) {
                    const alertsContainer = document.querySelector('.alerts-container');
                    if (alertsContainer) {
                        alertsContainer.outerHTML = data.messages_html;
                    } else {
                        document.querySelector('.backdrop-layer')
                            .insertAdjacentHTML('afterbegin', data.messages_html);
                    }
                }
            }
        } catch (error) {
            console.error("Error submitting form:", error);
            alert("Something went wrong.");
        }
    })
 
    let countdownTimer; 

    const resendBtn = document.getElementById("resend-btn"); 
 
    function startCountdown(seconds = 30) { 
        const countdownEl = document.getElementById("countdown"); 
        const resendWrapper = document.getElementById("resendWrapper");
 
        if (resendWrapper && resendBtn && countdownEl) {
            resendWrapper.style.display = "inline"; 
            resendBtn.style.display = "none"; 
            countdownEl.textContent = seconds; 
     
            clearInterval(countdownTimer); 
            countdownTimer = setInterval(() => { 
                seconds--; 
                countdownEl.textContent = seconds; 
                if (seconds <= 0) { 
                    clearInterval(countdownTimer); 
                    resendWrapper.style.display = "none"; 
                    resendBtn.style.display = "inline"; 
                } 
            }, 1000);
        }
    }

    resendBtn.addEventListener('click', async function() {
        const title = document.querySelector('#step3 .title') 
        try {
            const response = await fetch(`/users/resend-code/`, {
                method: "POST",
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json()
            if (data.success) {
                console.log('Code resent successfully')
                startCountdown(30)

                if (title) {
                    title.textContent = 'Code resent, check your inbox'
                }
            }
        } catch (error) {
            console.error('Error: failed to resend code')
        }
    })

    // Auto-navigation logic for code inputs
    codeInputs.forEach((input, index) => {
        input.addEventListener('input', function(e) {
            const value = e.target.value;
            
            // Only allow single digit
            if (value.length > 1) {
                e.target.value = value.slice(0, 1);
            }
            
            // Move to next input if current is filled
            if (e.target.value.length === 1 && index < codeInputs.length - 1) {
                codeInputs[index + 1].focus();
            }
        });

        input.addEventListener('keydown', function(e) {
            // Handle backspace
            if (e.key === 'Backspace') {
                // If current input is empty and not the first input, go to previous
                if (e.target.value === '' && index > 0) {
                    e.preventDefault();
                    codeInputs[index - 1].focus();
                    codeInputs[index - 1].value = '';
                }
                // If current input has value, just clear it (default behavior)
                else if (e.target.value !== '') {
                    e.target.value = '';
                    e.preventDefault();
                }
            }
            
            // Handle arrow keys for navigation
            if (e.key === 'ArrowLeft' && index > 0) {
                e.preventDefault();
                codeInputs[index - 1].focus();
            }
            
            if (e.key === 'ArrowRight' && index < codeInputs.length - 1) {
                e.preventDefault();
                codeInputs[index + 1].focus();
            }
            
            // Only allow numeric input
            if (!/[0-9]/.test(e.key) && 
                !['Backspace', 'Delete', 'Tab', 'ArrowLeft', 'ArrowRight', 'Enter'].includes(e.key)) {
                e.preventDefault();
            }
        });

        // Handle paste events
        input.addEventListener('paste', function(e) {
            e.preventDefault();
            const pasteData = e.clipboardData.getData('text').replace(/\D/g, ''); // Only digits
            
            // Fill inputs starting from current position
            for (let i = 0; i < pasteData.length && (index + i) < codeInputs.length; i++) {
                codeInputs[index + i].value = pasteData[i];
            }
            
            // Focus the next empty input or the last filled one
            const nextEmptyIndex = Math.min(index + pasteData.length, codeInputs.length - 1);
            codeInputs[nextEmptyIndex].focus();
        });
    });
 
    // Resend link handler
    const resendLink = document.getElementById("resendLink");
    if (resendLink) {
        resendLink.onclick = (e) => { 
            e.preventDefault(); 
            alert("Code resent! (fake demo)"); 
            startCountdown(30);
            
            // Clear all inputs and focus first one
            const modalCodeInputs = document.querySelectorAll('.code-input');
            modalCodeInputs.forEach(input => input.value = '');
            if (modalCodeInputs.length > 0) {
                modalCodeInputs[0].focus();
            }
        };
    }

    // Close modal handler
    const closeModalBtn = document.getElementById('close-verification-modal-btn');
    const verificationContainer = document.querySelector('.verification-container');

    if (closeModalBtn && verificationContainer) {
        closeModalBtn.addEventListener('click', function() {
            verificationContainer.style.display = 'none';
        })
    }

    // USE EVENT DELEGATION FOR VERIFY BUTTON
    // This will work even if the button is hidden when the page loads
    document.addEventListener('click', async function(e) {
        // Check if the clicked element is the verify button
        if (e.target.matches('.btn-verify')) {
            e.preventDefault();
            
            console.log('=== VERIFY BUTTON CLICKED ===');
            
            // Get code inputs from the modal (they might be different from the initial codeInputs)
            const modalCodeInputs = document.querySelectorAll('.code-input');
            const code = Array.from(modalCodeInputs).map(input => input.value).join('');

            console.log('Collected code:', code);
            console.log('Code length:', code.length);

            if (code.length != 6) {
                alert("Please enter the full 6-digit code.");
                return;
            }

            try {
                console.log('Sending verification request...');
                const response = await fetch('/users/verify-user/', {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded",
                        "X-CSRFToken": getCSRFToken(),
                        "X-Requested-With": "XMLHttpRequest",
                    },
                    body: new URLSearchParams({ code: code })
                });

                console.log('Response status:', response.status);
                const data = await response.json();
                console.log('Response data:', data);

                if (data.success) {
                    alert("✅ Verification successful!");
                    window.location.href = data.redirect || "/dashboard/";
                } else {
                    alert("❌ " + (data.error || data.message || "Verification failed"));
                }

            } catch (error) {
                console.error("Error verifying code:", error);
                alert("Something went wrong. Please try again.");
            }
        }
    });

    function getCSRFToken() {
        const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]");
        if (!csrfToken) {
            console.error("CSRF token not found!");
            return '';
        }
        return csrfToken.value;
    }

});