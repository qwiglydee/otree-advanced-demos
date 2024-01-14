/**
 * Some extensions for otree-front
 */

/**
 * Warapper for a input handler.
 *
 * @example
 * ot.onEvent('input', onInput(handleInput));
 * ot.onEvent('input', 'inputname', onInput(handleInput));
 *
 * function handleInput(name, value) { ... }
 */
function onInput(handler) {
    return (e) => handler(e.detail.name, e.detail.value);
}

/**
 * Warapper for a timer handler.
 *
 * @example
 * ot.onEvent('timer', onTimer(handleTimer));
 * ot.onEvent('timer', 'timername', onTimer(handleTimer));
 *
 * function handleTimer(name, value) { ... }
 */
function onTimer(handler) {
    return (e) => handler(e.detail.name, e.detail.elapsed, e.detail.count);
}


/**
 * Converting built-in otree page timeout counter to ot-events.
 *
 * The event triggers every second and reports remaining time in seconds.
 *
 * @example
 * ot.onEvent('countdown', onCountdown(handlePageTimer));
 *
 * function handlePageTimer(remaining) {
 *   ...
 * }
 */
if (document.querySelector(".otree-timer")) {
    $(".otree-timer__time-left").on("update.countdown", function (e) {
        ot.triggerEvent('countdown', { remaining: e.offset.totalSeconds });
    });

    function onCountdown(handler) {
        return (e) => handler(e.detail.remaining);
    };
}


/**
 * Get a property from actual stylesheet
 *
 * @example
 * const FADEOUT_TIME = getStyleProp("--ot-fade-out-time");
 *
 * @param {string} propname property name to get from style
 * @param {string} [selector] selector for an element, default is to ge global style
 */
function getStyleProp(propname, selector) {
    let elem = selector ? document.querySelector(selector) : document.body;
    return window.getComputedStyle(elem).getPropertyValue(propname);
}

/**
 * Directive `ot-puse`
 *
 * Creates pulsating dots.
 *
 * Use showDisplay(id_of_pulse) and hideDisplay(id_of_pulse) to toggle
 */
class otPulse extends ot.DirectiveBase {
    init() {
        this.render();
    }

    render() {
        this.elem.innerHTML = "<i></i><i></i><i></i>";
    }
}

ot.attachDirective(otPulse, "ot-pulse");



