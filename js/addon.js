console.log('addon.js loaded');

function getDOMHierarchy(element) {

    if (element.tagName != 'P') {
        return [];
    }

    var elements = [...document.getElementsByTagName('shiny-markdown-stream')[0].children];

    var expected_htag_level = 1;
    var hierarchy = [];
    var para_index = 0;
    for (let i = 0; i < elements.length; i++) {
        if (elements[i] == element) {
            hierarchy.push(para_index);
            break;
        }
        if (elements[i].tagName == `H${expected_htag_level}`) {
            hierarchy.push(elements[i].innerHTML);
            expected_htag_level++;
            para_index = 0;
        }
        else if (elements[i].tagName == 'P') {
            para_index += 1
        }
    }
    return hierarchy;
}

targetDiv = document.getElementById('content-container')

// let data = '';
// logSelection = () => {
//     if (window.getSelection) {
//         selection = window.getSelection();
//     } else if (document.selection) {
//         selection = document.selection.createRange();
//     }
//     if (selection) {
//         data = selection.toString()
//     }
// }

// targetDiv.addEventListener('selectstart', () => {
//     document.addEventListener('selectionchange', logSelection)
// })

// targetDiv.addEventListener("mouseup", () => {
//     document.removeEventListener("selectionchange", logSelection);
// })

var current_element;

targetDiv.addEventListener('contextmenu', function (event) {

    if (current_element) {
        current_element.style.backgroundColor = '';
    }

    current_element = event.target;
    var hierarchy = getDOMHierarchy(current_element);
    console.log(hierarchy);

    event.preventDefault(); // Prevent default browser menu
    let menu = document.getElementById('main-ctx_menu');

    let ancestor_props = document.getElementsByClassName('app-container')[0].getBoundingClientRect();
    let container_props = targetDiv.getBoundingClientRect();

    let left = Math.min(event.clientX, container_props.right - 250) - ancestor_props.left;
    let top = Math.min(event.clientY, container_props.bottom - 75) - ancestor_props.top;

    current_element.style.backgroundColor = '#d3d3e9';

    menu.style.display = 'block';
    menu.style.left = `${left}px`;
    menu.style.top = `${top}px`;

    Shiny.setInputValue("main-selected_para_hierarchy", hierarchy);
});

$(document).bind("click", function (event) {
    console.log(event.clientX, event.clientY);
    document.getElementById("main-ctx_menu").style.display = "none";
    if (current_element) {
        current_element.style.backgroundColor = '';
    }
});