"use strict";

// Deterministic fixed-marginal switch-chain required by EXP-001.
const fs = require("fs");

function xoshiro(seed) {
  let a = (seed ^ 0x9e3779b9) >>> 0, b = (seed + 0x6a09e667) >>> 0;
  let c = (seed ^ 0xbb67ae85) >>> 0, d = (seed + 0x3c6ef372) >>> 0;
  return function () {
    const result = Math.imul(((Math.imul(b, 5) << 7) | (Math.imul(b, 5) >>> 25)) >>> 0, 9) >>> 0;
    const t = (b << 9) >>> 0;
    c ^= a; d ^= b; b ^= c; a ^= d; c ^= t; d = ((d << 11) | (d >>> 21)) >>> 0;
    return result;
  };
}

function parseArgs() {
  const args = {};
  for (let i = 2; i < process.argv.length; i += 2) args[process.argv[i].replace(/^--/, "")] = process.argv[i + 1];
  return args;
}

const args = parseArgs();
const scope = args.scope;
const width = scope === "MAIN" ? 6 : 7;
const p0 = scope === "MAIN" ? 1 / 66 : 7 / 330;
const samples = Number(args.samples || 10000);
const seed = Number(args.seed) >>> 0;
const rows = fs.readFileSync(args.input, "utf8").trim().split(/\r?\n/).slice(1).map(line => line.split(","));
const n = rows.length;
const members = new Uint8Array(n * width);
const matrix = new Uint8Array(n * 45);
const counts = new Int32Array(45 * 45);
for (let r = 0; r < n; r++) {
  const nums = rows[r].slice(2, 2 + width).map(Number).map(x => x - 1);
  for (let i = 0; i < width; i++) { members[r * width + i] = nums[i]; matrix[r * 45 + nums[i]] = 1; }
  for (let i = 0; i < width; i++) for (let j = i + 1; j < width; j++) {
    const x = Math.min(nums[i], nums[j]), y = Math.max(nums[i], nums[j]); counts[x * 45 + y]++;
  }
}
const rng = xoshiro(seed);
const burnin = 10 * n * 45;
const interval = n * 45;
let accepted = 0;
const maxima = new Array(samples);
const expected = n * p0;
const denominator = Math.sqrt(n * p0 * (1 - p0));

function oneSwitch() {
  let r1, r2, base1, base2, slot1, a, attempts;
  while (true) {
    r1 = rng() % n; r2 = rng() % n;
    if (r2 === r1) continue;
    base1 = r1 * width; base2 = r2 * width; attempts = 0;
    do { slot1 = rng() % width; a = members[base1 + slot1]; attempts++; } while (matrix[r2 * 45 + a] && attempts < width * 3);
    if (!matrix[r2 * 45 + a]) break;
  }
  let slot2 = rng() % width, b = members[base2 + slot2];
  while (matrix[r1 * 45 + b]) { slot2 = rng() % width; b = members[base2 + slot2]; }
  for (let i = 0; i < width; i++) {
    const c1 = members[base1 + i];
    if (c1 !== a) {
      let x = Math.min(a, c1), y = Math.max(a, c1); counts[x * 45 + y]--;
      x = Math.min(b, c1); y = Math.max(b, c1); counts[x * 45 + y]++;
    }
    const c2 = members[base2 + i];
    if (c2 !== b) {
      let x = Math.min(b, c2), y = Math.max(b, c2); counts[x * 45 + y]--;
      x = Math.min(a, c2); y = Math.max(a, c2); counts[x * 45 + y]++;
    }
  }
  matrix[r1 * 45 + a] = 0; matrix[r1 * 45 + b] = 1;
  matrix[r2 * 45 + b] = 0; matrix[r2 * 45 + a] = 1;
  members[base1 + slot1] = b; members[base2 + slot2] = a;
  accepted++;
}

while (accepted < burnin) oneSwitch();
for (let sample = 0; sample < samples; sample++) {
  const target = burnin + (sample + 1) * interval;
  while (accepted < target) oneSwitch();
  let maximum = 0;
  for (let a = 0; a < 44; a++) for (let b = a + 1; b < 45; b++) {
    const value = Math.abs((counts[a * 45 + b] - expected) / denominator);
    if (value > maximum) maximum = value;
  }
  maxima[sample] = maximum;
}
fs.writeFileSync(args.output, JSON.stringify({version:"EXP001-FIXED-MARGINAL-1.0",prng:"XOSHIRO128STARSTAR-UINT32",scope,n,width,seed,burnin_accepted:burnin,interval_accepted:interval,samples,accepted_switches:accepted,maxima}) + "\n");
