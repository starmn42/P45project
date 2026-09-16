import fs from "node:fs/promises";

const endpoint = process.argv[2];
const outDir = process.argv[3];
const targets = JSON.parse(process.argv[4]);
const pages = await (await fetch(`${endpoint}/json`)).json();
const page = pages.find((item) => item.type === "page");
if (!page) throw new Error("No debuggable page");
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((resolve, reject) => { ws.onopen = resolve; ws.onerror = reject; });
let nextId = 0;
const pending = new Map();
const consoleErrors = [];
ws.onmessage = ({data}) => {
  const message = JSON.parse(data);
  if (message.id && pending.has(message.id)) {
    const {resolve, reject} = pending.get(message.id); pending.delete(message.id);
    message.error ? reject(new Error(JSON.stringify(message.error))) : resolve(message.result);
  } else if (message.method === "Runtime.exceptionThrown") {
    consoleErrors.push(message.params.exceptionDetails?.text || "exception");
  } else if (message.method === "Runtime.consoleAPICalled" && message.params.type === "error") {
    consoleErrors.push("console.error");
  }
};
const send = (method, params={}) => new Promise((resolve, reject) => {
  const id = ++nextId; pending.set(id, {resolve, reject}); ws.send(JSON.stringify({id, method, params}));
});
await send("Runtime.enable");
await send("Page.enable");
const results = [];
for (const target of targets) {
  await send("Emulation.setDeviceMetricsOverride", {width: target.width, height: target.height, deviceScaleFactor: 1, mobile: target.mobile});
  await send("Page.navigate", {url: "http://127.0.0.1:8045/"});
  await new Promise((resolve) => setTimeout(resolve, 1800));
  const metrics = await send("Runtime.evaluate", {expression: `({clientWidth:document.documentElement.clientWidth,scrollWidth:document.documentElement.scrollWidth,scrollHeight:document.documentElement.scrollHeight,bodyWidth:document.body.getBoundingClientRect().width,buttons:[...document.querySelectorAll('.home-actions button')].map(x=>({text:x.textContent.trim(),left:x.getBoundingClientRect().left,right:x.getBoundingClientRect().right,width:x.getBoundingClientRect().width})),textOverflow:[...document.querySelectorAll('#status *')].filter(x=>x.scrollWidth>x.clientWidth+1).slice(0,20).map(x=>({tag:x.tagName,cls:x.className,txt:(x.textContent||'').trim().slice(0,60),cw:x.clientWidth,sw:x.scrollWidth}))})`, returnByValue: true});
  const shot = await send("Page.captureScreenshot", {format:"png", captureBeyondViewport:true, fromSurface:true});
  await fs.writeFile(`${outDir}/${target.name}`, Buffer.from(shot.data, "base64"));
  results.push({...target, ...metrics.result.value, horizontalOverflow: metrics.result.value.scrollWidth - metrics.result.value.clientWidth});
}
ws.close();
await fs.writeFile(`${outDir}/responsive_metrics.json`, JSON.stringify({results, consoleErrors}, null, 2));
console.log(JSON.stringify({results, consoleErrors}, null, 2));
