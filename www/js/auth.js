console.log('auth.js loaded')

Shiny.addCustomMessageHandler("auth_key", ({ email }) => localStorage.setItem('email', email));
window.onload = () => Shiny.setInputValue("email", localStorage.getItem('email'));

const passwordVisibleClass = 'password-visible';
const passwordVisibleButtonClass = 'is-visible';
const hasPasswordClass = 'has-password';

function getPasswordInput(field) {
    return field.querySelector('input[type="password"], input.password-visible, input[type="text"]');
}

function syncPasswordToggle(field) {
    const passwordInput = getPasswordInput(field);
    const button = field.querySelector('.password-toggle-button');
    if (!passwordInput || !button) return;

    const hasPassword = passwordInput.value.length > 0;
    field.classList.toggle(hasPasswordClass, hasPassword);

    if (!hasPassword) {
        passwordInput.type = 'password';
        passwordInput.classList.remove(passwordVisibleClass);
        button.classList.remove(passwordVisibleButtonClass);
        button.setAttribute('aria-label', 'Show password');
        button.setAttribute('title', 'Show password');
    }
}

function setPasswordVisibility(button) {
    const field = button.closest('.password-field');
    if (!field) return;

    const passwordInput = getPasswordInput(field);
    if (!passwordInput || passwordInput.value.length === 0) return;

    const showPassword = passwordInput.type === 'password';
    passwordInput.type = showPassword ? 'text' : 'password';
    passwordInput.classList.toggle(passwordVisibleClass, showPassword);
    button.classList.toggle(passwordVisibleButtonClass, showPassword);
    button.setAttribute('aria-label', showPassword ? 'Hide password' : 'Show password');
    button.setAttribute('title', showPassword ? 'Hide password' : 'Show password');
}

document.addEventListener('input', (event) => {
    const field = event.target.closest('.password-field');
    if (!field) return;

    syncPasswordToggle(field);
});

document.addEventListener('click', (event) => {
    const button = event.target.closest('.password-toggle-button');
    if (!button) return;

    setPasswordVisibility(button);
});
