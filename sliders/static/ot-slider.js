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
        this.slider_id = this.name.split('-')[1];
    }

    render() {
        this.elem.innerHTML = `<i></i><input type="range" name="${this.name}" class="form-range" min="${this.min}" max="${this.max}" step="1">`;
        this.input = this.elem.querySelector("input");
        this.tick = this.elem.querySelector("i");
    }

    commit() {
        super.commit({ id: this.slider_id, value: parseInt(this.value) });
    }

    reset() {
        this.input.value = this.value;
    }

    update(updated) {
        if(updated.has('target')) this.tick.style.left = (100 * (this.target - this.min) / this.range).toFixed(2) + "%";
        if(updated.has('offset')) this.elem.style.marginLeft = `${this.offset}px`;
        if(updated.has('solved')) this.elem.classList.toggle('is-valid', this.solved);
    }
}


ot.attachDirective(otSlider, "ot-slider");