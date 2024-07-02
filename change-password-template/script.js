'use strict';

const btnPassword = document.getElementById('btn-password');
const overlay = document.querySelector('.overlay');
const modal = document.querySelector('.modal-form');

const openModal = function() {
    overlay.classList.remove('hidden');
    modal.classList.remove('hidden');
};

const closeModal = function() {
    modal.classList.add('hidden');
    overlay.classList.add('hidden');
};

//Open modal-form
btnPassword.addEventListener('click', openModal);


//Close modal-form
overlay.addEventListener('click', closeModal);

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
        closeModal();
    }
});



//Show password with the checkbox
function togglePasswordVisibility() {
    const passwordFields = document.querySelectorAll('input[type="password"], input[type="text"]');
    const checkbox = document.getElementById('show-password');
    
    passwordFields.forEach(field => {
        if (checkbox.checked) {
            console.log('Hola');
            field.type = 'text';
            field.setAttribute('data-type', 'shown');
        } else {
            if (field.getAttribute('data-type') === 'shown') {
                field.type = 'password';
                field.removeAttribute('data-type');
            }
        }
    });
}

//Compare both password, is equal send(only a simple prototype change in a future)
document.getElementById('change-password-form').addEventListener('submit', function(event) {
    const newPassword = document.getElementById('new-password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    if (newPassword !== confirmPassword) {
        alert('Passwords do not match!');
        event.preventDefault();
    }
});
