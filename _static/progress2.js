/** Directive my-progress
 *
 * Draws progress with two layers and smooth transitions.
 * Use together with progress2.css
 *
 * Usage:
 * <my-progress max="..." ticks="..." value="..." value2="..."></my-progress>
 *
 * The values can be constants or variable references.
 */
class myProgress extends ot.otDirectiveBase {

    parameters() {
        return {
            max: { type: 'number' },
            value: { type: 'number' },
            value2: { type: 'number', optional: true },
            ticks: { type: 'number', optional: true }
        }
    }

    render() {
        if (this.elems == undefined) { // initial rendering
            this.elem.classList.add("progress");
            this.elem.innerHTML = `
                <div class="progress-1 progress-bar"></div>
                <div class="progress-2 progress-bar"></div>
                <div class="progress-ticks"></div>
            `

            // shortcuts to nested elems
            this.elems = {
                bar1: this.elem.querySelector(".progress-1"),
                bar2: this.elem.querySelector(".progress-2"),
                ticks: this.elem.querySelector(".progress-ticks"),
            }
        }

        this.renderTicks();
        this.renderBars();
    }

    renderBars() {
        let max = this.max;
        let v1 = this.value;
        let v2 = this.value2;

        function offset(v) {
            return Math.round((v / max) * 10000) / 100;
        }

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

    update(updates) {
        super.update(updates);
        if ('max' in updates || 'ticks' in updates) this.renderTicks();
        this.renderBars();
    }
}

// registed the directive for all elements <my-progress>
ot.registerDirective(myProgress, "my-progress");
