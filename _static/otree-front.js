/*!
otree-front v1.5.b2
microframework for interactive pages for oTree platform
(C) qwiglydee@gmail.com
https://github.com/qwiglydee/otree-front
*/
var ot = (function (exports) {
    'use strict';

    function isArray(o) {
      return Array.isArray(o);
    }
    function isFunction(obj) {
      return typeof obj == "function";
    }
    function isVoid(value) {
      return value === undefined || value === null || Number.isNaN(value);
    }
    function isHTMLElement(value) {
      return Object.prototype.toString.call(value).startsWith("[object HTML");
    }

    /**
     * from https://github.com/oleics/node-is-scalar
     */
    function isScalar(value) {
      var type = typeof value;
      if (type === 'string') return true;
      if (type === 'number') return true;
      if (type === 'boolean') return true;
      if (type === 'symbol') return true;
      if (value == null) return true;
      if (value instanceof Symbol) return true;
      if (value instanceof String) return true;
      if (value instanceof Number) return true;
      if (value instanceof Boolean) return true;
      return false;
    }

    /*
     * is-plain-object <https://github.com/jonschlinkert/is-plain-object>
     *
     * Copyright (c) 2014-2017, Jon Schlinkert.
     * Released under the MIT License.
     */

    function isObject(o) {
      return Object.prototype.toString.call(o) === '[object Object]';
    }
    function isPlainObject(o) {
      var ctor, prot;
      if (isObject(o) === false) return false;

      // If has modified constructor
      ctor = o.constructor;
      if (ctor === undefined) return true;

      // If has modified prototype
      prot = ctor.prototype;
      if (isObject(prot) === false) return false;

      // If constructor does not have an Object-specific method
      if (prot.hasOwnProperty('isPrototypeOf') === false) {
        return false;
      }

      // Most likely a plain Object
      return true;
    }

    function matchType(value, type) {
      switch (type) {
        case 'data':
          return true;
        case 'array':
          return isArray(value);
        case 'object':
          return isObject(value);
        default:
          return typeof value === type;
      }
    }
    function matchTypes(args, types) {
      return Array.from(args).every((a, i) => matchType(a, types[i]));
    }
    function assertArgs(fname, args) {
      for (var _len = arguments.length, types = new Array(_len > 2 ? _len - 2 : 0), _key = 2; _key < _len; _key++) {
        types[_key - 2] = arguments[_key];
      }
      let matching = types.filter(argtypes => argtypes.length == args.length && matchTypes(args, argtypes));
      if (matching.length == 0) {
        const usage = types.map(argtypes => "".concat(fname, "(").concat(argtypes.join(", "), ")")).join(" or ");
        throw new Error("Invalid arguments, expected: ".concat(usage));
      }
    }
    function pickArgs(args) {
      if (args.length == 2) {
        return {
          match: args[0],
          handler: args[1]
        };
      } else {
        return {
          match: undefined,
          handler: args[0]
        };
      }
    }

    /**
     * Utils to work with dot-separated key paths
     */

    const PATH_RE = /^[a-zA-Z]\w+(\.\w+)*$/;
    function validate(path) {
      return path.match(PATH_RE);
    }
    function length(path) {
      return path.split('.').length;
    }
    function extract(obj, path) {
      if (path.endsWith(".*")) path = path.slice(0, -2);
      return path.split(".").reduce((o, k) => o && k in o ? o[k] : undefined, obj);
    }
    function update(obj, path, value) {
      const keys = path.split(".");
      const parent_path = keys.slice(0, -1);
      const fld = keys.slice(-1)[0];
      function extract(obj, path) {
        return path.reduce((o, k) => o && k in o ? o[k] : undefined, obj);
      }
      let parent = parent_path.length ? extract(obj, parent_path) : obj;
      if (parent === undefined) throw new Error("Unreachable keypath ".concat(path));
      parent[fld] = value;
    }
    function upsert(obj, path, value) {
      const keys = path.split(".");
      const parent_path = keys.slice(0, -1);
      const fld = keys.slice(-1)[0];
      function extract(obj, path) {
        return path.reduce((o, k) => o && k in o ? o[k] : undefined, obj);
      }
      let parent = parent_path.length ? extract(obj, parent_path) : obj;
      if (parent === undefined) throw new Error("Unreachable keypath ".concat(path));
      parent[fld] = value;
    }

    var keypath = /*#__PURE__*/Object.freeze({
        __proto__: null,
        extract: extract,
        length: length,
        update: update,
        upsert: upsert,
        validate: validate
    });

    const FORMATS = {
      string: /^.*$/,
      number: /^-?\d*(\.\d+)?$/,
      boolean: /^(true|false)$/,
      name: /^[a-zA-Z]\w+$/,
      variable: /^vars.[a-zA-Z]\w+(\.\w+)*(\.\*)?$/
    };
    function matchFormat(format, value) {
      if (!(format in FORMATS)) throw new Error("Unknown parameter type: ".concat(format));
      return value.match(FORMATS[format]);
    }
    function parseValue(name, format, value) {
      if (!matchFormat(format, value)) throw new Error("Invalid parameter '".concat(name, "'; expected: ").concat(format));
      switch (format) {
        case 'number':
          return Number(value);
        case 'boolean':
          return value === 'true';
        case 'variable':
          return value.slice(5);
        default:
          return value;
      }
    }
    function parseParam(name, conf, attrs) {
      if (conf.type !== undefined && !(conf.type in FORMATS)) Error("Unrecognized parameter type '".concat(conf.type, "'"));
      let value = conf.attr ? attrs[conf.attr] : attrs[name];
      if (conf.type == 'flag') {
        if (value != "" && value != undefined) throw new Error("Invalid parameter '".concat(name, "'; expected: flag with no value"));
        return {
          val: name in attrs,
          type: 'flag'
        };
      }
      if (value === undefined) {
        if (!conf.optional) throw new Error("Missing parameter '".concat(name, "'"));
        return {
          val: conf.default,
          type: conf.type
        };
      }
      if (matchFormat('variable', value)) {
        if (conf.variable === false) throw new Error("Invalid parameter '".concat(name, "'; expected: value"));
        return {
          var: value.slice(5),
          type: conf.type,
          val: conf.default
        };
      } else {
        if (conf.variable === true) throw new Error("Invalid parameter '".concat(name, "'; expected: variable"));
      }
      if (conf.type !== undefined) {
        return {
          val: parseValue(name, conf.type, value),
          type: conf.type
        };
      } else {
        return {
          val: value,
          type: undefined
        };
      }
    }
    function evalParam(name, param, changes, vars) {
      if (param.var === undefined || !changes.affect(param.var)) return;
      let value = extract(vars, param.var);
      if (value === undefined) {
        return null; // deleted
      }

      if (param.type && typeof value != param.type) throw new Error("Invalid value of 'vars.".concat(param.var, "' for parameter '").concat(name, "'; expected: ").concat(param.type));
      return value;
    }

    function isValuable(value) {
      return isScalar(value) || isObject(value) || isArray(value) || isHTMLElement(value);
    }
    function isCompound(value) {
      return isPlainObject(value) || isArray(value);
    }
    function flatten(obj) {
      let prefix = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : "";
      return function* () {
        // yield value, including compound, except top-level
        if (prefix != "" && isValuable(obj)) {
          yield [prefix, isVoid(obj) ? null : obj];
        }

        // recurse into compound
        if (isCompound(obj)) {
          for (let [k, v] of Object.entries(obj)) {
            if (isValuable(v)) yield* flatten(v, prefix ? "".concat(prefix, ".").concat(k) : k);
          }
        }
      }();
    }
    function snap(obj) {
      return new Map(flatten(obj));
    }
    function affects(key, path) {
      if (path.endsWith(".*")) {
        return key.startsWith(path.slice(0, -2));
      } else {
        return path == key || path.startsWith(key + '.');
      }
    }
    class Changes extends Set {
      affect(varpath) {
        return Array.from(this.keys()).some(k => affects(k, varpath));
      }
    }
    function roots(path) {
      let p = path.split('.');
      return p.map((e, i) => p.slice(0, i + 1).join("."));
    }
    function diff(oldshot, newshot) {
      let changes = new Changes();
      let allkeys = new Set([].concat(Array.from(oldshot.keys()), Array.from(newshot.keys())));
      for (let k of allkeys) {
        if (roots(k).some(r => changes.has(r))) continue; // skip if any parent already in changes
        if (oldshot.get(k) !== newshot.get(k)) changes.add(k);
      }
      return changes;
    }

    let snapshot = new Map();
    function updatePage() {
      let recursed = 2;
      while (recursed > 0) {
        recursed--;
        let newshot = snap(window.vars);
        let changes = diff(snapshot, newshot);
        if (changes.size == 0) break;
        snapshot = newshot;
        document.body.dispatchEvent(new CustomEvent("ot.update", {
          detail: changes
        }));
      }
    }
    function onDelete(variable, handler) {
      let watch;
      try {
        assertArgs("onDelete", arguments, ['string', 'function']);
        watch = parseValue('variable', 'variable', variable);
      } catch (e) {
        console.error(e);
        throw new Error("Invalid onDelete usage");
      }

      // not using onEvent to avoid recursive updates
      document.body.addEventListener('ot.update', function (event) {
        let changes = event.detail;
        if (changes.affect(watch)) {
          let val = extract(window.vars, watch);
          if (isVoid(val)) {
            handler();
          }
        }
      });
    }
    function onUpdate(variable, handler) {
      let watch;
      try {
        assertArgs("onUpdate", arguments, ['string', 'function']);
        watch = parseValue('variable', 'variable', variable);
      } catch (e) {
        console.error(e);
        throw new Error("Invalid onUpdate usage");
      }

      // not using onEvent to avoid recursive updates
      document.body.addEventListener('ot.update', function (event) {
        let changes = event.detail;
        if (changes.affect(watch)) {
          let val = extract(window.vars, watch);
          if (!isVoid(val)) {
            handler(val);
          }
        }
      });
    }

    function dispatchEvent(name, detail) {
      assertArgs("dispatchEvent", arguments, ['string', 'data'], ['string']);
      document.body.dispatchEvent(new CustomEvent("ot.".concat(name), {
        detail
      }));
    }
    function emitEvent(name, detail) {
      assertArgs("emitEvent", arguments, ['string', 'data'], ['string']);
      setTimeout(() => document.body.dispatchEvent(new CustomEvent("ot.".concat(name), {
        detail
      })));
    }
    function delayEvent(time, name, detail) {
      assertArgs("delayEvent", arguments, ['number', 'string', 'data'], ['number', 'string']);
      setTimeout(() => document.body.dispatchEvent(new CustomEvent("ot.".concat(name), {
        detail
      })), time);
    }
    function onEvent(name, handler) {
      assertArgs("onEvent", arguments, ['string', 'function']);

      // TODO: parseValue('name')

      document.body.addEventListener("ot.".concat(name), async ev => {
        await handler(ev.detail, ev);
        updatePage();
      });
    }

    function onInput() {
      assertArgs("onInput", arguments, ['string', 'function'], ['function']);
      let {
        handler,
        match
      } = pickArgs(arguments);
      if (match !== undefined) {
        onEvent('input', detail => {
          if (detail.name == match) handler(detail.value);
        });
      } else {
        onEvent('input', detail => {
          handler(detail.name, detail.value);
        });
      }
    }
    function resetInputs() {
      assertArgs("resetInputs", arguments, []);
      dispatchEvent("resetInputs");
    }
    function resetInput(name, value) {
      assertArgs("resetInput", arguments, ['string'], ['string', 'data']);
      dispatchEvent("resetInputs", {
        name,
        value
      });
    }
    function commitInput(name) {
      assertArgs("commitInput", arguments, ['string']);
      dispatchEvent("commitInputs", {
        name
      });
    }

    const handlers$1 = {
      'startPage': function startPage() {},
      // default
      'completePage': function completePage() {},
      // default
      'nextIteration': null,
      'completeIteration': null,
      'startTrial': null,
      'completeTrial': null
    };
    function handle$1(hook, args) {
      let handler = handlers$1[hook];
      if (!handler) throw new Error("Missing ".concat(hook, " handler"));
      setTimeout(async () => {
        await handler.apply(null, args);
        updatePage();
      });
    }
    function onStartPage(handler) {
      assertArgs("onStartPage", arguments, ['function']);
      handlers$1["startPage"] = handler;
    }
    function startPage() {
      handle$1("startPage");
    }
    function onCompletePage(handler) {
      assertArgs("onCompletePage", arguments, ['function']);
      handlers$1["completePage"] = handler;
    }
    function completePage() {
      assertArgs("completePage", arguments, []);
      handle$1("completePage");
      // this simulates submit button, including 'submit' event
      setTimeout(() => document.getElementById("form").requestSubmit());
    }
    function onNextIteration(handler) {
      assertArgs("onNextIteration", arguments, ['function']);
      handlers$1["nextIteration"] = handler;
    }
    function nextIteration() {
      assertArgs("nextIteration", arguments, []);
      handle$1("nextIteration");
    }
    function onCompleteIteration(handler) {
      assertArgs("onCompleteIteration", arguments, ['function']);
      handlers$1["completeIteration"] = handler;
    }
    function completeIteration() {
      assertArgs("completeIteration", arguments, []);
      handle$1("completeIteration");
    }
    function onStartTrial(handler) {
      assertArgs("onStartTrial", arguments, ['function']);
      handlers$1["startTrial"] = handler;
    }
    function startTrial(data) {
      assertArgs("startTrial", arguments, ['object']);
      handle$1("startTrial", arguments);
    }
    function onCompleteTrial(handler) {
      assertArgs("onCompleteTrial", arguments, ['function']);
      handlers$1["completeTrial"] = handler;
    }
    function completeTrial(data) {
      assertArgs("completeTrial", arguments, ['object']);
      handle$1("completeTrial", arguments);
    }

    const timeouts = {};
    function startTimeout(delay, name) {
      assertArgs("startTimeout", arguments, ['number', 'string']);
      cancelTimeout(name);
      timeouts[name] = window.setTimeout(function () {
        emitEvent('timeout', {
          name
        });
      }, delay);
    }
    function cancelTimeout(name) {
      assertArgs("cancelTimeout", arguments, ['string']);
      if (!(name in timeouts)) return;
      window.clearTimeout(timeouts[name]);
      delete timeouts[name];
    }
    function cancelTimeouts() {
      assertArgs("cancelTimeouts", arguments, []);
      for (let name in timeouts) {
        cancelTimeout(name);
      }
    }
    function onTimeout() {
      assertArgs("onTimeout", arguments, ['string', 'function']);
      let {
        handler,
        match
      } = pickArgs(arguments);
      onEvent('timeout', detail => {
        if (detail.name == match) handler();
      });
    }
    const timeouts_ph = {};
    function startPhases(schedule) {
      assertArgs("startPhases", arguments, ['object']);
      cancelPhases();
      let elapsed = 0;
      for (let name in schedule) {
        let duration = schedule[name];
        timeouts_ph["".concat(name, ".start")] = window.setTimeout(function () {
          emitEvent('phase', {
            name,
            start: true
          });
        }, elapsed);
        if (duration !== null) {
          elapsed += duration;
          timeouts_ph["".concat(name, ".end")] = window.setTimeout(function () {
            emitEvent('phase', {
              name,
              end: true
            });
          }, elapsed);
        }
      }
    }
    function cancelPhases() {
      assertArgs("cancelPhases", arguments, []);
      for (let name in timeouts_ph) {
        window.clearTimeout(timeouts_ph[name]);
        delete timeouts_ph[name];
      }
    }
    function onPhase() {
      assertArgs("onPhase", arguments, ['string', 'function'], ['function']);
      let {
        handler,
        match
      } = pickArgs(arguments);
      if (match) {
        onEvent('phase', detail => {
          if (detail.name == match && detail.start) handler();
        });
      } else {
        onEvent('phase', detail => {
          if (detail.start) handler(detail.name);
        });
      }
    }
    function onPhaseEnd() {
      assertArgs("onPhase", arguments, ['string', 'function']);
      let {
        handler,
        match
      } = pickArgs(arguments);
      onEvent('phase', detail => {
        if (detail.name == match && detail.end) handler();
      });
    }
    const timers = {},
      timers_t0 = {};
    function startTimer(delay, name) {
      assertArgs("startTimer", arguments, ['number', 'string']);
      cancelTimer(name);
      timers_t0[name] = window.performance.now();
      timers[name] = window.setInterval(function () {
        emitEvent('timer', {
          name,
          time: window.performance.now() - timers_t0[name]
        });
      }, delay);
      emitEvent('timer', {
        name,
        time: 0
      });
    }
    function cancelTimer(name) {
      assertArgs("cancelTimer", arguments, ['string']);
      if (!(name in timers)) return;
      window.clearInterval(timers[name]);
      delete timers[name];
      delete timers_t0[name];
    }
    function cancelTimers() {
      assertArgs("cancelTimers", arguments, []);
      for (let name in timers) {
        cancelTimer(name);
      }
    }
    function onTimer() {
      assertArgs("onTimer", arguments, ['string', 'function']);
      let {
        handler,
        match
      } = pickArgs(arguments);
      onEvent('timer', detail => {
        if (detail.name == match) handler(detail.time);
      });
    }

    function selectorDisplay(id) {
      return id == '*' ? "[ot-display]" : "[ot-display=".concat(id, "]");
    }
    function selectDisplays(ids) {
      let selector = isArray(ids) ? ids.map(id => selectorDisplay(id)).join(",") : selectorDisplay(ids);
      return document.querySelectorAll(selector);
    }
    function switchDisplays(switches) {
      let {
        on,
        off,
        only
      } = switches;
      if (only !== undefined) {
        off = '*';
        on = only;
      }
      if (off) {
        selectDisplays(off).forEach(e => e.setAttribute('hidden', ""));
      }
      if (on) {
        selectDisplays(on).forEach(e => e.removeAttribute('hidden'));
      }
    }
    function showDisplays() {
      let selected = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : "*";
      assertArgs("showDisplays", arguments, [], ['string'], ['array']);
      switchDisplays({
        on: selected
      });
    }
    function hideDisplays() {
      let selected = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : "*";
      assertArgs("hideDisplays", arguments, [], ['string'], ['array']);
      switchDisplays({
        off: selected
      });
    }
    function selectorInput(id) {
      return id == '*' ? "[ot-enable]" : "[ot-enable=".concat(id, "]");
    }
    function selectInputs(ids) {
      let selector = isArray(ids) ? ids.map(id => selectorInput(id)).join(",") : selectorInput(ids);
      return document.querySelectorAll(selector);
    }
    function switchInputs(switches) {
      let {
        on,
        off,
        only
      } = switches;
      if (only !== undefined) {
        off = '*';
        on = only;
      }
      if (off) {
        selectInputs(off).forEach(e => {
          e.setAttribute('disabled', "");
          e.blur();
        });
      }
      if (on) {
        selectInputs(on).forEach(e => {
          e.removeAttribute('disabled');
          if (e.hasAttribute('autofocus')) e.focus();
        });
      }
    }
    function enableInputs() {
      let selected = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : "*";
      assertArgs("enableInputs", arguments, [], ['string'], ['array']);
      switchInputs({
        on: selected
      });
    }
    function disableInputs() {
      let selected = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : "*";
      assertArgs("disableInputs", arguments, [], ['string'], ['array']);
      switchInputs({
        off: selected
      });
    }

    function preloadImage(url) {
      assertArgs("preloadImage", arguments, ['string']);
      return new Promise((resolve, reject) => {
        let img = new Image();
        img.loading = "eager";
        img.src = url;
        img.onload = () => resolve(img);
      });
    }
    function preloadImages(urls) {
      assertArgs("preloadImage", arguments, ['array']);
      return Promise.all(urls.map(url => preloadImage(url)));
    }

    function start(tag) {
      performance.mark("ot.".concat(tag, ".start"));
    }
    function mark(tag) {
      performance.mark("ot.".concat(tag));
    }
    function measure(tag) {
      return performance.measure("ot.".concat(tag, ".measure"), "ot.".concat(tag, ".start"), "ot.".concat(tag));
      // return performance.getEntriesByName(`otree.${tag}.measure`).slice(-1)[0];
    }

    function clear(tag) {
      performance.clearMarks("ot.".concat(tag, ".start"));
      performance.clearMarks("ot.".concat(tag));
      performance.clearMeasures("ot.".concat(tag, ".measure"));
    }
    function startTimeMeasurement() {
      let tag = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : "response";
      clear(tag);
      start(tag);
    }
    function getTimeMeasurement() {
      let tag = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : "response";
      mark(tag);
      let entry = measure(tag);
      return entry.duration;
    }

    async function delay(time, func) {
      assertArgs("delay", arguments, ['number', 'function'], ['number']);
      if (func === undefined) {
        return new Promise((resolve, reject) => {
          setTimeout(() => resolve(), time);
        });
      } else {
        return new Promise((resolve, reject) => {
          setTimeout(() => {
            func();
            updatePage();
            resolve();
          }, time);
        });
      }
    }

    const handlers = {};
    function handle(hook, data) {
      let handler = handlers[hook];
      if (!handler) throw new Error("Missing onLive('".concat(hook, "') handler"));
      setTimeout(async () => {
        await handler.apply(null, [data]);
        updatePage();
      });
    }
    function initLive() {
      if (window.liveSocket === undefined) return;
      window.liveSocket.onmessage = function (message) {
        let messages = JSON.parse(message.data);
        Object.entries(messages).forEach(entry => handle(entry[0], entry[1]));
      };
    }
    function onLive(type, handler) {
      if (window.liveSocket === undefined) {
        throw new Error("The page doesn't seem live");
      }
      assertArgs("onLive", arguments, ['string', 'function']);
      handlers[type] = handler;
    }
    function sendLive(type) {
      let data = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : null;
      if (window.liveSocket === undefined) {
        throw new Error("Missing live socket, the page is not live");
      }
      assertArgs("sendLive", arguments, ['string', 'object'], ['string']);
      window.liveSocket.send(JSON.stringify({
        [type]: data
      }));
    }

    function switchAttr(elem, attr, flag) {
      if (flag) {
        elem.setAttribute(attr, "");
      } else {
        elem.removeAttribute(attr);
      }
    }

    /** Base class for all directives
     *
     * implements generic initialization and updates
     * provides tools for event handlers binding and triggering
     */
    class otDirectiveBase {
      /** Defines parameters to parse form attributes
       *
       * returns obj:
       * - param_name: config
       * config:
       * - type: str = number|boolean|string|flag|name -- type of value to check, default= undefined
       * - optional: true|false -- if the param can be skipped, default = required
       * - default: ... -- default value for skipped or uninitialized params, default = undefined
       * - variable: true|false -- if the attribute should or should not be a var reference, default = undefined
       */
      parameters() {
        return {};
      }
      constructor(elem) {
        this.elem = elem;
        this.init(Object.fromEntries(Array.from(this.elem.attributes).map(a => [a.name, a.value])));
        this.render();
        this.setup();
      }

      /** initialize parameters and initial properties */
      init(attrs) {
        this.params = this.initParams(attrs);
        // NB: not using this.update to avoid excessive render
        let initial = Object.fromEntries(Object.entries(this.params).filter(_ref => {
          let [k, v] = _ref;
          return v.val !== undefined;
        }).map(_ref2 => {
          let [k, v] = _ref2;
          return [k, v.val];
        }));
        Object.assign(this, initial);
      }
      get disabled() {
        return this.elem.hasAttribute('disabled') || this.elem.hasAttribute('hidden');
      }

      /** setup event handlers */
      setup() {
        this.onPageEvent('ot.update', this.onUpdate);
      }

      /** render or update content */
      render() {}

      /** handle update of params */
      update(updates) {
        Object.assign(this, updates);
      }

      /** generic update handler */
      onUpdate(changes) {
        let updates = this.evalParams(changes);
        if (Object.entries(updates).length == 0) return;
        this.update(updates);
      }

      /** parses declared parameters from attributes
       * returns: param configs
       * - name: { val, var, type }
       */
      initParams(attrs) {
        let config = this.parameters();
        let params = {};
        for (let name in config) {
          let conf = config[name];
          try {
            let param = parseParam(name, conf, attrs);
            if (params) params[name] = param;
          } catch (e) {
            console.error(e.message);
            params = null;
          }
        }
        if (params === null) throw new Error("Failed to initialize some params");
        return params;
      }

      /** evaluate params from changes and global vars
       * returns: updates object
       * - name: value
       */
      evalParams(changes) {
        let values = {};
        for (let name in this.params) {
          try {
            let value = evalParam(name, this.params[name], changes, window.vars);
            if (values && value !== undefined) values[name] = value;
          } catch (e) {
            console.error(e.message);
            values = null;
          }
        }
        if (values === null) throw new Error("Failed to evaluate some params");
        return values;
      }

      /* util to wrap local method for handler */
      _wrap(handler) {
        function handle(event) {
          try {
            handler.call(this, event.detail, event);
          } catch (e) {
            console.error(e);
            console.error("Failed to handle ".concat(event.type, " for ").concat(this.constructor.name, " at"), this.elem);
          }
        }
        return handle.bind(this);
      }

      /** add an event handler on the host element (raw event names) */
      onElemEvent(type, handler) {
        this.elem.addEventListener(type, this._wrap(handler));
      }

      /** add an event handler on the page (still raw event names) */
      onPageEvent(type, handler) {
        document.body.addEventListener(type, this._wrap(handler));
      }

      /** queue an event on the host element */
      emitElemEvent(type, detail) {
        setTimeout(() => this.elem.dispatchEvent(new CustomEvent(type, {
          detail
        })));
      }

      /** synchronously dispatch an event on the host element */
      dispatchElemEvent(type, detail) {
        this.elem.dispatchEvent(new CustomEvent(type, {
          detail
        }));
      }
    }

    /** Base class for input directives
     *
     * implements resetting/toggling/commiting logic
     */
    class otInputBase extends otDirectiveBase {
      constructor(elem) {
        super(elem);
        switchAttr(this.elem, "input", true);
      }
      parameters() {
        return {
          name: {
            type: 'name',
            variable: false
          }
        };
      }
      setup() {
        super.setup();
        this.onPageEvent("ot.resetInputs", this.onReset);
        this.onElemEvent("ot.resetInputs", this.onReset);
        this.onPageEvent("ot.commitInputs", this.onCommit);
        this.onElemEvent("ot.commitInputs", this.onCommit);
      }
      onReset(detail) {
        if (detail && detail.name != this.name) return;
        this.reset(detail && 'value' in detail ? detail.value : null);
      }
      reset(value) {
        this.update({
          value
        });
      }
      onCommit(detail) {
        if (detail && detail.name != this.name) return;
        if (this.disabled) return;
        this.commit();
      }
      commit() {
        dispatchEvent('input', {
          name: this.name,
          value: this.value
        });
      }
      onRefocus() {
        this.refocus();
      }
      refocus() {
        if (this.disabled) {
          this.elem.blur();
        } else if (this.elem.hasAttribute("autofocus")) {
          this.elem.focus();
        }
      }
    }
    const registry = {};
    function registerDirective(cls, selector) {
      registry[selector] = cls;
    }
    function attachDirective(cls, selector) {
      document.querySelectorAll(selector).forEach(elem => {
        try {
          new cls(elem);
        } catch (e) {
          console.error(e);
          console.error("Failed to create directive ".concat(cls.name, " for ").concat(selector, " at"), elem);
        }
      });
    }
    function initDirectives() {
      for (let sel in registry) {
        attachDirective(registry[sel], sel);
      }
    }

    class otAttr extends otDirectiveBase {
      get attr_name() {}
      parameters() {
        return {
          value: {
            attr: "ot-".concat(this.attr_name),
            variable: true
          }
        };
      }
      render() {
        if (isVoid(this.value)) {
          this.elem.removeAttribute(this.attr_name);
        } else {
          this.elem.setAttribute(this.attr_name, this.value);
        }
      }
      update(updates) {
        super.update(updates);
        this.render();
      }
    }
    class otAttrMin extends otAttr {
      get attr_name() {
        return 'min';
      }
    }
    class otAttrMax extends otAttr {
      get attr_name() {
        return 'max';
      }
    }
    class otAttrHeight extends otAttr {
      get attr_name() {
        return 'height';
      }
    }
    class otAttrWidth extends otAttr {
      get attr_name() {
        return 'width';
      }
    }
    class otAttrSrc extends otAttr {
      get attr_name() {
        return 'src';
      }
    }
    class otAttrHref extends otAttr {
      get attr_name() {
        return 'href';
      }
    }
    registerDirective(otAttrMin, "[ot-min]");
    registerDirective(otAttrMax, "[ot-max]");
    registerDirective(otAttrHeight, "[ot-height]");
    registerDirective(otAttrWidth, "[ot-width]");
    registerDirective(otAttrSrc, "[ot-src]");
    registerDirective(otAttrHref, "[ot-href]");

    class otText extends otDirectiveBase {
      parameters() {
        return {
          value: {
            attr: "ot-text",
            variable: true
          }
        };
      }
      render() {
        let content = isVoid(this.value) ? "" : this.value;
        this.elem.innerText = content;
      }
      update(updates) {
        super.update(updates);
        this.render();
      }
    }
    registerDirective(otText, "[ot-text]");

    class otHTML extends otDirectiveBase {
      parameters() {
        return {
          value: {
            attr: "ot-html",
            variable: true
          }
        };
      }
      render() {
        let content = isVoid(this.value) ? "" : this.value;
        this.elem.innerHTML = content;
      }
      update(updates) {
        super.update(updates);
        this.render();
      }
    }
    registerDirective(otHTML, "[ot-html]");

    class otClass extends otDirectiveBase {
      parameters() {
        return {
          value: {
            attr: "ot-class",
            variable: true
          }
        };
      }
      init(attrs) {
        super.init(attrs);
        this.initial = Array.from(this.elem.classList);
      }
      render() {
        this.elem.classList.remove(...this.elem.classList);
        if (this.initial) this.elem.classList.add(...this.initial);
        if (isVoid(this.value) || !this.value) return;
        if (Array.isArray(this.value)) {
          this.elem.classList.add(...this.value);
        } else {
          this.elem.classList.add(this.value);
        }
      }
      update(updates) {
        super.update(updates);
        this.render();
      }
    }
    registerDirective(otClass, "[ot-class]");

    class otImg extends otDirectiveBase {
      parameters() {
        return {
          image: {
            attr: 'ot-img',
            variable: true
          }
        };
      }
      render() {
        if (isVoid(this.image)) return;
        let img = this.image;
        for (let attr of this.elem.attributes) {
          if (attr.name == 'src') continue;
          img.setAttribute(attr.name, attr.value);
        }
        this.elem.replaceWith(img);
        this.elem = img;
      }
      update(updates) {
        if (isVoid(updates.image)) updates.image = new Image();else if (!(updates.image instanceof HTMLImageElement)) {
          throw new Error("Invalid value of 'vars.".concat(this.params.image.var, "'; expected: preloaded HTMLImage"));
        }
        super.update(updates);
        this.render();
      }
    }
    registerDirective(otImg, "img[ot-img]");

    class otValue extends otDirectiveBase {
      parameters() {
        return {
          value: {
            attr: 'ot-value',
            variable: true
          }
        };
      }
      update(updates) {
        if (this.elem.hasAttribute('input')) {
          this.dispatchElemEvent("ot.resetInputs", {
            name: this.elem.getAttribute("name"),
            value: updates.value
          });
        } else {
          this.elem.value = updates.value;
        }
      }
    }
    registerDirective(otValue, "[ot-value]");

    class otStyle extends otDirectiveBase {
      parameters() {
        return {
          style: {
            attr: "ot-style",
            variable: true
          }
        };
      }
      update(updates) {
        let style = updates.style;

        // remove all customized properties
        while (this.elem.style[0] !== undefined) {
          this.elem.style[this.elem.style[0]] = null;
        }
        if (!isVoid(style)) {
          Object.assign(this.elem.style, style);
        }
      }
    }
    registerDirective(otStyle, "[ot-style]");

    /** ot-input for non-native elements
     *
     * Simulates element.value property
     * Taking value from 'value' attribute, constant or variable
     * Not resetting value.
     *
     * Expects to receive extrenal 'commitInput' event (from ot-click, ot-key or ot.commitInput)
     */
    class otInputBare extends otInputBase {
      parameters() {
        return {
          'ot-input': {
            type: 'flag'
          },
          name: {
            type: 'name',
            variable: false
          },
          value: {
            optional: true
          }
        };
      }
      get value() {
        return this.elem.value;
      }
      set value(val) {
        this.elem.value = val;
      }
      reset(value) {
        // not resetting
      }
    }

    /** ot-input for native inputs
     *
     * Utilize native element.value property
     * React on change event, whenever it comes
     */
    class otInputNative extends otInputBase {
      parameters() {
        return {
          'ot-input': {
            type: 'flag'
          },
          name: {
            type: 'name',
            variable: false
          }
        };
      }
      setup() {
        super.setup();
        this.onElemEvent("change", this.onCommit);
      }
      get value() {
        return this.elem.value;
      }
      set value(val) {
        this.elem.value = val;
      }
    }
    class otInputCheck extends otInputNative {
      get value() {
        return this.elem.checked;
      }
      set value(val) {
        this.elem.checked = !!val;
      }
    }
    class otInputRadio extends otInputNative {
      commit() {
        if (!this.elem.checked) return;
        super.commit();
      }
      get value() {
        return this.elem.value;
      }
      set value(val) {
        this.elem.checked = this.elem.value == val;
      }
    }
    registerDirective(otInputNative, "input[ot-input]:not([type=radio], [type=checkbox])");
    registerDirective(otInputCheck, "input[ot-input][type=checkbox]");
    registerDirective(otInputRadio, "input[ot-input][type=radio]");
    registerDirective(otInputNative, "select[ot-input]");
    registerDirective(otInputNative, "textarea[ot-input]");
    registerDirective(otInputBare, "[ot-input]:not(input, select, textarea)");

    class otEvent extends otInputBase {
      parameters() {
        return {
          name: {
            attr: 'ot-event',
            type: 'name',
            variable: false
          }
        };
      }
      commit() {
        dispatchEvent(this.name);
      }
    }
    registerDirective(otEvent, "[ot-event]");

    class otClick extends otDirectiveBase {
      parameters() {
        return {
          'ot-click': {
            type: 'flag'
          }
        };
      }
      setup() {
        this.onElemEvent('click', this.onClick);
      }
      onClick(detail, event) {
        if (this.disabled) return;
        event.preventDefault();
        event.stopImmediatePropagation();
        this.dispatchElemEvent("ot.commitInputs");
      }
    }
    registerDirective(otClick, "[ot-click]:not(button)");
    registerDirective(otClick, "button[type=button][ot-input]");
    registerDirective(otClick, "button[type=button][ot-event]");

    class otKey extends otDirectiveBase {
      init(attrs) {
        this.key = attrs['ot-kbd'];
        if (this.key.length != 1 && !this.key.match(/[A-Z]\w+/)) {
          throw new Error("Invalid attribute value: \"".concat(this.key, "\", expected a letter or a codename (see \"Code values for keyboard\" at developer.mozilla.org"));
        }
      }
      setup() {
        if (this.elem instanceof HTMLInputElement) {
          this.onElemEvent("keydown", this.onKey);
        } else {
          this.onPageEvent("keydown", this.onKey);
        }
      }
      onKey(detail, event) {
        if (this.disabled) return;
        if (this.key != event.key && this.key != event.code) return;
        event.preventDefault();
        event.stopImmediatePropagation();
        this.dispatchElemEvent("ot.commitInputs");
      }
    }
    registerDirective(otKey, "[ot-kbd]");

    class otPoint extends otInputBase {
      parameters() {
        return {
          'ot-point-input': {
            type: 'flag'
          },
          name: {
            type: 'name',
            variable: false
          }
        };
      }
      setup() {
        super.setup();
        this.onElemEvent('click', this.onClick);
      }
      onClick(detail, event) {
        if (this.disabled) return;
        this.update({
          value: {
            x: event.offsetX,
            y: event.offsetY
          }
        });
        this.commit();
      }
    }
    registerDirective(otPoint, "[ot-point-input]");

    const setters1 = {
      onStartPage,
      onCompletePage,
      onNextIteration,
      onCompleteIteration,
      onStartTrial,
      onCompleteTrial
    };
    function checkIntegrity(ns) {
      for (let nm in setters1) {
        if (window[ns][nm] !== setters1[nm]) {
          console.error("Invalid usage of ".concat(nm, "; Expected: ").concat(ns, ".").concat(nm, "(function() { ... })"));
        }
      }
    }
    window.addEventListener('DOMContentLoaded', () => {
      initDirectives();
      initLive();
      window.vars = {};
      checkIntegrity('ot');
    });
    window.addEventListener('load', () => {
      startPage();
    });

    exports.cancelPhases = cancelPhases;
    exports.cancelTimeout = cancelTimeout;
    exports.cancelTimeouts = cancelTimeouts;
    exports.cancelTimer = cancelTimer;
    exports.cancelTimers = cancelTimers;
    exports.commitInput = commitInput;
    exports.completeIteration = completeIteration;
    exports.completePage = completePage;
    exports.completeTrial = completeTrial;
    exports.delay = delay;
    exports.delayEvent = delayEvent;
    exports.disableInputs = disableInputs;
    exports.dispatchEvent = dispatchEvent;
    exports.emitEvent = emitEvent;
    exports.enableInputs = enableInputs;
    exports.evalParam = evalParam;
    exports.getTimeMeasurement = getTimeMeasurement;
    exports.hideDisplays = hideDisplays;
    exports.isArray = isArray;
    exports.isFunction = isFunction;
    exports.isHTMLElement = isHTMLElement;
    exports.isObject = isObject;
    exports.isPlainObject = isPlainObject;
    exports.isScalar = isScalar;
    exports.isVoid = isVoid;
    exports.keypath = keypath;
    exports.nextIteration = nextIteration;
    exports.onCompleteIteration = onCompleteIteration;
    exports.onCompletePage = onCompletePage;
    exports.onCompleteTrial = onCompleteTrial;
    exports.onDelete = onDelete;
    exports.onEvent = onEvent;
    exports.onInput = onInput;
    exports.onLive = onLive;
    exports.onNextIteration = onNextIteration;
    exports.onPhase = onPhase;
    exports.onPhaseEnd = onPhaseEnd;
    exports.onStartPage = onStartPage;
    exports.onStartTrial = onStartTrial;
    exports.onTimeout = onTimeout;
    exports.onTimer = onTimer;
    exports.onUpdate = onUpdate;
    exports.otDirectiveBase = otDirectiveBase;
    exports.otInputBase = otInputBase;
    exports.parseParam = parseParam;
    exports.parseValue = parseValue;
    exports.preloadImage = preloadImage;
    exports.preloadImages = preloadImages;
    exports.registerDirective = registerDirective;
    exports.resetInput = resetInput;
    exports.resetInputs = resetInputs;
    exports.sendLive = sendLive;
    exports.showDisplays = showDisplays;
    exports.startPage = startPage;
    exports.startPhases = startPhases;
    exports.startTimeMeasurement = startTimeMeasurement;
    exports.startTimeout = startTimeout;
    exports.startTimer = startTimer;
    exports.startTrial = startTrial;
    exports.switchDisplays = switchDisplays;
    exports.switchInputs = switchInputs;
    exports.updatePage = updatePage;

    return exports;

})({});
