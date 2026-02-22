module.exports = (function() {
var __MODS__ = {};
var __DEFINE__ = function(modId, func, req) { var m = { exports: {}, _tempexports: {} }; __MODS__[modId] = { status: 0, func: func, req: req, m: m }; };
var __REQUIRE__ = function(modId, source) { if(!__MODS__[modId]) return require(source); if(!__MODS__[modId].status) { var m = __MODS__[modId].m; m._exports = m._tempexports; var desp = Object.getOwnPropertyDescriptor(m, "exports"); if (desp && desp.configurable) Object.defineProperty(m, "exports", { set: function (val) { if(typeof val === "object" && val !== m._exports) { m._exports.__proto__ = val.__proto__; Object.keys(val).forEach(function (k) { m._exports[k] = val[k]; }); } m._tempexports = val }, get: function () { return m._tempexports; } }); __MODS__[modId].status = 1; __MODS__[modId].func(__MODS__[modId].req, m, m.exports); } return __MODS__[modId].m.exports; };
var __REQUIRE_WILDCARD__ = function(obj) { if(obj && obj.__esModule) { return obj; } else { var newObj = {}; if(obj != null) { for(var k in obj) { if (Object.prototype.hasOwnProperty.call(obj, k)) newObj[k] = obj[k]; } } newObj.default = obj; return newObj; } };
var __REQUIRE_DEFAULT__ = function(obj) { return obj && obj.__esModule ? obj.default : obj; };
__DEFINE__(1770924812546, function(require, module, exports) {

const mimicFn = require('mimic-fn');

module.exports = (fn, opts) => {
	// TODO: Remove this in v3
	if (opts === true) {
		throw new TypeError('The second argument is now an options object');
	}

	if (typeof fn !== 'function') {
		throw new TypeError('Expected a function');
	}

	opts = opts || {};

	let ret;
	let called = false;
	const fnName = fn.displayName || fn.name || '<anonymous>';

	const onetime = function () {
		if (called) {
			if (opts.throw === true) {
				throw new Error(`Function \`${fnName}\` can only be called once`);
			}

			return ret;
		}

		called = true;
		ret = fn.apply(this, arguments);
		fn = null;

		return ret;
	};

	mimicFn(onetime, fn);

	return onetime;
};

}, function(modId) {var map = {}; return __REQUIRE__(map[modId], modId); })
return __REQUIRE__(1770924812546);
})()
//miniprogram-npm-outsideDeps=["mimic-fn"]
//# sourceMappingURL=index.js.map