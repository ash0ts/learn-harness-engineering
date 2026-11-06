<script setup>
import { computed } from 'vue'
import catalog from '../../../public/forge/evidence/catalog.json'
const props = defineProps({ kind: { type: String, required: true } })
const urls = import.meta.glob('../../../en/forge/assets/captures/*', { eager: true, query: '?url', import: 'default' })
const captures = computed(() => catalog.assets.filter(a => a.kind === props.kind))
const imageUrl = file => urls['../../../en/forge/assets/' + file]
const title = item => item.file.split('/').pop().replace(/\.(jpg|png)$/,'').replace(/^supplemental-/,'').replaceAll('-',' ')
</script>
<template>
  <div class="capture-gallery">
    <figure v-for="capture in captures" :key="capture.file">
      <a :href="imageUrl(capture.file)" target="_blank" rel="noopener"><img :src="imageUrl(capture.file)" loading="lazy" :alt="'Original capture: '+title(capture)+'. Open for full size.'" /></a>
      <figcaption><strong>{{ title(capture) }}</strong><br /><a :href="capture.sourceUrl">Open the source in Forge / W&amp;B ↗</a><details><summary>Capture provenance</summary><p>{{ capture.snapshotNote || 'Original unmodified capture from the saved course evidence.' }}</p><p>Artifact path: <code>{{ capture.originalArtifactPath }}</code></p><p>SHA-256: <code>{{ capture.sha256 }}</code></p></details></figcaption>
    </figure>
  </div>
</template>
<style scoped>
.capture-gallery{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px 18px;margin:24px 0}.capture-gallery figure{margin:0;min-width:0}.capture-gallery img{border-radius:5px;border:1px solid var(--vp-c-divider)}.capture-gallery figcaption{font-size:13px;line-height:1.6;margin-top:8px;overflow-wrap:anywhere}.capture-gallery strong{font-weight:600}.capture-gallery summary{cursor:pointer;margin-top:8px}.capture-gallery code{overflow-wrap:anywhere;font-size:11px}.capture-gallery a:focus-visible,.capture-gallery summary:focus-visible{outline:3px solid var(--vp-c-brand-1);outline-offset:3px}@media(max-width:640px){.capture-gallery{grid-template-columns:1fr}}
</style>
