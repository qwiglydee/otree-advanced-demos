liveSocket.onmessage = function (message) {
    let messages = JSON.parse(message.data);
    for (const [type, detail] of Object.entries(messages)) {
        emitEvent(`live.${type}`, detail);
    }
}

function onLive(type, handler) {
    onEvent(`live.${type}`, handler);
}

function sendLive(type, data=null) {
    liveSocket.send(JSON.stringify({ [type]: data }));
}