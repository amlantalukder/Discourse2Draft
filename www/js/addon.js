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
    var para_index = 0;
    for (let i = 0; i < elements.length; i++) {
        if (elements[i].tagName.startsWith('H')) {
            index = parseInt(elements[i].tagName.slice(1), 10) - 1;
            while (hierarchy.length - 1 > index) {
                hierarchy.pop();
            }
            hierarchy[index] = htmlDecode(elements[i].innerHTML);
            para_index = 0;
        }
        else if (elements[i].tagName == 'P') {
            if (elements[i] == element) {
                hierarchy.push(para_index);
                break;
            }
            para_index += 1
        }
    }
    return hierarchy;
}

Shiny.addCustomMessageHandler("reload_content", ({ ui_id }) => {

    targetDiv = document.getElementById('content');
    console.log(targetDiv);

    if (targetDiv) {

        targetDiv.addEventListener('mouseover', (event) => {

            var element = event.target;
            if (element.tagName == 'P') {
                if (!element.classList.contains('highlight-with-border')) {
                    element.classList.add('highlight-with-border');
                }

                element.addEventListener('mouseout', (event) => {
                    element.classList.remove('highlight-with-border');
                });
            }
        });

        var current_element;

        targetDiv.addEventListener('click', (event) => {

            if (current_element) {
                current_element.classList.remove('highlight-with-color');
            }

            event.preventDefault(); // Prevent default browser menu

            if (event.target.tagName != 'P') {
                return;
            }

            current_element = event.target;
            var hierarchy = getDOMHierarchy(current_element);

            console.log(current_element);
            console.log(hierarchy);

            if (!hierarchy.length) {
                return;
            }

            let menu = document.getElementById('regenerate_text_controls');

            //let ancestor_props = document.getElementsByClassName('app-body-container')[0].getBoundingClientRect();
            //let container_props = targetDiv.getBoundingClientRect();

            //let left = Math.min(event.clientX, container_props.right - 250) - ancestor_props.left;
            //let top = Math.min(event.clientY, container_props.bottom - 75) - ancestor_props.top;

            if (!current_element.classList.contains('highlight-with-color')) {
                current_element.classList.add('highlight-with-color');
            }

            console.log(menu);
            menu.style.display = 'block';
            //menu.style.left = `${left}px`;
            //menu.style.top = `${top}px`;

            Shiny.setInputValue(`${ui_id}-selected_para_hierarchy`, hierarchy);
        });

        $(document).bind("click", function (event) {

            const regenerate_text_controls_elements = document.querySelector('#regenerate_text_controls');
            const popover_regen_instruction = document.querySelector('#popover_regen_instruction');

            if (event.target != current_element &&
                !regenerate_text_controls_elements.contains(event.target) &&
                !popover_regen_instruction.contains(event.target)) {
                document.getElementById('regenerate_text_controls').style.display = 'none';
                current_element.classList.remove('highlight-with-border');
                current_element.classList.remove('highlight-with-color');
            }
        });
    }

});


