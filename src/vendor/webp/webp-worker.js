// Runs the libwebp WebAssembly encoder off the main thread. Loaded as a module worker by engine.js.
const DEFAULTS = { quality: 75, target_size: 0, target_PSNR: 0, method: 4, sns_strength: 50, filter_strength: 60, filter_sharpness: 0, filter_type: 1,
  partitions: 0, segments: 4, pass: 1, show_compressed: 0, preprocessing: 0, autofilter: 0, partition_limit: 0, alpha_compression: 1, alpha_filtering: 1,
  alpha_quality: 100, lossless: 0, exact: 0, image_hint: 0, emulate_jpeg_size: 0, thread_level: 0, low_memory: 0, near_lossless: 100, use_delta_palette: 0, use_sharp_yuv: 0 };
let mod = null;
async function init() {
  if (mod) return mod;
  // feature-detect WebAssembly SIMD (same probe module used by wasm-feature-detect)
  const simd = WebAssembly.validate(new Uint8Array([0, 97, 115, 109, 1, 0, 0, 0, 1, 5, 1, 96, 0, 1, 123, 3, 2, 1, 0, 10, 10, 1, 8, 0, 65, 0, 253, 15, 253, 98, 11]));
  const m = await import(simd ? './webp_enc_simd.js' : './webp_enc.js');
  mod = await m.default({ noInitialRun: true });
  return mod;
}
self.onmessage = async (e) => {
  const { id, buf, width, height, options } = e.data;
  try {
    const m = await init();
    const out = m.encode(new Uint8Array(buf), width, height, Object.assign({}, DEFAULTS, options));
    if (!out) throw new Error('WebP encoding failed');
    const copy = out.slice();
    self.postMessage({ id, ok: true, buf: copy.buffer }, [copy.buffer]);
  } catch (err) {
    self.postMessage({ id, ok: false, error: String((err && err.message) || err) });
  }
};
