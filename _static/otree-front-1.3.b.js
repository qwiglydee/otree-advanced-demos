/*!
otree-front v1.3.b
microframework for interactive pages for oTree platform
(C) qwiglydee@gmail.com
https://github.com/qwiglydee/otree-front
*/
var ot=function(e){"use strict";function t(e){return Array.isArray(e)}function n(e){return null==e||Number.isNaN(e)}function a(e){return Object.prototype.toString.call(e).startsWith("[object HTML")}function r(e){var t=typeof e;return"string"===t||("number"===t||("boolean"===t||("symbol"===t||(null==e||(e instanceof Symbol||(e instanceof String||(e instanceof Number||e instanceof Boolean)))))))}function i(e){return"[object Object]"===Object.prototype.toString.call(e)}function o(e){var t,n;return!1!==i(e)&&(void 0===(t=e.constructor)||!1!==i(n=t.prototype)&&!1!==n.hasOwnProperty("isPrototypeOf"))}function s(e,n){return Array.from(e).every(((e,a)=>function(e,n){switch(n){case"data":return!0;case"array":return t(e);case"object":return i(e);default:return typeof e===n}}(e,n[a])))}function l(e,t){for(var n=arguments.length,a=new Array(n>2?n-2:0),r=2;r<n;r++)a[r-2]=arguments[r];if(0==a.filter((e=>e.length==t.length&&s(t,e))).length){const t=a.map((t=>"".concat(e,"(").concat(t.join(", "),")"))).join(" or ");throw new Error("Invalid arguments, expected: ".concat(t))}}function c(e){return 2==e.length?{match:e[0],handler:e[1]}:{match:void 0,handler:e[0]}}const u=/^[a-zA-Z]\w+(\.\w+)*$/;function m(e,t){return t.endsWith(".*")&&(t=t.slice(0,-2)),t.split(".").reduce(((e,t)=>e&&t in e?e[t]:void 0),e)}var d=Object.freeze({__proto__:null,extract:m,length:function(e){return e.split(".").length},update:function(e,t,n){const a=t.split("."),r=a.slice(0,-1),i=a.slice(-1)[0];let o=r.length?function(e,t){return t.reduce(((e,t)=>e&&t in e?e[t]:void 0),e)}(e,r):e;if(void 0===o)throw new Error("Unreachable keypath ".concat(t));o[i]=n},upsert:function(e,t,n){const a=t.split("."),r=a.slice(0,-1),i=a.slice(-1)[0];let o=r.length?function(e,t){return t.reduce(((e,t)=>e&&t in e?e[t]:void 0),e)}(e,r):e;if(void 0===o)throw new Error("Unreachable keypath ".concat(t));o[i]=n},validate:function(e){return e.match(u)}});const h={string:/^.*$/,number:/^-?\d*(\.\d+)?$/,boolean:/^(true|false)$/,name:/^[a-zA-Z]\w+$/,variable:/^vars.[a-zA-Z]\w+(\.\w+)*(\.\*)?$/};function p(e,t){if(!(e in h))throw new Error("Unknown parameter type: ".concat(e));return t.match(h[e])}function f(e,t,n){if(!p(t,n))throw new Error("Invalid parameter '".concat(e,"'; expected: ").concat(t));switch(t){case"number":return Number(n);case"boolean":return"true"===n;case"variable":return n.slice(5);default:return n}}function v(e,t,n){void 0===t.type||t.type in h||Error("Unrecognized parameter type '".concat(t.type,"'"));let a=t.attr?n[t.attr]:n[e];if("flag"==t.type){if(""!=a&&null!=a)throw new Error("Invalid parameter '".concat(e,"'; expected: flag with no value"));return{val:e in n,type:"flag"}}if(void 0===a){if(!t.optional)throw new Error("Missing parameter '".concat(e,"'"));return{val:t.default,type:t.type}}if(p("variable",a)){if(!1===t.variable)throw new Error("Invalid parameter '".concat(e,"'; expected: value"));return{var:a.slice(5),type:t.type,val:t.default}}if(!0===t.variable)throw new Error("Invalid parameter '".concat(e,"'; expected: variable"));return void 0!==t.type?{val:f(e,t.type,a),type:t.type}:{val:a,type:void 0}}function g(e,t,n,a){if(void 0===t.var||!n.affect(t.var))return;let r=m(a,t.var);if(void 0===r)return null;if(t.type&&typeof r!=t.type)throw new Error("Invalid value of 'vars.".concat(t.var,"' for parameter '").concat(e,"'; expected: ").concat(t.type));return r}function y(e){return r(e)||i(e)||t(e)||a(e)}function w(e){let a=arguments.length>1&&void 0!==arguments[1]?arguments[1]:"";return function*(){if(""!=a&&y(e)&&(yield[a,n(e)?null:e]),o(r=e)||t(r))for(let[t,n]of Object.entries(e))y(n)&&(yield*w(n,a?"".concat(a,".").concat(t):t));var r}()}class b extends Set{affect(e){return Array.from(this.keys()).some((t=>{return n=t,(a=e).endsWith(".*")?n.startsWith(a.slice(0,-2)):a==n||a.startsWith(n+".");var n,a}))}}function E(e){let t=e.split(".");return t.map(((e,n)=>t.slice(0,n+1).join(".")))}function T(e,t){let n=new b,a=new Set([].concat(Array.from(e.keys()),Array.from(t.keys())));for(let r of a)E(r).some((e=>n.has(e)))||e.get(r)!==t.get(r)&&n.add(r);return n}let I=new Map;function x(){let e=2;for(;e>0;){e--;let n=(t=window.vars,new Map(w(t))),a=T(I,n);if(0==a.size)break;I=n,document.body.dispatchEvent(new CustomEvent("ot.update",{detail:a}))}var t}function k(e,t){l("dispatchEvent",arguments,["string","data"],["string"]),document.body.dispatchEvent(new CustomEvent("ot.".concat(e),{detail:t}))}function P(e,t){l("emitEvent",arguments,["string","data"],["string"]),setTimeout((()=>document.body.dispatchEvent(new CustomEvent("ot.".concat(e),{detail:t}))))}function A(e,t){l("onEvent",arguments,["string","function"]),document.body.addEventListener("ot.".concat(e),(async e=>{await t(e.detail,e),x()}))}const j={startPage:function(){},completePage:function(){},nextIteration:null,startTrial:null,completeTrial:null};function L(e,t){let n=j[e];if(!n)throw new Error("Missing ".concat(e," handler"));setTimeout((async()=>{await n.apply(null,t),x()}))}function S(e){l("onStartPage",arguments,["function"]),j.startPage=e}function C(){L("startPage")}function O(e){l("onNextIteration",arguments,["function"]),j.nextIteration=e}function M(e){l("onStartTrial",arguments,["function"]),j.startTrial=e}function _(e){l("onCompleteTrial",arguments,["function"]),j.completeTrial=e}const D={};function N(e){l("cancelTimeout",arguments,["string"]),e in D&&(window.clearTimeout(D[e]),delete D[e])}const U={};function z(){l("cancelPhases",arguments,[]);for(let e in U)window.clearTimeout(U[e]),delete U[e]}const H={},W={};function $(e){l("cancelTimer",arguments,["string"]),e in H&&(window.clearInterval(H[e]),delete H[e],delete W[e])}function F(e){return l("preloadImage",arguments,["string"]),new Promise(((t,n)=>{let a=new Image;a.loading="eager",a.src=e,a.onload=()=>t(a)}))}const B={};function Z(){void 0!==window.liveSocket&&(window.liveSocket.onmessage=function(e){let t=JSON.parse(e.data);Object.entries(t).forEach((e=>function(e,t){let n=B[e];if(!n)throw new Error("Missing onLive('".concat(e,"') handler"));setTimeout((async()=>{await n.apply(null,[t]),x()}))}(e[0],e[1])))})}class q{parameters(){return{}}constructor(e){this.elem=e,this.init(Object.fromEntries(Array.from(this.elem.attributes).map((e=>[e.name,e.value])))),this.render(),this.setup()}init(e){this.params=this.initParams(e);let t=Object.fromEntries(Object.entries(this.params).filter((e=>{let[t,n]=e;return void 0!==n.val})).map((e=>{let[t,n]=e;return[t,n.val]})));Object.assign(this,t)}setup(){this.onPageEvent("ot.update",this.onUpdate)}render(){}update(e){Object.assign(this,e)}onUpdate(e){let t=this.evalParams(e);0!=Object.entries(t).length&&this.update(t)}initParams(e){let t=this.parameters(),n={};for(let a in t){let r=t[a];try{let t=v(a,r,e);n&&(n[a]=t)}catch(e){console.error(e.message),n=null}}if(null===n)throw new Error("Failed to initialize some params");return n}evalParams(e){let t={};for(let n in this.params)try{let a=g(n,this.params[n],e,window.vars);t&&void 0!==a&&(t[n]=a)}catch(e){console.error(e.message),t=null}if(null===t)throw new Error("Failed to evaluate some params");return t}_wrap(e){return function(t){try{e.call(this,t.detail,t)}catch(e){console.error(e),console.error("Failed to handle ".concat(t.type," for ").concat(this.constructor.name," at"),this.elem)}}.bind(this)}onElemEvent(e,t){this.elem.addEventListener(e,this._wrap(t))}onPageEvent(e,t){document.body.addEventListener(e,this._wrap(t))}emitElemEvent(e,t){setTimeout((()=>this.elem.dispatchEvent(new CustomEvent(e,{detail:t}))))}dispatchElemEvent(e,t){this.elem.dispatchEvent(new CustomEvent(e,{detail:t}))}}class K extends q{constructor(e){super(e),e.setAttribute("input","")}parameters(){return{name:{type:"name",variable:!1}}}get disabled(){return this.elem.disabled||this.elem.hidden}setup(){super.setup(),this.onPageEvent("ot.toggleInputs",this.onToggle),this.onPageEvent("ot.resetInputs",this.onReset),this.onElemEvent("ot.resetInputs",this.onReset),this.onPageEvent("ot.commitInputs",this.onCommit),this.onElemEvent("ot.commitInputs",this.onCommit),this.toggle(!1)}onReset(e){e&&e.name!=this.name||this.reset(e&&"value"in e?e.value:null)}reset(e){this.update({value:e})}onToggle(e){(void 0===e.selected||e.selected.includes(this.name))&&this.toggle(e.state)}toggle(e){this.elem.disabled=!e,this.elem.disabled?(this.elem.setAttribute("disabled",""),this.elem.blur()):(this.elem.removeAttribute("disabled"),!this.elem.disabled&&this.elem.hasAttribute("autofocus")&&this.elem.focus())}onCommit(e){e&&e.name!=this.name||this.disabled||this.commit()}commit(){k("input",{name:this.name,value:this.value})}}const R={};function J(e,t){R[t]=e}function V(e,t){document.querySelectorAll(t).forEach((n=>{try{new e(n)}catch(a){console.error(a),console.error("Failed to create directive ".concat(e.name," for ").concat(t," at"),n)}}))}class X extends q{get attr_name(){}parameters(){return{value:{attr:"ot-".concat(this.attr_name),variable:!0}}}render(){n(this.value)?this.elem.removeAttribute(this.attr_name):this.elem.setAttribute(this.attr_name,this.value)}update(e){super.update(e),this.render()}}J(class extends X{get attr_name(){return"min"}},"[ot-min]"),J(class extends X{get attr_name(){return"max"}},"[ot-max]"),J(class extends X{get attr_name(){return"height"}},"[ot-height]"),J(class extends X{get attr_name(){return"width"}},"[ot-width]"),J(class extends X{get attr_name(){return"src"}},"[ot-src]"),J(class extends X{get attr_name(){return"href"}},"[ot-href]");J(class extends q{parameters(){return{value:{attr:"ot-text",variable:!0}}}render(){let e=n(this.value)?"":this.value;this.elem.innerText=e}update(e){super.update(e),this.render()}},"[ot-text]");J(class extends q{parameters(){return{value:{attr:"ot-html",variable:!0}}}render(){let e=n(this.value)?"":this.value;this.elem.innerHTML=e}update(e){super.update(e),this.render()}},"[ot-html]");J(class extends q{parameters(){return{value:{attr:"ot-class",variable:!0}}}init(e){super.init(e),this.initial=Array.from(this.elem.classList)}render(){this.elem.classList.remove(...this.elem.classList),this.initial&&this.elem.classList.add(...this.initial),!n(this.value)&&this.value&&(Array.isArray(this.value)?this.elem.classList.add(...this.value):this.elem.classList.add(this.value))}update(e){super.update(e),this.render()}},"[ot-class]");function Y(e,t){e.hidden=t,!0===t?e.setAttribute("hidden",""):e.removeAttribute("hidden")}J(class extends q{parameters(){return{image:{attr:"ot-img",variable:!0}}}render(){if(n(this.image))return;let e=this.image;for(let t of this.elem.attributes)"src"!=t.name&&e.setAttribute(t.name,t.value);this.elem.replaceWith(e),this.elem=e}update(e){if(n(e.image))e.image=new Image;else if(!(e.image instanceof HTMLImageElement))throw new Error("Invalid value of 'vars.".concat(this.params.image.var,"'; expected: preloaded HTMLImage"));super.update(e),this.render()}},"img[ot-img]");J(class extends q{parameters(){return{name:{attr:"ot-display",type:"name",variable:!1}}}setup(){super.setup(),this.onPageEvent("ot.toggleDisplays",this.onToggle),this.toggle(!1)}toggle(e){Y(this.elem,!e),this.toggleDescendants()}toggleDescendants(){this.elem.querySelectorAll("input, select, textarea, [input]").forEach((e=>{e.removeAttribute("hidden"),Y(e,null!==e.closest("[hidden]"))}))}onToggle(e){(void 0===e.selected||e.selected.includes(this.name))&&this.toggle(e.state)}},"[ot-display]");J(class extends q{parameters(){return{value:{attr:"ot-value",variable:!0}}}update(e){this.elem.hasAttribute("input")?this.dispatchElemEvent("ot.resetInputs",{name:this.elem.getAttribute("name"),value:e.value}):this.elem.value=e.value}},"[ot-value]");J(class extends q{parameters(){return{style:{attr:"ot-style",variable:!0}}}update(e){let t=e.style;for(;void 0!==this.elem.style[0];)this.elem.style[this.elem.style[0]]=null;n(t)||Object.assign(this.elem.style,t)}},"[ot-style]");class G extends K{parameters(){return{"ot-input":{type:"flag"},name:{type:"name",variable:!1}}}setup(){super.setup(),this.onElemEvent("change",this.onCommit)}get value(){return this.elem.value}set value(e){this.elem.value=e}}J(G,"input[ot-input]:not([type=radio], [type=checkbox])"),J(class extends G{get value(){return this.elem.checked}set value(e){this.elem.checked=!!e}},"input[ot-input][type=checkbox]"),J(class extends G{commit(){this.elem.checked&&super.commit()}get value(){return this.elem.value}set value(e){this.elem.checked=this.elem.value==e}},"input[ot-input][type=radio]"),J(G,"select[ot-input]"),J(G,"textarea[ot-input]"),J(class extends K{parameters(){return{"ot-input":{type:"flag"},name:{type:"name",variable:!1},value:{optional:!0}}}get value(){return this.elem.value}set value(e){this.elem.value=e}reset(e){}},"[ot-input]:not(input, select, textarea)");J(class extends K{parameters(){return{name:{attr:"ot-event",type:"name",variable:!1}}}commit(){k(this.name)}},"[ot-event]");class Q extends q{parameters(){return{"ot-click":{type:"flag"}}}setup(){this.onElemEvent("click",this.onClick)}onClick(){this.elem.disabled||this.dispatchElemEvent("ot.commitInputs")}}J(Q,"[ot-click]:not(button)"),J(Q,"button[type=button][ot-input]"),J(Q,"button[type=button][ot-event]");J(class extends q{init(e){if(this.key=e["ot-kbd"],1!=this.key.length&&!this.key.match(/[A-Z]\w+/))throw new Error('Invalid attribute value: "'.concat(this.key,'", expected a letter or a codename (see "Code values for keyboard" at developer.mozilla.org'))}setup(){this.elem instanceof HTMLInputElement?this.onElemEvent("keydown",this.onKey):this.onPageEvent("keydown",this.onKey)}onKey(e,t){this.disabled||this.key!=t.key&&this.key!=t.code||(t.preventDefault(),this.dispatchElemEvent("ot.commitInputs"))}},"[ot-kbd]");J(class extends K{parameters(){return{"ot-point-input":{type:"flag"},name:{type:"name",variable:!1}}}setup(){super.setup(),this.onElemEvent("click",this.onClick)}onClick(e,t){this.disabled||(this.update({value:{x:t.offsetX,y:t.offsetY}}),this.commit())}},"[ot-point-input]");const ee={onStartPage:S,onNextIteration:O,onStartTrial:M,onCompleteTrial:_};return window.addEventListener("load",(()=>{!function(e){for(let t in ee)window[e][t]!==ee[t]&&console.error("Broken ".concat(t,"; Expected usage: ").concat(e,".").concat(t,"(function)"))}("ot"),function(){for(let e in R)V(R[e],e)}(),Z(),window.vars={},C()})),e.cancelPhases=z,e.cancelTimeout=N,e.cancelTimeouts=function(){l("cancelTimeouts",arguments,[]);for(let e in D)N(e)},e.cancelTimer=$,e.cancelTimers=function(){l("cancelTimers",arguments,[]);for(let e in H)$(e)},e.commitInput=function(e){l("commitInput",arguments,["string"]),k("commitInputs",{name:e})},e.completePage=function(){l("completePage",arguments,[]),L("completePage"),setTimeout((()=>document.querySelector("form#form").submit()))},e.completeTrial=function(e){l("completeTrial",arguments,["object"]),L("completeTrial",arguments)},e.delay=async function(e,t){return l("delay",arguments,["number","function"],["number"]),new Promise(void 0===t?(t,n)=>{setTimeout((()=>t()),e)}:(n,a)=>{setTimeout((()=>{t(),x(),n()}),e)})},e.delayEvent=function(e,t,n){l("delayEvent",arguments,["number","string","data"],["number","string"]),setTimeout((()=>document.body.dispatchEvent(new CustomEvent("ot.".concat(t),{detail:n}))),e)},e.disableInputs=function(e){l("disableInputs",arguments,[],["string"],["array"]),"string"==typeof e&&(e=[e]),k("toggleInputs",{state:!1,selected:e})},e.dispatchEvent=k,e.emitEvent=P,e.enableInputs=function(e){l("enableInputs",arguments,[],["string"],["array"]),"string"==typeof e&&(e=[e]),P("toggleInputs",{state:!0,selected:e})},e.evalParam=g,e.getTimeMeasurement=function(){let e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:"response";return function(e){performance.mark("ot.".concat(e))}(e),function(e){return performance.measure("ot.".concat(e,".measure"),"ot.".concat(e,".start"),"ot.".concat(e))}(e).duration},e.hideDisplays=function(e){l("hideDisplays",arguments,[],["string"],["array"]),"string"==typeof e&&(e=[e]),P("toggleDisplays",{state:!1,selected:e})},e.isArray=t,e.isFunction=function(e){return"function"==typeof e},e.isHTMLElement=a,e.isObject=i,e.isPlainObject=o,e.isScalar=r,e.isVoid=n,e.keypath=d,e.nextIteration=function(){l("nextIteration",arguments,[]),L("nextIteration")},e.onCompletePage=function(e){l("onCompletePage",arguments,["function"]),j.completePage=e},e.onCompleteTrial=_,e.onDelete=function(e,t){let a;try{l("onDelete",arguments,["string","function"]),a=f("variable","variable",e)}catch(e){throw console.error(e),new Error("Invalid onDelete usage")}document.body.addEventListener("ot.update",(function(e){if(e.detail.affect(a)){n(m(window.vars,a))&&t()}}))},e.onEvent=A,e.onInput=function(){l("onInput",arguments,["string","function"],["function"]);let{handler:e,match:t}=c(arguments);A("input",void 0!==t?n=>{n.name==t&&e(n.value)}:t=>{e(t.name,t.value)})},e.onLive=function(e,t){if(void 0===window.liveSocket)throw new Error("The page doesn't seem live");l("onLive",arguments,["string","function"]),B[e]=t},e.onNextIteration=O,e.onPhase=function(){l("onPhase",arguments,["string","function"],["function"]);let{handler:e,match:t}=c(arguments);A("phase",t?n=>{n.name==t&&n.start&&e()}:t=>{t.start&&e(t.name)})},e.onPhaseEnd=function(){l("onPhase",arguments,["string","function"]);let{handler:e,match:t}=c(arguments);A("phase",(n=>{n.name==t&&n.end&&e()}))},e.onStartPage=S,e.onStartTrial=M,e.onTimeout=function(){l("onTimeout",arguments,["string","function"]);let{handler:e,match:t}=c(arguments);A("timeout",(n=>{n.name==t&&e()}))},e.onTimer=function(){l("onTimer",arguments,["string","function"]);let{handler:e,match:t}=c(arguments);A("timer",(n=>{n.name==t&&e(n.time)}))},e.onUpdate=function(e,t){let a;try{l("onUpdate",arguments,["string","function"]),a=f("variable","variable",e)}catch(e){throw console.error(e),new Error("Invalid onUpdate usage")}document.body.addEventListener("ot.update",(function(e){if(e.detail.affect(a)){let e=m(window.vars,a);n(e)||t(e)}}))},e.otDirectiveBase=q,e.otInputBase=K,e.parseParam=v,e.parseValue=f,e.preloadImage=F,e.preloadImages=function(e){return l("preloadImage",arguments,["array"]),Promise.all(e.map((e=>F(e))))},e.registerDirective=J,e.resetInput=function(e,t){l("resetInput",arguments,["string"],["string","data"]),k("resetInputs",{name:e,value:t})},e.resetInputs=function(){l("resetInputs",arguments,[]),k("resetInputs")},e.sendLive=function(e){let t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:null;if(void 0===window.liveSocket)throw new Error("Missing live socket, the page is not live");l("sendLive",arguments,["string","object"],["string"]),window.liveSocket.send(JSON.stringify({[e]:t}))},e.showDisplays=function(e){l("showDisplays",arguments,[],["string"],["array"]),"string"==typeof e&&(e=[e]),P("toggleDisplays",{state:!0,selected:e})},e.startPage=C,e.startPhases=function(e){l("startPhases",arguments,["object"]),z();let t=0;for(let n in e){let a=e[n];U["".concat(n,".start")]=window.setTimeout((function(){P("phase",{name:n,start:!0})}),t),null!==a&&(t+=a,U["".concat(n,".end")]=window.setTimeout((function(){P("phase",{name:n,end:!0})}),t))}},e.startTimeMeasurement=function(){let e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:"response";!function(e){performance.clearMarks("ot.".concat(e,".start")),performance.clearMarks("ot.".concat(e)),performance.clearMeasures("ot.".concat(e,".measure"))}(e),function(e){performance.mark("ot.".concat(e,".start"))}(e)},e.startTimeout=function(e,t){l("startTimeout",arguments,["number","string"]),N(t),D[t]=window.setTimeout((function(){P("timeout",{name:t})}),e)},e.startTimer=function(e,t){l("startTimer",arguments,["number","string"]),$(t),W[t]=window.performance.now(),H[t]=window.setInterval((function(){P("timer",{name:t,time:window.performance.now()-W[t]})}),e),P("timer",{name:t,time:0})},e.startTrial=function(e){l("startTrial",arguments,["object"]),L("startTrial",arguments)},e.updatePage=x,e}({});