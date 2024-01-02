class otSlider extends ot.WidgetDirective {
    params = {
        min: { default: -100 },
        max: { default: +100 },
        offset: { defalt: 0 },
        solved: { default: false }
    }

    init() {
        super.init();
        this.slider_id = this.name.split('-')[1];
    }

    render() {
        this.elem.innerHTML = `<input type="range" class="form-range" min="${this.min}" max="${this.max}" step="1">`;
        this.input = this.elem.querySelector("input");
    }

    commit() {
        super.commit({ id: this.slider_id, value: parseInt(this.value) });
    }

    reset() {
        this.input.value = this.value;
    }

    update(updated) {
        if(updated.has('solved')) {
            this.elem.classList.toggle('is-valid', this.solved);
        }

        if(updated.has('offset')) {
            this.elem.style.marginLeft = `${this.offset}px`;
        }
    }
}


ot.attachDirective(otSlider, "ot-slider");