/*!
otree-front v2.0.b2
Microframework for interactive pages for oTree platform
(C) qwiglydee@gmail.com
https://github.com/oTree-org/otree-front
*/
var ot=function(t){"use strict";function e(t){return Array.isArray(t)}function i(t){return"function"==typeof t}function n(t){return null==t||Number.isNaN(t)}function s(t){var e=typeof t;return"string"===e||("number"===e||("boolean"===e||("symbol"===e||(null==t||(t instanceof Symbol||(t instanceof String||(t instanceof Number||t instanceof Boolean)))))))}function r(t){return"[object Object]"===Object.prototype.toString.call(t)}function o(t){var e,i;return!1!==r(t)&&(void 0===(e=t.constructor)||!1!==r(i=e.prototype)&&!1!==i.hasOwnProperty("isPrototypeOf"))}function a(t,n){return Array.from(t).every(((t,s)=>function(t,n){switch(n){case"any":return!0;case"array":return e(t);case"object":return r(t);case"class":return i(t);default:return typeof t===n}}(t,n[s])))}function c(t,e){for(var i=arguments.length,n=new Array(i>2?i-2:0),s=2;s<i;s++)n[s-2]=arguments[s];if(0==n.filter((t=>t.length==e.length&&a(e,t))).length){const e=n.map((e=>"".concat(t,"(").concat(e.join(", "),")"))).join(" or ");throw new Error("Invalid arguments, expected: ".concat(e))}}function*u(t){let e=t.split(".");for(let t=0;t<e.length-1;t++)yield[e.slice(0,t+1).join("."),e.slice(t+1).join(".")]}function l(t){return s(t)||r(t)||e(t)||t instanceof HTMLElement}function m(t){let i=arguments.length>1&&void 0!==arguments[1]?arguments[1]:"";return function*(){if(""!=i&&l(t)&&(yield[i,n(t)?null:t]),o(s=t)||e(s))for(let[e,n]of Object.entries(t))l(n)&&(yield*m(n,i?"".concat(i,".").concat(e):e));var s}()}class h extends Map{affect(t){let e=t.endsWith(".*"),i=e?t.slice(0,-2):t;if(this.has(i))return!0;for(let[t,e]of u(i))if(this.has(t))return!0;if(e){let t=i+".";for(let e of this.keys())if(e.startsWith(t))return!0}return!1}extract(t){let e=t.endsWith(".*")?t.slice(0,-2):t;if(this.has(e))return this.get(e);for(let[t,s]of u(e))if(this.has(t))return i=this.get(t),"string"==typeof(n=s)&&(n=n.split(".")),n.reduce(((t,e)=>t&&e in t?t[e]:void 0),i);var i,n}}function d(t,e){let i=new Set([].concat(Array.from(t.keys()),Array.from(e.keys()))),n=Array.from(i).filter((i=>t.get(i)!==e.get(i)));return n=n.filter((t=>{return!(e=t,Array.from(u(e)).map((t=>t[0]))).some((t=>n.includes(t)));var e})),new h(n.map((t=>[t,e.has(t)?e.get(t):null])))}function p(){let t=(e=window.vars,new Map(m(e)));var e;let i=d(window.ot_snapshot,t);i.size&&(window.ot_snapshot=t,document.body.dispatchEvent(new CustomEvent("ot.update",{detail:{changes:i}})))}function f(t,e){c("triggerEvent",arguments,["string"],["string","object"]),document.body.dispatchEvent(new CustomEvent("ot.".concat(t),{detail:e}))}function v(t){f("submitted"),t.preventDefault(),document.getElementById("form").checkValidity()&&setTimeout((()=>g()))}function g(){HTMLFormElement.prototype.submit.call(document.getElementById("form"))}function y(t){return"#".concat(t)}function b(t){return"[id|=".concat(t.slice(0,-2),"]")}function w(t){return"[name=".concat(t,"]")}function E(t){return"".concat(w(t),",").concat(y(t))}function x(t){return t.endsWith("-*")?b(t):y(t)}function A(t){return t.endsWith("-*")?b(t):E(t)}function k(t,i){return e(i)||(i=[i]),i.map((e=>function(t,e){let i=t(e),n=document.querySelectorAll(i);if(!n.length)throw Error("No elements found for: ".concat(e));return Array.from(n).map((t=>[i,t]))}(t,e))).flat()}function T(){let t="[name]";return Array.from(document.querySelectorAll(t)).map((e=>[t,e]))}function I(t){return t instanceof HTMLInputElement||t instanceof HTMLTextAreaElement||t instanceof HTMLSelectElement}function P(t){return["text","textarea","email","tel","date","time","datetime-local","url","number"].includes(t.type)}function C(t){return["radio","checkbox"].includes(t.type)}function M(t){t.setAttribute("hidden","")}function j(t){t.removeAttribute("hidden")}function S(t){t.setAttribute("disabled","")}function D(t){t.removeAttribute("disabled")}function L(t,e){return t.forEach((t=>{let[i,n]=t;return e(n)}))}function O(t){let e=t.map((t=>t[0])).join(","),i=document.querySelector("[autofocus]:enabled:is(".concat(e,"), *:is(").concat(e,") [autofocus]:enabled"));i&&i.focus()}class _{constructor(t){this.name=t,this.started=0,this.counter=0,this.handler=null}start(){this.started=Date.now(),this.counter=0,window.ot_timers[this.name]=this}elapsed(){return Date.now()-this.started}cancel(){window.clearTimeout(this.handler),delete window.ot_timers[this.name]}}class N extends _{constructor(t,e){super(t),this.timeout=e}start(){super.start(),this.handler=window.setTimeout((()=>{f("timer",{name:this.name,elapsed:this.elapsed(),count:1})}),this.timeout)}}class V extends _{constructor(t,e,i){super(t),this.period=e,this.count=i}start(){super.start(),this.handler=window.setTimeout((()=>{f("timer",{name:this.name,elapsed:this.elapsed(),count:0}),this.restart()}),0)}restart(){this.handler=window.setInterval((()=>{this.counter+=1,f("timer",{name:this.name,elapsed:this.elapsed(),count:this.counter}),this.count&&this.counter>=this.count&&this.cancel()}),this.period)}}class q extends _{constructor(t,e){super(t),this.intervals=e}start(){super.start(),this.handler=window.setTimeout((()=>{f("timer",{name:this.name,elapsed:this.elapsed(),count:0}),this.restart()}),0)}restart(){this.handler=window.setTimeout((()=>{this.counter+=1,f("timer",{name:this.name,elapsed:this.elapsed(),count:this.counter}),this.counter>=this.intervals.length?this.cancel():this.restart()}),this.intervals[this.counter])}}function H(){window.ot_timers={}}function W(t){c("cancelTimer",arguments,["string"]),t in window.ot_timers&&window.ot_timers[t].cancel()}function R(t){return c("preloadImage",arguments,["string"]),new Promise(((e,i)=>{let n=new Image;n.loading="eager",n.src=t,n.onload=()=>e(n)}))}function B(t,e){return t.forEach((t=>{let[i,n]=t;return e(n)}))}function K(t){C(t)?t.checked=t.defaultChecked:t.value=t.defaultValue,t.dispatchEvent(new Event("ot.reset"))}function F(t){t.dispatchEvent(new Event("ot.commit"))}function z(t,e,i){return(e=function(t){var e=function(t,e){if("object"!=typeof t||null===t)return t;var i=t[Symbol.toPrimitive];if(void 0!==i){var n=i.call(t,e||"default");if("object"!=typeof n)return n;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===e?String:Number)(t)}(t,"string");return"symbol"==typeof e?e:String(e)}(e))in t?Object.defineProperty(t,e,{value:i,enumerable:!0,configurable:!0,writable:!0}):t[e]=i,t}class U{constructor(t){z(this,"params",{}),this.elem=t}get hidden(){return this.elem.hasAttribute("hidden")||null!=this.elem.closest("[hidden]")}get disabled(){return this.elem.hasAttribute("disabled")}get focused(){return this.elem===document.activeElement}get active(){return!this.hidden&&!this.disabled}init(){}render(){}update(t){this.render()}reset(){this.render()}commit(t){void 0===t&&(t=this.value),this.triggerPageEvent("ot.input",{name:this.name,value:t})}initParams(){this.paramVars={};for(let t in this.params){let e=this.params[t],i=this.elem.getAttribute(e.attr||t);"string"==typeof i&&i.startsWith("vars.")&&(this.paramVars[t]=i.slice(5),i=void 0),this[t]=n(i)?e.default:i}}updateParams(t){let e=Object.entries(this.paramVars).filter((e=>{let[i,n]=e;return t.affect(n)}));return e.forEach((e=>{let[i,n]=e;return this[i]=t.extract(n)})),new Set(e.map((t=>{let[e,i]=t;return e})))}onEvent(t,e,i){t.addEventListener(e,(t=>{try{i.call(this,t)}catch(e){console.error(e),console.error("Failed to handle '".concat(t.type,"' for ").concat(this.constructor.name," at"),this.elem)}}))}onPageEvent(t,e){this.onEvent(document.body,t,e)}onElemEvent(t,e){this.onEvent(this.elem,t,e)}triggerElemEvent(t){let e=new Event(t);this.elem.dispatchEvent(e)}triggerPageEvent(t,e){let i=new CustomEvent(t,{detail:e});i.source=this.elem,document.body.dispatchEvent(i)}}class X extends U{init(){this.initParams(),this.render(),this.onPageEvent("ot.update",this.onUpdate)}onUpdate(t){let e=t.detail.changes,i=this.updateParams(e);i.size&&this.update(i)}}class Y extends U{get value(){return this.elem.value}set value(t){this.elem.value=t}init(){if(!I(this.elem))throw Error("This directive is for native inputs only");if(!this.elem.hasAttribute("name"))throw Error("Missing `name` attribute");this.name=this.elem.getAttribute("name"),this.elem.setAttribute("input",""),this.initParams(),this.render(),this.onElemEvent("change",this.onChange),this.onElemEvent("ot.commit",this.onCommit),this.onElemEvent("ot.reset",this.onReset)}onChange(){this.active&&(this.reset(),this.commit())}onCommit(){this.commit()}onReset(){this.reset()}}class Z extends U{init(){this.combined=void 0!==Array.from(Object.values(this.elem.ot)).find((t=>t instanceof Y||t instanceof G)),this.combined||(this.name=this.elem.getAttribute("name"),this.elem.value=this.elem.getAttribute("value"),this.elem.defaultValue=this.elem.value),this.initParams()}trigger(){this.active&&(this.combined?this.triggerElemEvent("ot.commit"):this.commit(this.elem.value))}}class G extends U{get value(){return this.input?this.input.value:this.elem.value}set value(t){this.input?this.input.value=t:this.elem.value=t}init(){if(I(this.elem))throw Error("This directive is not for native inputs");if(!this.elem.hasAttribute("name")&&!this.elem.hasAttribute("input"))throw Error("Missing `name` or `input` attribute");if(this.params.value||(this.params.value={}),this.elem.hasAttribute("input")){if(this.name=this.elem.getAttribute("input"),this.input=document.querySelector("input[name=".concat(this.name,"]")),!this.input)throw Error("Linked input not found: ".concat(this.name));this.input.hasAttribute("value")&&(this.params.value.default=this.input.defaultValue)}else this.name=this.elem.getAttribute("name");this.initParams(),this.input?this.input.defaultValue=this.value:this.elem.defaultValue=this.value,this.render(),this.onPageEvent("ot.update",this.onUpdate),this.onElemEvent("ot.commit",this.onCommit),this.input?(this.onEvent(this.input,"change",this.onChange),this.onEvent(this.input,"ot.reset",this.onReset)):this.onEvent(this.elem,"ot.reset",this.onReset)}onUpdate(t){let e=t.detail.changes,i=this.updateParams(e);i.size&&this.update(i)}onChange(){this.active&&(this.reset(),this.commit())}onCommit(){this.commit()}onReset(){this.reset()}}function J(t,e){c("attachDirective",arguments,["class","string"]),document.querySelectorAll(e).forEach((e=>{void 0===e.ot&&(e.ot={});try{let i=new t(e);i.init(),e.ot[t.name]=i}catch(i){console.error(i),console.error("Failed to create directive ".concat(t.name," at"),e)}}))}class Q extends X{constructor(){super(...arguments),z(this,"params",{val:{attr:"ot-text"}})}render(){n(this.val)?this.elem.textContent="":this.elem.textContent=this.val}}class $ extends X{constructor(){super(...arguments),z(this,"params",{val:{attr:"ot-html"}})}render(){n(this.val)?this.elem.innerHTML="":this.elem.innerHTML=this.val}}class tt extends X{constructor(){super(...arguments),z(this,"attr","foo"),z(this,"params",{val:{attr:"ot-foo"}})}render(){n(this.val)?this.elem.removeAttribute(this.attr):this.elem.setAttribute(this.attr,this.val)}}class et extends tt{constructor(){super(...arguments),z(this,"attr","min"),z(this,"params",{val:{attr:"ot-min"}})}}class it extends tt{constructor(){super(...arguments),z(this,"attr","max"),z(this,"params",{val:{attr:"ot-max"}})}}class nt extends tt{constructor(){super(...arguments),z(this,"attr","step"),z(this,"params",{val:{attr:"ot-step"}})}}class st extends tt{constructor(){super(...arguments),z(this,"attr","width"),z(this,"params",{val:{attr:"ot-width"}})}}class rt extends tt{constructor(){super(...arguments),z(this,"attr","height"),z(this,"params",{val:{attr:"ot-height"}})}}class ot extends tt{constructor(){super(...arguments),z(this,"attr","href"),z(this,"params",{val:{attr:"ot-href"}})}}class at extends tt{constructor(){super(...arguments),z(this,"attr","src"),z(this,"params",{val:{attr:"ot-src"}})}}class ct extends X{constructor(){super(...arguments),z(this,"params",{val:{attr:"ot-class"}})}init(){this.initial=Array.from(this.elem.classList),super.init()}render(){let t=this.initial.slice();n(this.val)||(Array.isArray(this.val)?t=t.concat(this.val):t.push(this.val)),this.elem.classList.remove(...this.elem.classList),this.elem.classList.add(...t)}}class ut extends X{constructor(){super(...arguments),z(this,"params",{val:{attr:"ot-value"}})}update(){n(this.val)?this.elem.value=null:this.elem.value=this.val,this.triggerElemEvent("ot.reset")}}class lt extends Y{}class mt extends Y{constructor(){super(...arguments),z(this,"params",{autocommit:{default:null}})}init(){super.init(),this.onElemEvent("keypress",this.onKey),""==this.autocommit&&(this.autocommit=350),this.autocommit&&this.onElemEvent("input",this.onAutocommit)}commit(){"number"==this.elem.type?super.commit(Number(this.value)):super.commit()}onKey(t){"Enter"===t.key&&t.preventDefault()}onAutocommit(){this.commit_timeout&&window.clearTimeout(this.commit_timeout),this.commit_timeout=window.setTimeout((()=>this.commit()),this.autocommit)}}class ht extends Y{commit(){super.commit(Number(this.value))}}class dt extends Y{commit(){this.elem.checked&&super.commit()}}class pt extends Y{commit(){"on"==this.elem.value?super.commit(this.elem.checked):super.commit(this.elem.checked?this.value:null)}}class ft extends Z{init(){super.init(),this.onElemEvent("click",this.onClick)}onClick(){this.active&&this.trigger()}}class vt extends Z{constructor(){super(...arguments),z(this,"params",{key:{attr:"ot-key-input"}})}init(){if(super.init(),1!=this.key.length&&!this.key.match(/[A-Z]\w+/))throw new Error('Invalid key name: "'.concat(this.key,'", expected a letter or a codename.'));P(this.elem)?this.onElemEvent("keypress",this.onKey):this.onPageEvent("keypress",this.onKey)}onKey(t){!this.active||this.key!=t.key&&this.key!=t.code||(t.preventDefault(),t.stopImmediatePropagation(),this.trigger())}}class gt extends U{init(){super.init(),this.name=this.elem.getAttribute("name"),this.onElemEvent("click",this.onClick)}onClick(t){this.active&&this.commit({x:t.offsetX,y:t.offsetY})}}return window.addEventListener("DOMContentLoaded",(()=>{J(Q,"[ot-text]"),J($,"[ot-html]"),J(et,"[ot-min]"),J(it,"[ot-max]"),J(nt,"[ot-step]"),J(st,"[ot-width]"),J(rt,"[ot-height]"),J(at,"[ot-src]"),J(ot,"[ot-href]"),J(ct,"[ot-class]"),J(ut,"[ot-value]"),J(mt,"input[ot-input]:is([type=text],[type=number])"),J(mt,"textarea[ot-input]"),J(ht,"input[ot-input][type=range]"),J(dt,"input[ot-input][type=radio]"),J(pt,"input[ot-input][type=checkbox]"),J(lt,"input[ot-input]:not([type=text],[type=number],[type=range],[type=radio],[type=checkbox])"),J(lt,"select[ot-input]"),J(gt,"[ot-point-input]"),J(vt,"[ot-key-input]"),J(ft,"[ot-click-input]"),window.vars={},window.ot_snapshot=new Map,document.getElementById("form").addEventListener("submit",v),H()})),window.addEventListener("load",(()=>{f("loaded")})),t.ContentDirective=X,t.DirectiveBase=U,t.NativeInput=Y,t.TriggerInput=Z,t.WidgetDirective=G,t.attachDirective=J,t.beginTimeMeasurement=function(){let t=arguments.length>0&&void 0!==arguments[0]?arguments[0]:"measurement";c("beginTimeMeasurement",arguments,[],["string"]),function(t){window.performance.clearMarks("ot.".concat(t,".begin")),window.performance.clearMarks("ot.".concat(t)),window.performance.clearMeasures("ot.".concat(t,".measure"))}(t),function(t){window.performance.mark("ot.".concat(t,".begin"))}(t)},t.cancelTimer=W,t.cancelTimers=function(t){c("cancelTimers",arguments,[],["string"],["array"]),void 0===t&&(t=Array.from(Object.keys(window.ot_timers))),e(t)||(t=[t]);for(let e of t)W(e)},t.commitInput=function(t){c("commitInput",arguments,["string"]);let e=document.querySelectorAll("[input=".concat(t,"]")),i=document.querySelectorAll("[name=".concat(t,"]"));if(e.length)e.forEach(F);else{if(!i.length)throw Error("No inputs found: ".concat(t));i.forEach(F)}},t.completePage=function(){g()},t.delay=async function(t){return p(),new Promise(((e,i)=>{window.setTimeout((()=>e()),t)}))},t.delayEvent=function(t,e,i){c("delayEvent",arguments,["number","string"],["number","string","object"]),setTimeout((()=>document.body.dispatchEvent(new CustomEvent("ot.".concat(e),{detail:i}))),t)},t.disableElem=S,t.disableInput=function(t){c("disableInput",arguments,["string"]),L(k(E,t),S)},t.disableInputs=function(t){c("disableInputs",arguments,["string"],["array"],[]),L(void 0===t?T():k(A,t),S)},t.emitEvent=function(t,e){c("emitEvent",arguments,["string"],["string","object"]),setTimeout((()=>document.body.dispatchEvent(new CustomEvent("ot.".concat(t),{detail:e}))))},t.enableElem=D,t.enableInput=function(t){c("enableInput",arguments,["string"]);let e=k(E,t);L(e,D),O(e)},t.enableInputs=function(t){c("enableInputs",arguments,["string"],["array"],[]);let e=void 0===t?T():k(A,t);L(e,D),O(e)},t.getTimeMeasurement=function(){let t=arguments.length>0&&void 0!==arguments[0]?arguments[0]:"measurement";return c("getTimeMeasurement",arguments,[],["string"]),function(t){window.performance.mark("ot.".concat(t))}(t),Math.round(function(t){return window.performance.measure("ot.".concat(t,".measure"),"ot.".concat(t,".begin"),"ot.".concat(t))}(t).duration)},t.hideDisplay=function(t){c("hideDisplay",arguments,["string"]),L(k(y,t),M)},t.hideDisplays=function(t){c("hideDisplays",arguments,["string"],["array"]),L(k(x,t),M)},t.hideElem=M,t.initTimers=H,t.isArray=e,t.isElemCheckable=C,t.isElemEditable=P,t.isElemField=I,t.isElemNavigable=function(t){return-1!=t.tabIndex},t.isFunction=i,t.isObject=r,t.isPlainObject=o,t.isScalar=s,t.isVoid=n,t.onEvent=function(t,e,i){c("onEvent",arguments,["string","function"],["string","string","function"],["string","function","function"]),2==arguments.length?(i=arguments[1],e=null):"string"==typeof arguments[1]&&(e=t=>t.detail&&t.detail.name==arguments[1]),document.body.addEventListener("ot.".concat(t),(async n=>{e&&!e(n)||(await i.call(null,n),"update"!==t&&p())}))},t.otCheckInput=pt,t.otClass=ct,t.otClick=ft,t.otHTML=$,t.otHeight=rt,t.otHref=ot,t.otInput=lt,t.otKey=vt,t.otMax=it,t.otMin=et,t.otPoint=gt,t.otRadioInput=dt,t.otRangeInput=ht,t.otSrc=at,t.otStep=nt,t.otText=Q,t.otTextInput=mt,t.otValue=ut,t.otWidth=st,t.preloadImage=R,t.preloadImages=function(t){return c("preloadImage",arguments,["array"]),Promise.all(t.map((t=>R(t))))},t.resetInput=function(t){c("resetInput",arguments,["string"]),B(k(w,t),K)},t.resetInputs=function(t){c("resetInputs",arguments,[],["array"]),B(void 0===t?T():k(w,t),K)},t.showDisplay=function(t){c("showDisplay",arguments,["string"]);let e=k(y,t);L(e,j),O(e)},t.showDisplays=function(t){c("showDisplays",arguments,["string"],["array"]);let e=k(x,t);L(e,j),O(e)},t.showElem=j,t.startTimer=function(t,e){c("startTimer",arguments,["string","number"]),W(t),new N(t,e).start()},t.startTimerPeriodic=function(t,e,i){c("startTimerPeriodic",arguments,["string","number","number"],["string","number"]),W(t),new V(t,e,i).start()},t.startTimerSequence=function(t,e){c("startTimerSequence",arguments,["string","array"]),W(t),new q(t,e).start()},t.submitPage=function(){document.getElementById("form").requestSubmit()},t.triggerEvent=f,t.updatePage=p,t}({});Object.freeze(ot);
