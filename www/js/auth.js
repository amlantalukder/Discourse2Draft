console.log('auth.js loaded')

Shiny.addCustomMessageHandler("auth_key", ({ email }) => localStorage.setItem('email', email));
window.onload = () => Shiny.setInputValue("email", localStorage.getItem('email'));

const passwordVisibleClass = 'password-visible';
const passwordVisibleButtonClass = 'is-visible';

function setPasswordVisibility(button) {
    const field = button.closest('.password-field');
    if (!field) return;

    const passwordInput = field.querySelector('input[type="password"], input.password-visible');
    if (!passwordInput) return;

    const showPassword = passwordInput.type === 'password';
    passwordInput.type = showPassword ? 'text' : 'password';
    passwordInput.classList.toggle(passwordVisibleClass, showPassword);
    button.classList.toggle(passwordVisibleButtonClass, showPassword);
    button.setAttribute('aria-label', showPassword ? 'Hide password' : 'Show password');
    button.setAttribute('title', showPassword ? 'Hide password' : 'Show password');
}

document.addEventListener('click', (event) => {
    const button = event.target.closest('.password-toggle-button');
    if (!button) return;

    setPasswordVisibility(button);
});
