/**
 * Helpers to communicate with backend driven by `utils/live.py`
 */

if (window.liveSocket) {
    window.liveSocket.onmessage = triggerLive;
} else {
    throw new Error("otree-front-live.js doesn't see live socket")
}

/**
 * Warapper for live handlers.
 *
 * @example
 * onLive('message_type', handleLive);
 *
 * function handleLive(data) { ... }
 */
function onLive(name, handler) {
    ot.onEvent('live', name,  (e) => handler(e.detail.data));
}

/**
 * Sending a live message.
 *
 * @example
 * sendLive("something", { ... } );
 * sendLive("something", "foo");
 * sendLive("something");
 *
 * @param {string} type type of the message
 * @param {object} [data] message payload
 */
function sendLive(type, data) {
    window.liveSocket.send(JSON.stringify({ type, data }))
}

/**
 * @event live
 * @property {object} detail
 * @property {string} detail.name type of a message
 * @property {any} detail.data message payload
 */

/** converting live socket messages into ot-events */
function triggerLive(event) {
    let data = JSON.parse(event.data);
    if (!ot.isArray(data)) throw new Error("live socket received invalid data")
    for (let msg of data) {
        if (!ot.isObject(msg) || !Object.hasOwn(msg, 'type')) throw new Error("live socket received invalid data")
        ot.emitEvent('live', { name: msg.type, data: msg.data });
    }
}
