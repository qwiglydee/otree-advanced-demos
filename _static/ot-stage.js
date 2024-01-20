/*
// This file is originally a part of https://github.com/qwiglydee/otree-advanced-demos
// SPDX-FileCopyrightText: © 2024 Maxim Vasilyev <qwiglydee@gmail.com>
// SPDX-License-Identifier: MIT
*/

/**
 * Directive ot-stage="name"
 *
 * Marks elements and inputs to be switched by `switchStage(name)`
 *
 * Elements of matching stage get enabled and reviealed, and got class "active".
 * Elements of other stages get hidden and disabled.
 *
 * If stage name is numeric, then inactive elements additionally get css classes "passed" or "further"
 *
 * @example
 * <section ot-stage="1">...</section>
 * <section ot-stage="2">...</section>
 * <section ot-stage="3">...</section>
 *
 * switchStage(2);
 */
class otStage extends ot.DirectiveBase {
    params = {
        name: { attr: "ot-stage" }
    }

    init() {
        this.initParams();
        this.isInput = this.elem.hasAttribute("name") || this.elem.hasAttribute("input");
        if (this.isInput) {
            this.elem.disabled = true;
        } else {
            this.elem.hidden = true;
        }
        this.onPageEvent("ot.switch", this.onSwitch);
    }

    onSwitch(event) {
        let target = event.detail.stage;
        let activating = this.name == target;
        let sequential = String(target).match(/^\d+$/);
        if (this.isInput) {
            this.elem.disabled = !activating;
            if (activating && this.elem.hasAttribute("autofocus")) this.elem.focus();
        } else {
            this.elem.hidden = !activating;
            this.elem.classList.toggle("active", activating);
            this.elem.classList.toggle("passed", !activating && sequential && this.name < target);
            this.elem.classList.toggle("further", !activating && sequential && this.name > target);
        }
    }
}

ot.attachDirective(otStage, "[ot-stage]");

function switchStage(stage) {
    ot.triggerEvent("switch", { stage });
}