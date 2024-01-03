class otDrawInput extends ot.WidgetDirective {
    params = {
        feather: { default: 4 },
        color: { default: "black" }
    }

    init() {
        if (this.elem.nodeName != "CANVAS") throw new Error("The ot-draw-input should be attached to canvas element")
        super.init();
        this.onElemEvent('pointerdown', this.onStartDrawing);
        this.onElemEvent('pointermove', this.onDraw);
        this.onElemEvent('pointerup', this.onStopDrawing);
        this.onElemEvent('pointerleave', this.onStopDrawing);
        this.onElemEvent('pointerout', this.onStopDrawing);

        this.drawing = false;
        this.ctx = this.elem.getContext("2d");
        this.last = null;
    }

    update(updated) {
        if (updated.has('value')) this.ctx.clearRect(0, 0, this.elem.width, this.elem.height);
    }

    commit() {
        let data = this.elem.toDataURL("image/png");
        super.commit(data);
    }

    onStartDrawing(event) {
        if (!this.active) return;
        this.drawing = true;

        this.last = { x: event.offsetX, y: event.offsetY };
        this.ctx.strokeStyle = this.color;
        this.ctx.lineWidth = this.feather;
    }

    onStopDrawing() {
        if (!this.active) return;
        this.drawing = false;
    }

    onDraw(event) {
        if (!this.active || !this.drawing) return;
        let target = { x: event.offsetX, y: event.offsetY };

        this.ctx.beginPath();
        this.ctx.moveTo(this.last.x, this.last.y);
        this.ctx.lineTo(target.x, target.y);
        this.ctx.stroke();

        this.last = target;
    }
}

ot.attachDirective(otDrawInput, "[ot-draw-input]");