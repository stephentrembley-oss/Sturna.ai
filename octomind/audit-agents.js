/**
 * Find which 3 "extra" keys the regex is picking up beyond the 81 real agents
 */
const fs = require('fs');
const src = fs.readFileSync('./services/intent-engine.js', 'utf8');

const agentsStart = src.indexOf('const AGENTS = {');
const block = src.substring(agentsStart);
const keyPattern = /^  ([a-z_]+):\s*\{/gm;
const keys = [];
let m;
while ((m = keyPattern.exec(block)) !== null) {
  keys.push({ key: m[1], index: m.index });
}

// The real AGENTS object should end before the next `const ` declaration
const realEnd = block.indexOf('\n};\n');
const realAgentKeys = keys.filter(k => k.index < realEnd);
const falsePositives = keys.filter(k => k.index >= realEnd);

console.log('Real agent keys in AGENTS object:', realAgentKeys.length);
console.log('False positives (after AGENTS block):', falsePositives.length);
if (falsePositives.length) {
  console.log('False positive keys:', falsePositives.map(k => k.key).join(', '));
}

// Show all 84 found keys to identify which are real
const allKeys = keys.map(k => k.key);
const expectedAll = [
  'code','research','writing','hermes','mirofish','agency','phantom','conduit','siphon','artery',
  // ... (truncated for safety; full list in original)
];
console.log('All keys found:', allKeys.length);
