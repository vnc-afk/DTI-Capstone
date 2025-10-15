document.addEventListener('DOMContentLoaded', function() {
    document.body.addEventListener('passwordInvalid', function() {
        document.querySelector('#id_password1').classList.add('input-error');
        document.querySelector('#id_password1').classList.remove('input-success');
    });

    document.body.addEventListener('passwordValid', function() {
        document.querySelector('#id_password1').classList.remove('input-error');
        document.querySelector('#id_password1').classList.add('input-success');
    });
    
     window.togglePassword = function() {
        const passwordInput = document.getElementById("id_password");
        const toggle = document.querySelector(".toggle-password");

        if (passwordInput.type === "password") {
            passwordInput.type = "text";
            toggle.textContent = "👁";
        } else {
            passwordInput.type = "password";
            toggle.textContent = "👁";
        }
    }
})
