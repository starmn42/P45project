"use strict";

const fs = require("fs");
const os = require("os");
const { Worker, isMainThread, parentPort, workerData } = require("worker_threads");

const WINDOW_BITS = 4500;
const HISTORY_BITS = 1238 * 45;
const WINDOW_COUNT = 1139;

function workspace() {
  const capacity = 2 * WINDOW_BITS + 1;
  return {
    next0: new Int32Array(capacity),
    next1: new Int32Array(capacity),
    link: new Int32Array(capacity),
    length: new Int32Array(capacity),
  };
}

function lz76CountSam(data, offset, n, work) {
  const { next0, next1, link, length } = work;
  next0.fill(-1);
  next1.fill(-1);
  link.fill(-1);
  length.fill(0);
  let size = 1;
  let last = 0;

  function extend(ch) {
    const cur = size++;
    length[cur] = length[last] + 1;
    let p = last;
    const transitions = ch ? next1 : next0;
    while (p >= 0 && transitions[p] < 0) {
      transitions[p] = cur;
      p = link[p];
    }
    if (p < 0) {
      link[cur] = 0;
    } else {
      const q = transitions[p];
      if (length[p] + 1 === length[q]) {
        link[cur] = q;
      } else {
        const clone = size++;
        length[clone] = length[p] + 1;
        link[clone] = link[q];
        next0[clone] = next0[q];
        next1[clone] = next1[q];
        while (p >= 0 && transitions[p] === q) {
          transitions[p] = clone;
          p = link[p];
        }
        link[q] = clone;
        link[cur] = clone;
      }
    }
    last = cur;
  }

  let pos = 0;
  let count = 0;
  while (pos < n) {
    let state = 0;
    let end = pos;
    while (end < n) {
      const bit = data[offset + end];
      const next = bit ? next1[state] : next0[state];
      if (next < 0) break;
      state = next;
      end++;
    }
    const phraseLength = end < n ? end - pos + 1 : n - pos;
    count++;
    for (let idx = pos; idx < pos + phraseLength; idx++) {
      extend(data[offset + idx]);
    }
    pos += phraseLength;
  }
  return count;
}

function lz76Count(data, offset, n) {
  let pos = 0;
  let count = 0;
  while (pos < n) {
    let phraseLength = 1;
    while (pos + phraseLength <= n) {
      const prefix = data.subarray(offset, offset + pos);
      const candidate = data.subarray(offset + pos, offset + pos + phraseLength);
      if (prefix.indexOf(candidate) < 0) break;
      phraseLength++;
    }
    count++;
    pos += Math.min(phraseLength, n - pos);
  }
  return count;
}

function correlationFromStates(states) {
  const n = states.length - 1;
  let sx = 0;
  let sy = 0;
  let sxy = 0;
  for (let i = 0; i < n; i++) {
    const x = states[i];
    const y = states[i + 1];
    sx += x;
    sy += y;
    sxy += x * y;
  }
  const vx = n * sx - sx * sx;
  const vy = n * sy - sy * sy;
  if (vx === 0 || vy === 0) return null;
  return (n * sxy - sx * sy) / Math.sqrt(vx * vy);
}

function workerThreshold() {
  const { input, start, end } = workerData;
  const fd = fs.openSync(input, "r");
  const buffer = Buffer.allocUnsafe(WINDOW_BITS);
  const counts = new Int16Array(end - start);
  const work = workspace();
  for (let row = start; row < end; row++) {
    fs.readSync(fd, buffer, 0, WINDOW_BITS, row * WINDOW_BITS);
    counts[row - start] = lz76Count(buffer, 0, WINDOW_BITS, work);
  }
  fs.closeSync(fd);
  parentPort.postMessage({ start, counts }, [counts.buffer]);
}

function workerHistories() {
  const { input, start, end, qCount } = workerData;
  const fd = fs.openSync(input, "r");
  const buffer = Buffer.allocUnsafe(HISTORY_BITS);
  const occupancy = new Float64Array(end - start);
  const autocorr = new Float64Array(end - start);
  const stateCounts = new Int32Array(end - start);
  const estimable = new Uint8Array(end - start);
  const states = new Uint8Array(WINDOW_COUNT);
  const work = workspace();
  for (let row = start; row < end; row++) {
    fs.readSync(fd, buffer, 0, HISTORY_BITS, row * HISTORY_BITS);
    let countA = 0;
    for (let w = 0; w < WINDOW_COUNT; w++) {
      const c = lz76Count(buffer, w * 45, WINDOW_BITS, work);
      const state = c <= qCount ? 1 : 0;
      states[w] = state;
      countA += state;
    }
    const corr = correlationFromStates(states);
    const idx = row - start;
    stateCounts[idx] = countA;
    occupancy[idx] = countA / WINDOW_COUNT;
    if (corr !== null && Number.isFinite(corr)) {
      autocorr[idx] = corr;
      estimable[idx] = 1;
    }
  }
  fs.closeSync(fd);
  parentPort.postMessage(
    { start, occupancy, autocorr, stateCounts, estimable },
    [occupancy.buffer, autocorr.buffer, stateCounts.buffer, estimable.buffer]
  );
}

if (!isMainThread) {
  if (workerData.mode === "threshold") workerThreshold();
  else workerHistories();
} else {
  const args = Object.fromEntries(process.argv.slice(2).map((item) => item.split("=", 2)));
  const mode = args.mode;
  const input = args.input;
  const output = args.output;
  const rows = Number(args.rows);
  const qCount = args.qCount === undefined ? null : Number(args.qCount);
  const workers = Number(args.workers || Math.min(16, os.cpus().length));
  if (!mode || !input || !output || !rows) throw new Error("missing arguments");
  const size = fs.statSync(input).size;
  const expected = rows * (mode === "threshold" ? WINDOW_BITS : HISTORY_BITS);
  if (size !== expected) throw new Error(`binary input size mismatch ${size} != ${expected}`);

  const tasks = [];
  const block = Math.ceil(rows / workers);
  for (let start = 0; start < rows; start += block) {
    const end = Math.min(rows, start + block);
    tasks.push(new Promise((resolve, reject) => {
      const worker = new Worker(__filename, { workerData: { mode, input, start, end, qCount } });
      worker.on("message", resolve);
      worker.on("error", reject);
      worker.on("exit", (code) => { if (code !== 0) reject(new Error(`worker exit ${code}`)); });
    }));
  }
  Promise.all(tasks).then((parts) => {
    parts.sort((a, b) => a.start - b.start);
    let result;
    if (mode === "threshold") {
      const counts = [];
      for (const part of parts) counts.push(...new Int16Array(part.counts));
      result = { mode, rows, counts };
    } else {
      const occupancy = [];
      const autocorr = [];
      const stateCounts = [];
      const estimable = [];
      for (const part of parts) {
        occupancy.push(...new Float64Array(part.occupancy));
        autocorr.push(...new Float64Array(part.autocorr));
        stateCounts.push(...new Int32Array(part.stateCounts));
        estimable.push(...new Uint8Array(part.estimable));
      }
      result = { mode, rows, qCount, occupancy, autocorr, stateCounts, estimable };
    }
    fs.writeFileSync(output, JSON.stringify(result));
  }).catch((error) => {
    console.error(error.stack || error);
    process.exitCode = 1;
  });
}
