console.log('addon.js loaded');

function htmlDecode(input) {
    var doc = new DOMParser().parseFromString(input, "text/html");
    return doc.documentElement.textContent;
}

function getDOMHierarchy(element) {

    if (element.tagName != 'P') {
        return [];
    }

    var elements = [...document.getElementsByTagName('shiny-markdown-stream')[0].children];

    var hierarchy = [];
    var hierarchy_options = [];
    var para_index = 0;
    for (let i = 0; i < elements.length; i++) {
        if (elements[i] == element) {
            for (let j in hierarchy_options) {
                hierarchy.push(hierarchy_options[j].at(-1));
            }
            hierarchy.push(para_index);
            break;
        }

        if (elements[i].tagName.startsWith('H')) {
            index = parseInt(elements[i].tagName.slice(1), 10) - 1;
            if (!Array.isArray(hierarchy_options[index])) {
                hierarchy_options[index] = [];
            }
            hierarchy_options[index].push(htmlDecode(elements[i].innerHTML));
            para_index = 0;
        }
        else if (elements[i].tagName == 'P') {
            para_index += 1
        }
    }
    return hierarchy;
}

targetDiv = document.getElementById('content');

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

console.log(targetDiv);

if (targetDiv) {

    targetDiv.addEventListener('mouseover', (event) => {
        console.log('hello');
        var element = event.target;
        if (element.tagName == 'P') {
            if (!element.classList.contains('highlight-with-color')) {
                element.classList.add('highlight-with-color');
            }

            element.addEventListener('mouseout', (event) => {
                element.classList.remove('highlight-with-color');
            });
        }
    });

    var current_element;

    targetDiv.addEventListener('contextmenu', (event) => {

        if (current_element) {
            current_element.classList.remove('highlight-with-border');
        }

        current_element = event.target;
        var hierarchy = getDOMHierarchy(current_element);

        console.log(hierarchy, !hierarchy);
        if (!hierarchy.length) {
            return;
        }

        event.preventDefault(); // Prevent default browser menu
        let menu = document.getElementById('main-ctx_menu');

        let ancestor_props = document.getElementsByClassName('app-container')[0].getBoundingClientRect();
        let container_props = targetDiv.getBoundingClientRect();

        let left = Math.min(event.clientX, container_props.right - 250) - ancestor_props.left;
        let top = Math.min(event.clientY, container_props.bottom - 75) - ancestor_props.top;

        if (!current_element.classList.contains('highlight-with-border')) {
            current_element.classList.add('highlight-with-border');
        }

        menu.style.display = 'block';
        menu.style.left = `${left}px`;
        menu.style.top = `${top}px`;

        Shiny.setInputValue("main-selected_para_hierarchy", hierarchy);
    });

    $(document).bind("click", function (event) {
        document.getElementById("main-ctx_menu").style.display = "none";

        if (current_element) {
            current_element.classList.remove('highlight-with-border');
        }
    });
}


