const fs = require('fs');
const file = 'node_modules/js-interpreter/lib/js-interpreter.js';
if (fs.existsSync(file)) {
  let data = fs.readFileSync(file, 'utf8');
  data = data.replace(/module\.exports = require\("vm"\);/g, 'module.exports = null;');
  data = data.replace(/Interpreter\.vm = __webpack_require__\(\/\*! vm \*\/ "vm"\);/g, 'Interpreter.vm = null;');
  fs.writeFileSync(file, data);
}
