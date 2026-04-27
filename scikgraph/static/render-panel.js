// Propagates the global "Visualization" panel settings (layout dropdown +
// "Render graph" checkbox) into every OTHER <form> on the page just before
// submit. The panel form itself is self-contained — its values post directly.
$(function () {
    "use strict";

    function setHidden(form, name, value) {
        var existing = form.querySelector('input[type="hidden"][name="' + name + '"]');
        if (existing) {
            existing.value = value;
            return;
        }
        var input = document.createElement('input');
        input.type = 'hidden';
        input.name = name;
        input.value = value;
        form.appendChild(input);
    }

    function clearHidden(form, name) {
        var existing = form.querySelectorAll('input[type="hidden"][name="' + name + '"]');
        for (var i = 0; i < existing.length; i++) existing[i].remove();
    }

    function injectIntoForm(form) {
        var layoutSelect = document.getElementById('globalLayoutSelect');
        var renderCheck = document.getElementById('globalRenderCheck');
        if (!layoutSelect) return;

        // Layout: every form gets the panel's current value.
        setHidden(form, 'layoutSelect', layoutSelect.value);

        // Render flag: skip if this form already has its own visible checkbox
        // (Construct Graph has one). Otherwise, drive it from the panel.
        var ownCheckbox = form.querySelector('input[type="checkbox"][name="renderVisualizationCheck"]');
        if (!ownCheckbox) {
            setHidden(form, 'renderVisualizationFormMarker', '1');
            clearHidden(form, 'renderVisualizationCheck');
            if (renderCheck && renderCheck.checked) {
                setHidden(form, 'renderVisualizationCheck', 'on');
            }
        }
    }

    var forms = document.querySelectorAll('form');
    for (var i = 0; i < forms.length; i++) {
        // Skip the panel form — it submits its own state directly.
        if (forms[i].name === 'visualizationPanelForm') continue;
        forms[i].addEventListener('submit', function (e) {
            injectIntoForm(e.currentTarget);
        });
    }

    // Long-running buttons — show a "Working..." indicator on submit so the
    // user can see their action was registered and the server is busy.
    function showWorkingOverlay(message) {
        var existing = document.getElementById('scikgraph-working-overlay');
        if (existing) existing.remove();
        var overlay = document.createElement('div');
        overlay.id = 'scikgraph-working-overlay';
        overlay.className = 'scikgraph-working-overlay';
        overlay.innerHTML = '<span class="scikgraph-spinner"></span>' + message + '...';
        document.body.appendChild(overlay);
    }

    var longButtons = document.querySelectorAll('button[data-long-task]');
    for (var j = 0; j < longButtons.length; j++) {
        (function (btn) {
            var form = btn.closest('form');
            if (!form) return;
            form.addEventListener('submit', function (ev) {
                // A form may have multiple submit buttons; only react if THIS
                // button is the one that triggered the submit.
                var trigger = ev.submitter || document.activeElement;
                if (trigger !== btn) return;
                var label = btn.getAttribute('data-long-task') || 'Working';
                // Update visuals immediately (cheap, doesn't affect form data).
                btn.innerHTML = '<span class="scikgraph-spinner" style="border-color:rgba(0,0,0,0.2);border-top-color:#333"></span>' + label + '...';
                btn.style.pointerEvents = 'none';
                btn.style.opacity = '0.7';
                showWorkingOverlay(label);
                // IMPORTANT: do NOT call `btn.disabled = true` synchronously here.
                // A disabled submit button is excluded from the POSTed form data,
                // which would strip its `name` from `request.form` and break the
                // route's elif chain. Defer to the next tick so the browser has
                // already serialised the form, then disable to prevent re-clicks.
                setTimeout(function () { btn.disabled = true; }, 0);
            });
        })(longButtons[j]);
    }
});
