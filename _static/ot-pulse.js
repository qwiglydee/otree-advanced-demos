/*
// This file is originally a part of https://github.com/qwiglydee/otree-advanced-demos
// SPDX-FileCopyrightText: © 2024 Maxim Vasilyev <qwiglydee@gmail.com>
// SPDX-License-Identifier: MIT
*/

/**
 * Directive `<ot-puse>`
 *
 * Creates dots to pulsate by css.
 * USe togather with `ot-pulse.css`
 *
 * @example
 * <ot-pulse id="waiting"></ot-pulse>
 *
 * showDisplay("waiting");
 * hideDisplay("waiting");
 */
class otPulse extends ot.DirectiveBase {
    init() {
        this.elem.hidden = true;
        this.render();
    }

    render() {
        this.elem.innerHTML = "<i></i><i></i><i></i>";
    }
}

ot.attachDirective(otPulse, "ot-pulse");



