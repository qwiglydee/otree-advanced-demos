/**
 * Directive ot-progress
 *
 * Draws progress with two layers and smooth transitions.
 * Using bootsreap-5.0 styles and ot-progress.css
 *
 * https://github.com/qwiglydee/otree-advanced-demos
 *
 * Usage:
 * <ot-progress max="..." ticks="..." value="..." value2="..."></ot-progress>
 *
 * All the parameters can be either constants or variable references.
 */
class otProgress extends ot.ContentDirective {

    params = {
        max: {},
        val: {},
        val2: {},
        ticks: {}
    }

    render() {
        if (this.elems == undefined) { // initial rendering
            this.elem.classList.add("progress");
            this.elem.innerHTML = `
                <div class="progress-1 progress-bar"></div>
                <div class="progress-2 progress-bar"></div>
                <div class="progress-ticks"></div>
            `;
            // shortcuts to nested elems
            this.elems = {
                bar1: this.elem.querySelector(".progress-1"),
                bar2: this.elem.querySelector(".progress-2"),
                ticks: this.elem.querySelector(".progress-ticks"),
            }
        }

        this.renderTicks();
        this.resetBars();
    }

    resetBars() {
        this.elem.setAttribute("reset", "");
        this.elems.bar1.style.width = 0;
        this.elems.bar2.style.width = 0;
    }

    renderBars() {
        let max = this.max;
        let v1 = this.val;
        let v2 = this.val2;

        function offset(v) {
            return Math.round((v / max) * 10000) / 100;
        }

        this.elem.removeAttribute("reset", "");

        if (v1 === undefined) return;
        this.elems.bar1.style.width = `${offset(v1)}%`;

        if (v2 === undefined) return;
        this.elems.bar2.style.width = `${offset(v2 - v1)}%`;
    }

    renderTicks() {
        let max = this.max;
        let ticks = this.ticks;

        // clean up
        this.elems.ticks.innerHTML = "";
        if (max === undefined || ticks === undefined || ticks > max) return;

        let n = Math.floor(max / ticks);

        function offset(i) {
            return Math.round((i / n) * 10000) / 100;
        }
        this.elems.ticks.innerHTML = [...new Array(n - 1).keys()]
            .map(i => `<i style="left: ${offset(i + 1)}%"></i>`)
            .join("");
    }

    update(updated) {
        if (updated.has('max') || updated.has('ticks')) this.renderTicks();
        if (updated.has('max') || updated.has('val') || updated.has('val2') ) {
            if (this.val !== null) this.renderBars(); else this.resetBars();
        }
    }
}

ot.attachDirective(otProgress, "ot-progress");
