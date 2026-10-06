// Loads a built .riv in the stock Rive runtime (the WASM build of the C++ core
// the mobile runtimes share, with no renderer) and drives isPrinting from host
// code the way the app will. Exits non-zero if the file stops behaving.
//
//   npm install && node check.mjs [../../dist/pos_printing.riv]
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

// The WASM build probes for a canvas at startup; nothing here draws.
globalThis.document = { createElement: () => ({ getContext: () => null, style: {} }) };
globalThis.window = globalThis;
const { default: RiveFactory } = await import('@rive-app/canvas-advanced');

const here = path.dirname(fileURLToPath(import.meta.url));
const pkg = path.join(here, 'node_modules', '@rive-app', 'canvas-advanced');
const rivPath = path.resolve(process.argv[2] ?? path.join(here, '..', '..', 'dist', 'pos_printing.riv'));

const rive = await RiveFactory({ wasmBinary: fs.readFileSync(path.join(pkg, 'rive.wasm')) });
const file = await rive.load(new Uint8Array(fs.readFileSync(rivPath)),
    new rive.CustomFileAssetLoader({ loadContents: () => true }), false);

const artboard = file.defaultArtboard();
assert.equal(artboard.name, 'PosPrinting');
const vm = file.defaultArtboardViewModel(artboard);
assert.equal(vm.name, 'PosPrinting');
const vmi = vm.defaultInstance();
const isPrinting = vmi.boolean('isPrinting');
assert.equal(isPrinting.value, true, 'isPrinting should default to true');

const sm = new rive.StateMachineInstance(artboard.stateMachineByName('printing'), artboard);
sm.bindViewModelInstance(vmi);
const feed = artboard.node('paper_feed');

let frame = 0;
let state = null;
const advance = (frames) => {
    for (let i = 0; i < frames; i++) {
        sm.advanceAndApply(1 / 60);
        frame++;
        for (let k = 0; k < sm.stateChangedCount(); k++) {
            state = sm.stateChangedNameByIndex(k);
            console.log(`  f${frame}: ${state}`);
        }
    }
};
const paperOut = () => Math.abs(feed.x) < 0.01 && Math.abs(feed.y) < 0.01;
const paperHidden = () => Math.abs(feed.x - 49.14) < 0.01 && Math.abs(feed.y - 96.173) < 0.01;

advance(24);
assert.equal(state, 'intro');
assert.ok(paperHidden(), 'paper starts inside the slot');

advance(56); // f80, part-way through the first loop cycle
assert.equal(state, 'printing_loop');
assert.ok(!paperHidden() && !paperOut(), 'paper is mid-feed');

isPrinting.value = false;
console.log(`host: isPrinting = false at f${frame}`);
advance(40);
assert.equal(state, 'printing_loop', 'the current cycle finishes before done');
advance(60);
assert.equal(state, 'done');
advance(80);
assert.ok(paperOut(), 'done holds the receipt in the Figma pose');
advance(300);
assert.ok(paperOut(), 'and keeps holding it');

isPrinting.value = true;
console.log(`host: isPrinting = true at f${frame}`);
advance(30);
assert.equal(state, 'printing_loop', 'printing again restarts intro, then the loop');

console.log(`ok: ${path.relative(process.cwd(), rivPath)}`);
