const fs = require('fs');
const src = fs.readFileSync('./services/intent-engine.js', 'utf8');

const start = src.indexOf('const AGENTS = {');
const block = src.substring(start);
const keyPattern = /^  ([a-z_]+):\s*\{/gm;
let keys = [];
let m;
while ((m = keyPattern.exec(block)) !== null) {
  keys.push(m[1]);
}
console.log('Agent keys in AGENTS object:', keys.length);
console.log(keys.join(', '));
