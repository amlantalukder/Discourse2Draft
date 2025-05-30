const handleSelectionChange = () => {
    const selection = window.getSelection();
    if (selection) {
        console.log(selection.toString());
        //Shiny.setInputValue("my_js_output", selection);
    }
}
console.log(document.getElementById('test'))
document.getElementById('test').addEventListener('select', handleSelectionChange);
alert("If you're seeing this, the javascript file was included successfully.");