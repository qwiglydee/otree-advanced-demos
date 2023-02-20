/** Custom directive my-progress
 * 
 * Draws 2 layer progress bar for 'current' and 'completed'
 * 
 * Usage:
 *   <div my-progress="obj.*"></div>
 * 
 * The `obj` should reference to an object { total, current, completed, ticks }
 * 
 */
class myProgress extends ot.dev.otDirectiveBase {
    /* initialize directive using element attributes */
    init(attrs) {
        super.init(attrs); // initialize base stuff for directives
        this.ref = ot.dev.parseExpr(attrs["my-progress"], [ot.dev.WatchExpr]); // reference to object to watch

        // watch subfields relevant to ticks 
        this.total_ref = ot.dev.parseExpr(this.ref.var + ".total", [ot.dev.VarExpr]);
        this.ticks_ref = ot.dev.parseExpr(this.ref.var + ".ticks", [ot.dev.VarExpr]);

        this.onPageEvent('ot.update', this.onUpdate);  // handle updates of the refs

        this.render(); // insert initial html
        this.refresh(); // clear bars
    }

    /* handle variable update, either values or undefined */
    onUpdate(changes) {
        // check if the object or any subfield changed
        if (this.ref.affected(changes)) { 
            let values = this.ref.eval(ot.page); // get values of the page vars
            this.refresh(values);
        }

        // check if ticks-relevant vars changed
        if (this.total_ref.affected(changes) || this.ticks_ref.affected(changes)) {
            let total = this.total_ref.eval(ot.page);
            let ticks = this.ticks_ref.eval(ot.page);
            if (ticks) {
                this.redrawTicks(total, ticks);
            }
        }
    }
    /* insert initial html */
    render() {
        // bootstrap5 progress bar stack
        this.elem.classList.add("progress");
        this.elem.innerHTML = `
            <div class="progress-completed progress-bar"></div></div>
            <div class="progress-current progress-bar"></div></div>
            <div class="progress-ticks"></div>
        `
        // save references to inner elems
        this.elems = {
            current: this.elem.querySelector(".progress-current"),
            completed: this.elem.querySelector(".progress-completed"),
            ticks: this.elem.querySelector(".progress-ticks"),
        }
    }

    /* update bars */
    refresh(values) {
        function offset(val) {
            let v = val / values.total;
            return Math.round(v * 10000) / 100;
        }
        if (!values) {
            this.elems.current.style.width = `0%`;
            this.elems.completed.style.width = `0%`;
        } else {
            let completed = values.completed || 0, current = values.current || 0, w;
            this.elems.current.style.width = `${offset(current - completed)}%`;
            this.elems.completed.style.width = `${offset(completed)}%`;
        }
    }

    /* update ticks */
    redrawTicks(total, ticks) {
        let n = Math.floor(total / ticks);

        function offset(i) {
            let v = i / n;
            return Math.round(v * 10000) / 100;
        }
        this.elems.ticks.innerHTML = [...new Array(n-1).keys()]
            .map(i => `<div class="progress-tick" style="left: ${offset(i+1)}%"></div>`)
            .join("");
    }
}

// registed the directive for all elements with attribute 'my-progress'
ot.dev.registerDirective(myProgress, "[my-progress]");
