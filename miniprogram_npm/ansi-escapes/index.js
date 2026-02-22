module.exports = (function() {
var __MODS__ = {};
var __DEFINE__ = function(modId, func, req) { var m = { exports: {}, _tempexports: {} }; __MODS__[modId] = { status: 0, func: func, req: req, m: m }; };
var __REQUIRE__ = function(modId, source) { if(!__MODS__[modId]) return require(source); if(!__MODS__[modId].status) { var m = __MODS__[modId].m; m._exports = m._tempexports; var desp = Object.getOwnPropertyDescriptor(m, "exports"); if (desp && desp.configurable) Object.defineProperty(m, "exports", { set: function (val) { if(typeof val === "object" && val !== m._exports) { m._exports.__proto__ = val.__proto__; Object.keys(val).forEach(function (k) { m._exports[k] = val[k]; }); } m._tempexports = val }, get: function () { return m._tempexports; } }); __MODS__[modId].status = 1; __MODS__[modId].func(__MODS__[modId].req, m, m.exports); } return __MODS__[modId].m.exports; };
var __REQUIRE_WILDCARD__ = function(obj) { if(obj && obj.__esModule) { return obj; } else { var newObj = {}; if(obj != null) { for(var k in obj) { if (Object.prototype.hasOwnProperty.call(obj, k)) newObj[k] = obj[k]; } } newObj.default = obj; return newObj; } };
var __REQUIRE_DEFAULT__ = function(obj) { return obj && obj.__esModule ? obj.default : obj; };
__DEFINE__(1770924812099, function(require, module, exports) {

var ESC = '\u001b[';
var x = module.exports;

x.cursorTo = function (x, y) {
	if (arguments.length === 0) {
		return ESC + 'H';
	}

	if (arguments.length === 1) {
		return ESC + (x + 1) + 'G';
	}

	return ESC + (y + 1) + ';' + (x + 1) + 'H';
};

x.cursorMove = function (x, y) {
	var ret = '';

	if (x < 0) {
		ret += ESC + (-x) + 'D';
	} else if (x > 0) {
		ret += ESC + x + 'C';
	}

	if (y < 0) {
		ret += ESC + (-y) + 'A';
	} else if (y > 0) {
		ret += ESC + y + 'B';
	}

	return ret;
};

x.cursorUp = function (count) {
	return ESC + (typeof count === 'number' ? count : 1) + 'A';
};

x.cursorDown = function (count) {
	return ESC + (typeof count === 'number' ? count : 1) + 'B';
};

x.cursorForward = function (count) {
	return ESC + (typeof count === 'number' ? count : 1) + 'C';
};

x.cursorBackward = function (count) {
	return ESC + (typeof count === 'number' ? count : 1) + 'D';
};

x.cursorLeft = ESC + '1000D';
x.cursorSavePosition = ESC + 's';
x.cursorRestorePosition = ESC + 'u';
x.cursorGetPosition = ESC + '6n';
x.cursorNextLine = ESC + 'E';
x.cursorPrevLine = ESC + 'F';
x.cursorHide = ESC + '?25l';
x.cursorShow = ESC + '?25h';

x.eraseLines = function (count) {
	var clear = '';

	for (var i = 0; i < count; i++) {
		clear += x.cursorLeft + x.eraseEndLine + (i < count - 1 ? x.cursorUp() : '');
	}

	return clear;
};

x.eraseEndLine = ESC + 'K';
x.eraseStartLine = ESC + '1K';
x.eraseLine = ESC + '2K';
x.eraseDown = ESC + 'J';
x.eraseUp = ESC + '1J';
x.eraseScreen = ESC + '2J';
x.scrollUp = ESC + 'S';
x.scrollDown = ESC + 'T';

x.clearScreen = '\u001bc';
x.beep = '\u0007';

x.image = function (buf, opts) {
	opts = opts || {};

	var ret = '\u001b]1337;File=inline=1';

	if (opts.width) {
		ret += ';width=' + opts.width;
	}

	if (opts.height) {
		ret += ';height=' + opts.height;
	}

	if (opts.preserveAspectRatio === false) {
		ret += ';preserveAspectRatio=0';
	}

	return ret + ':' + buf.toString('base64') + '\u0007';
};

x.iTerm = {};

x.iTerm.setCwd = function (cwd) {
	return '\u001b]50;CurrentDir=' + (cwd || process.cwd()) + '\u0007';
};

}, function(modId) {var map = {}; return __REQUIRE__(map[modId], modId); })
return __REQUIRE__(1770924812099);
})()
//miniprogram-npm-outsideDeps=[]
//# sourceMappingURL=index.js.map