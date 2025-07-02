console.log('auth.js loaded')

Shiny.addCustomMessageHandler("auth_key", ({ email }) => localStorage.setItem('email', email));
window.onload = () => Shiny.setInputValue("email", localStorage.getItem('email'));