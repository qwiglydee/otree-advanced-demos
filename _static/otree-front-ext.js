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
 * Directive `ot-fade`
 *
 * Makes a marked section smoothly cross-fade when switched.
 *
 * Mark the section with `ot-fade`:
 * <main ot-fade></main>
 */

class otFade extends ot.DirectiveBase {
    init() {
        this.state = "off";
        this.render();
        this.onPageEvent("fading", this.onFade)
    }

    render() {
        this.elem.classList.remove("fade-off", "fade-on", "fade-in", "fade-out");
        this.elem.classList.add(`fade-${this.state}`);
    }

    onFade(e) {
        this.state = e.detail.state;
        this.render();
    }
}

ot.attachDirective(otFade, "[ot-fade]");

/** turns off (no animation) */
function fadeOff() {
    ot.triggerEvent("fading", { state: "off" });
}

/** turns on (no animation) */
function fadeOff() {
    ot.triggerEvent("fading", { state: "on" });
}

/** make it fade in (with css animation) */
function fadeIn() {
    ot.triggerEvent("fading", { state: "in" });
}

/** make it fade out (with css animation) */
function fadeOut() {
    ot.triggerEvent("fading", { state: "out" });
}

/**
 * Directive `ot-puse`
 *
 * Creates pulsating dots.
 *
 * Initially hidden, use showDisplays(id_of_pulse) to toggle
 */
class otPulse extends ot.DirectiveBase {
    init() {
        this.elem.setAttribute("hidden", ""); // initially hidden
        this.render();
    }

    render() {
        this.elem.innerHTML = "<i></i><i></i><i></i>";
    }
}

ot.attachDirective(otPulse, "ot-pulse");



