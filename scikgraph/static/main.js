$(function () {
    "use strict";

    function findStyle(name, styles) {
        for (var i = 0; i < styles.length; i++) {
            if (styles[i].title === name) return styles[i];
        }
        return null;
    }

    var sel = "#cy",
        network = (typeof networks !== "undefined" && networks)
                  ? networks[Object.keys(networks)[0]] : null;

    if (!network || network.disabled || !network.elements) {
        // Visualization disabled (or never produced) — show a placeholder.
        var $cy = $(sel);
        $cy.empty();
        $cy.css({
            "display": "flex",
            "align-items": "center",
            "justify-content": "center",
            "min-height": "300px",
            "color": "#888",
            "font-size": "16px",
            "background": "#f5f5f5",
            "border": "1px dashed #ccc",
            "border-radius": "4px"
        });
        $cy.text("Visualization disabled");
        return;
    }

    var style = styles[0],
        layoutName = network.layout || "cose";

    $(sel).cytoscape({
        layout: { name: layoutName, padding: 10, animate: false },
        boxSelectionEnabled: true,
        pixelRatio: 1,
        wheelSensitivity: 0.5,
        ready: function () {
            window.cy = this;
            cy.load(network.elements);
            var chosen = findStyle("default", style) || style;
            cy.style().fromJson(chosen.style).update();
            // Explicitly run the layout after elements have been loaded.
            // cy.load() does not re-trigger the constructor's `layout` option in 2.x.
            try {
                cy.layout({ name: layoutName, padding: 10, animate: false }).run();
            } catch (e) {
                cy.layout({ name: "cose", padding: 10, animate: false }).run();
            }
        }
    });
});
