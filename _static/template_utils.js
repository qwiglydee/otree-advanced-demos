/*
 * clones template by name, 
 * replaces textnodes "{key}"" with values from provided dict 
 */
function template(name, dict) {
    function fill(node) {
        if (!node.hasChildNodes()) return;
        for (let child of node.childNodes) {
            if (child.nodeType == document.TEXT_NODE) {
                for (let [key, val] of Object.entries(dict)) {
                    child.textContent = child.textContent.replaceAll(`{${key}}`, val);
                }
            }
            if (child.nodeType == document.ELEMENT_NODE) {
                fill(child, dict);
            }
        }
    }

    let tmpl = document.querySelector(`template#${name}`);
    let root = tmpl.content.cloneNode(true);
    fill(root);
    return root;
}
