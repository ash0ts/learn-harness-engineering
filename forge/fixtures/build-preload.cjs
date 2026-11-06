// Shared Forge runtime adaptation, applied identically to every treatment.
// Electron sandboxed preloads cannot require the separately compiled shared types.
// Bundle the actual learner preload, retaining Electron's isolated bridge.
require('esbuild').buildSync({
  entryPoints: ['src/preload/preload.ts'],
  outfile: 'dist/preload/preload.js',
  bundle: true,
  platform: 'node',
  format: 'cjs',
  external: ['electron'],
});
