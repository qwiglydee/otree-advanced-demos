/*
// This file is originally a part of https://github.com/qwiglydee/otree-advanced-demos
// SPDX-FileCopyrightText: © 2024 Maxim Vasilyev <qwiglydee@gmail.com>
// SPDX-License-Identifier: MIT
*/

/**
 * Wrappers for lifecycle handlers.
 *
 * @example
 * onLoad(startGame);
 * onSubmit(doSomething);
 *
 * function startGame() { ... }
 * function doSomething() { ... }
 */
function onLoad(handler) {
    ot.onEvent('loaded', handler);
}
function onSubmit(handler) {
    ot.onEvent('submitted', handler);
}

/**
 * Warapper for input handler.
 *
 * @example
 * onInput('inputname', inputSomething);
 * onInputs(inputAll);
 *
 * function inputSomething(value) { ... }
 * function inputAll(name, value) { ... }
 */
function onInputs(handler) {
    ot.onEvent('input', (e) => handler(e.detail.name, e.detail.value));
}
function onInput(name,  handler) {
    ot.onEvent('input', name, (e) => handler(e.detail.value));
}

/**
 * Warapper for timer handlers.
 *
 * @example
 * onTimer(name, handleTimer);
 * onTimers(handleTimers));
 *
 * function handleTimer(elapsed, counter) { ... }
 * function handleTimers(name, elapsed, counter) { ... }
 */
function onTimers(handler) {
    ot.onEvent('timer', (e) => handler(e.detail.name, e.detail.elapsed, e.detail.count));
}
function onTimer(name, handler) {
    ot.onEvent('timer', name, (e) => handler(e.detail.elapsed, e.detail.count));
}

/**
 * Wrapper for built-in oTree page timer.
 *
 * @example
 * onCountdown(handleCountdown);
 *
 * function handleCountdown(remaining_seconds) { ... }
 */
function onCountdown(handler) {
    ot.onEvent('countdown', (e) => handler(e.detail.remaining))
}

if (document.querySelector(".otree-timer")) {
    $(".otree-timer__time-left").on("update.countdown", function (e) {
        ot.triggerEvent('countdown', { remaining: e.offset.totalSeconds });
    });
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
 * Switch display subsections like <div id="secttion-subsection">
 *
 * It shows one specified subsection and hides all sibling subsections with the same prefix.
 *
 * @example
 * <div id="feedback-success">...</div>
 * <div id="feedback-failure">...</div>
 * <div id="feedback-timeout">...</div>
 *
 * switchDisplays("feedback-failure");
 */
function switchDisplays(selector) {
    let split = selector.lastIndexOf("-");
    if(split == -1 || selector.endsWith('*')) throw Error("switchDisplays expects id like `prefix-subsection`");

    let pattern = selector.slice(0, split+1) + "*";
    ot.hideDisplays(pattern);
    ot.showDisplays(selector);
}