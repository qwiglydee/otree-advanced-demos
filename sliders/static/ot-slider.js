/*
// This file is originally a part of https://github.com/qwiglydee/otree-advanced-demos
// SPDX-FileCopyrightText: © 2024 Maxim Vasilyev <qwiglydee@gmail.com>
// SPDX-License-Identifier: MIT
*/

/**
 * Directive <ot-slider name=... min=... max=... target=... offset=... solved=...></ot-slider>
 *
 * Draws a slider input with marked target position.
 * The directive reuses native browser widget input[type=range] which may behave differently in different browsers.
 */
class otSlider extends ot.WidgetDirective {
    params = {
        min: { default: -100 },
        max: { default: +100 },
        target: { default: 0 },
        offset: { defalt: 0 },
        solved: { default: false },
    }

    init() {
        super.init();
        this.range = this.max - this.min + 1;
    }

    render() {
        this.elem.innerHTML = `<i></i><input type="range" name="${this.name}" class="form-range" min="${this.min}" max="${this.max}" step="1">`;
        this.input = this.elem.querySelector("input");
        this.tick = this.elem.querySelector("i");
    }

    reset() {
        this.input.value = this.value;
    }

    update(updated) {
        if(updated.has('target')) this.tick.style.left = (100 * (this.target - this.min) / this.range).toFixed(2) + "%";
        if(updated.has('offset')) this.elem.style.marginLeft = `${this.offset}px`;
        if(updated.has('solved')) this.elem.classList.toggle('is-valid', this.solved);
    }

    commit() {
        super.commit(Number(this.value))
    }
}


ot.attachDirective(otSlider, "ot-slider");