class myDrawInput extends ot.otInputBase {
    parameters() {
        return {
            name: { type: 'name', variable: false },
            feather: { type: 'number' },
            color: { type: 'string' }
        }
    };

    init(attrs) {
        super.init(attrs);
        this.drawing = false;
        this.ctx = this.elem.getContext("2d");
        this.last = null;
    }

    set value(val) {
        // ignore
    }

    get value() {
        return this.elem.toDataURL("image/png");
    }

    reset() {
        this.ctx.clearRect(0, 0, this.elem.width, this.elem.height);
    }

    setup() {
        super.setup();
        this.onElemEvent('pointerdown', this.onPointerStart);
        this.onElemEvent('pointerup', this.onPointerEnd);
        this.onElemEvent('pointerleave', this.onPointerEnd);
        this.onElemEvent('pointerout', this.onPointerEnd);
        this.onElemEvent('pointermove', this.onPointerMove);
    }

    onPointerStart(detail, event) {
        if (this.disabled) return;
        this.drawing = true;
        this.last = {x: event.offsetX, y: event.offsetY};
        this.ctx.strokeStyle = this.color;
        this.ctx.lineWidth = this.feather;
    }

    onPointerEnd() {
        if (this.disabled) return;
        this.drawing = false;
    }

    onPointerMove(detail, event) {
        if (this.disabled || !this.drawing) return;
        let x = event.offsetX, y = event.offsetY;

        this.ctx.beginPath();
        this.ctx.moveTo(this.last.x, this.last.y);
        this.ctx.lineTo(x, y);
        this.ctx.stroke();

        this.last = {x, y};
    }
}

ot.registerDirective(myDrawInput, "[my-draw-input]")