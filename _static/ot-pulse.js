/*
// This file is originally a part of https://github.com/qwiglydee/otree-advanced-demos
// SPDX-FileCopyrightText: © 2024 Maxim Vasilyev <qwiglydee@gmail.com>
// SPDX-License-Identifier: MIT
*/

/**
 * Directive `<ot-puse>`
 *
 * Creates dots to pulsate by css.
 * Use togather with `ot-pulse.css`
 *
 * Add 'hidden' attribute to make it hidden initially.
 *
 * @example
 * <ot-pulse id="waiting" hidden></ot-pulse>
 *
 * showDisplay("waiting");
 */
class otPulse extends ot.DirectiveBase {
    init() {
        this.elem.innerHTML = "<i></i><i></i><i></i>";
    }
}

ot.attachDirective(otPulse, "ot-pulse");



