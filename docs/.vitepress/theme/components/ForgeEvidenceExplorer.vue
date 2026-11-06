<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { withBase } from 'vitepress'
import catalog from '../../../public/forge/evidence/catalog.json'

const assets = import.meta.glob('../../../en/forge/assets/captures/*', { eager: true, query: '?url', import: 'default' })
const project = ref('all'), scope = ref('primary'), outcome = ref('all'), query = ref('')
const selected = ref(''), page = ref(0), notice = ref('')
const pageSize = 12
const projects = [...new Set(catalog.trials.map(t => t.project))].sort()
const outcomes = [...new Set(catalog.trials.map(t => t.outcome))].sort()
const filtered = computed(() => catalog.trials.filter(t =>
  (project.value === 'all' || t.project === project.value) &&
  (scope.value === 'all' || (scope.value === 'primary' ? t.primary : !t.primary)) &&
  (outcome.value === 'all' || t.outcome === outcome.value) &&
  (!query.value || [t.id, t.variant, t.sourceCommit, ...t.checks.map(c => c.error || '')].join(' ').toLowerCase().includes(query.value.toLowerCase()))))
const visible = computed(() => filtered.value.slice(page.value * pageSize, (page.value + 1) * pageSize))
const pages = computed(() => Math.max(1, Math.ceil(filtered.value.length / pageSize)))
const passed = computed(() => filtered.value.filter(t => t.outcome === 'passed').length)
const label = value => value.replaceAll('_', ' ')
const safeUrl = value => {
  try { const u = new URL(value); return u.protocol === 'https:' && ['forge.coreweave.com','wandb.ai','github.com'].includes(u.hostname) ? u.href : undefined }
  catch { return undefined }
}
const imageUrl = file => assets['../../../en/forge/assets/' + file]
const sourceUrl = trial => `https://github.com/ash0ts/learn-harness-engineering/tree/${trial.sourceCommit}`
function updateUrl() {
  const url = new URL(window.location.href)
  for (const [key,value] of Object.entries({ project: project.value, scope: scope.value, outcome: outcome.value, q: query.value, trial: selected.value, page: page.value ? String(page.value + 1) : '' })) {
    value ? url.searchParams.set(key,value) : url.searchParams.delete(key)
  }
  url.hash = 'inspect-every-attempt'
  window.history.pushState(null,'',url)
}
function changeFilter() { page.value = 0; selected.value = ''; notice.value = ''; updateUrl() }
function reset() { project.value = 'all'; scope.value = 'primary'; outcome.value = 'all'; query.value = ''; changeFilter() }
function toggle(id) { selected.value = selected.value === id ? '' : id; updateUrl() }
function changePage(amount) { page.value += amount; selected.value = ''; updateUrl() }
function readUrl() {
  const params = new URL(window.location.href).searchParams
  project.value = projects.includes(params.get('project')) ? params.get('project') : 'all'
  scope.value = ['primary','other','all'].includes(params.get('scope')) ? params.get('scope') : 'primary'
  outcome.value = outcomes.includes(params.get('outcome')) ? params.get('outcome') : 'all'
  query.value = params.get('q') || ''
  selected.value = params.get('trial') || ''
  const index = filtered.value.findIndex(t => t.id === selected.value)
  const requestedPage = Math.floor(Number(params.get('page') || 1)) - 1
  page.value = index >= 0 ? Math.floor(index / pageSize) : Math.max(0, Math.min(pages.value - 1, Number.isFinite(requestedPage) ? requestedPage : 0))
  notice.value = selected.value && index < 0 ? 'The requested trial is not in these filters. Select all recorded attempts or reset the filters.' : ''
}
onMounted(() => { readUrl(); window.addEventListener('popstate',readUrl) })
onUnmounted(() => window.removeEventListener('popstate',readUrl))
</script>

<template>
  <section class="forge-evidence" aria-label="Recorded trial evidence">
    <div class="filters">
      <label>Project<select aria-label="Project" v-model="project" @change="changeFilter"><option value="all">All projects</option><option v-for="p in projects" :key="p">{{ p }}</option></select></label>
      <label>Cohort<select aria-label="Cohort" v-model="scope" @change="changeFilter"><option value="primary">Primary comparison · 39</option><option value="other">Other recorded attempts · 90</option><option value="all">All recorded attempts · 129</option></select></label>
      <label>Outcome<select aria-label="Outcome" v-model="outcome" @change="changeFilter"><option value="all">All outcomes</option><option v-for="o in outcomes" :key="o" :value="o">{{ label(o) }}</option></select></label>
      <label class="search">Find a trial, treatment, source revision, or error<input v-model="query" type="search" @input="changeFilter" placeholder="For example: metadata or 9feeffa8" /></label>
      <button type="button" @click="reset">Reset filters</button>
    </div>
    <p class="denominator" role="status" aria-live="polite">{{ filtered.length }} matching attempts · {{ passed }} recorded passes · {{ filtered.length - passed }} other outcomes</p>
    <p v-if="scope !== 'primary'" class="scope-note">These native grades include historical checks, diagnostics, loops, and graphs. They are not a single controlled comparison and do not all establish visible-answer acceptance.</p>
    <p v-if="notice" role="alert">{{ notice }}</p>
    <p v-if="!filtered.length" class="empty">No recorded attempt matches these filters. No result is being treated as zero success. Projects 07–08 are available under “Other recorded attempts” or “All recorded attempts.”</p>
    <details v-for="trial in visible" :key="trial.id" :open="selected === trial.id" class="trial">
      <summary @click.prevent="toggle(trial.id)">
        <span class="trial-heading">{{ trial.project.slice(-2) }} · {{ trial.variant }} · repeat {{ trial.trial }}</span>
        <span :class="['outcome',trial.outcome === 'passed' ? 'passed' : 'failed']">{{ label(trial.outcome) }}</span>
        <span class="trial-id">{{ trial.id.slice(0,8) }}</span>
      </summary>
      <div class="trial-body">
        <p><strong>{{ trial.primary ? 'Primary comparison' : 'Other recorded attempt' }}</strong> · protocol {{ trial.protocolRevision ?? 'unavailable' }} · {{ trial.startedAt }} → {{ trial.finishedAt }}</p>
        <p class="hash">Trial: {{ trial.id }}<br />Source: <a :href="sourceUrl(trial)">{{ trial.sourceCommit }}</a><br />Patch SHA-256: {{ trial.patchSha256 || 'No exported patch recorded' }}</p>
        <p class="links"><a :href="safeUrl(trial.wandbRunUrl)">W&amp;B run ↗</a><a :href="safeUrl(trial.artifactUrl)">Patch, logs, and artifact ↗</a><a v-for="(url,i) in trial.agentLensUrls" :key="url" :href="safeUrl(url)">Agent Lens {{ i+1 }} ↗</a></p>
        <p class="access">Linked Forge/W&amp;B evidence requires membership in the private course project. Original files are also indexed by path and SHA-256 below.</p>
        <p>Actual input tokens: <strong>{{ trial.inputTokens ?? 'unavailable' }}</strong> · output tokens: <strong>{{ trial.outputTokens ?? 'unavailable' }}</strong>. Recorded estimate: <strong>{{ trial.reconciledEstimateUsd == null ? 'unknown' : '$' + trial.reconciledEstimateUsd.toFixed(6) }}</strong>. Estimates are not invoices.</p>
        <p v-if="trial.actorError">Actor error: {{ trial.actorError }}</p>
        <p>Actor completion: {{ trial.actorCompleted == null ? 'not recorded' : trial.actorCompleted ? 'reported complete' : 'did not report complete' }}. The protected grade is recorded separately.</p>
        <table class="checks"><caption>Checks actually executed; omitted checks are not passes.</caption><thead><tr><th scope="col">Check</th><th scope="col">Result and recorded error</th></tr></thead><tbody><tr v-for="check in trial.checks" :key="check.name"><th scope="row">{{ check.name }}</th><td><strong :class="check.passed ? 'pass-text' : 'fail-text'">{{ check.passed ? 'Passed' : 'Failed' }}</strong><p v-if="check.error">{{ check.error }}</p></td></tr></tbody></table>
        <p v-if="!trial.checks.length">No protected check results were recorded for this attempt.</p>
        <div v-if="trial.captures.length" class="captures">
          <figure v-for="capture in trial.captures" :key="capture.file"><a :href="imageUrl(capture.file)" target="_blank" rel="noopener"><img :src="imageUrl(capture.file)" loading="lazy" :alt="'Original Electron capture for '+trial.project+', '+trial.variant+', repeat '+trial.trial+'. Overall outcome: '+label(trial.outcome)+'.'" /></a><figcaption>{{ capture.originalArtifactPath.split('/').slice(-1)[0] }} · original capture. Open for full size; the image alone does not establish every check.</figcaption></figure>
        </div>
        <p v-else class="unavailable">No application screenshot was retained for this attempt. The grade and logs remain available; an image from another run has not been substituted.</p>
        <details><summary>Changed files and frozen configuration</summary><ul><li v-for="file in trial.changedFiles" :key="file"><code>{{ file }}</code></li></ul><p v-if="!trial.changedFiles.length">No changed file paths in the exported patch.</p><p class="hash">Staged application: {{ trial.applicationSha256 || 'not recorded' }}<br />Protected checker: {{ trial.checkerSha256 || 'not recorded' }}<br />Protocol: {{ trial.protocolSha256 || 'not recorded' }}</p><pre>{{ JSON.stringify(trial.protocol,null,2) }}</pre></details>
        <details><summary>Original evidence inventory · {{ trial.evidenceFiles.length }} files</summary><p>Paths refer to the complete course artifact linked above this explorer. SHA-256 values identify the local source bytes. Raw transcripts and patches remain in the private artifact.</p><table><thead><tr><th scope="col">Artifact path</th><th scope="col">Bytes / SHA-256</th></tr></thead><tbody><tr v-for="file in trial.evidenceFiles" :key="file.path"><td class="path">{{ file.path }}</td><td class="hash">{{ file.bytes }}<br />{{ file.sha256 }}</td></tr></tbody></table></details>
      </div>
    </details>
    <nav v-if="filtered.length" class="pagination" aria-label="Trial pages"><button :disabled="page === 0" @click="changePage(-1)">Previous</button><span>Page {{ page+1 }} of {{ pages }}</span><button :disabled="page+1 >= pages" @click="changePage(1)">Next</button></nav>
    <p class="downloads"><a :href="withBase('/forge/evidence/trials.csv')" download>Download all 129 rows (CSV)</a> · <a :href="withBase('/forge/evidence/catalog.json')" download>Download evidence catalog (JSON)</a></p>
  </section>
</template>

<style scoped>
.forge-evidence{margin:2rem 0;color:var(--vp-c-text-1)}
.filters{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;padding:18px;border:1px solid var(--vp-c-divider);border-radius:8px;background:var(--vp-c-bg-soft)}
label{display:flex;flex-direction:column;gap:6px;font-size:13px;font-weight:600}.search{grid-column:1/3}
select,input{width:100%;min-width:0;border:1px solid var(--vp-c-divider);background:var(--vp-c-bg);border-radius:4px;padding:9px 10px;font:inherit;color:inherit;min-height:42px}
button{padding:9px 14px;border:1px solid var(--vp-c-divider);border-radius:4px;background:var(--vp-c-bg);font-weight:600;align-self:end;min-height:42px}button:disabled{opacity:.4;cursor:not-allowed}
:is(button,select,input,summary,a):focus-visible{outline:3px solid var(--vp-c-brand-1);outline-offset:3px}
.denominator{font-weight:700}.scope-note,.empty,.unavailable{border-left:3px solid #ac7938;padding:8px 12px;background:var(--vp-c-bg-soft)}
.trial{border-top:1px solid var(--vp-c-divider);padding:0}.trial>summary{cursor:pointer;display:flex;align-items:center;gap:10px;flex-wrap:wrap;padding:14px 6px;font-size:14px;list-style:none;min-height:48px}.trial>summary:before{content:'+';font-size:20px;width:15px}.trial[open]>summary:before{content:'−'}.trial-heading{flex:1;min-width:200px;font-weight:600}.trial-id{font-family:monospace;color:var(--vp-c-text-2)}
.outcome{padding:2px 8px;border-radius:3px;font-size:12px;font-weight:700}.passed{background:#dbece6;color:#135342}.failed{background:#f5dfd9;color:#902d1f}.pass-text{color:#176c59}.fail-text{color:#a53624}
.trial-body{padding:4px 8px 18px}.trial-body p{font-size:14px;line-height:1.6}.links{display:flex;gap:10px 18px;flex-wrap:wrap}.access{color:var(--vp-c-text-2)}
.hash,.path{overflow-wrap:anywhere;font-size:12px;font-family:monospace}.checks{width:100%;display:table;table-layout:fixed}.checks caption{text-align:left;padding:10px 0;font-size:13px;color:var(--vp-c-text-2)}.checks th,.checks td{overflow-wrap:anywhere;vertical-align:top;font-size:13px}.checks td p{font-size:12px;margin:5px 0}.checks th{font-weight:500}
.captures{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.captures figure{margin:8px 0}.captures img{border:1px solid var(--vp-c-divider);border-radius:4px}.captures figcaption{font-size:12px;line-height:1.5;color:var(--vp-c-text-2);margin-top:6px}
.trial-body details{margin:14px 0}.trial-body details>summary{cursor:pointer;font-weight:600;font-size:14px;padding:8px 0}.trial-body pre{font-size:12px;max-height:420px;overflow:auto;padding:12px;background:var(--vp-c-bg-soft)}
.pagination{display:flex;align-items:center;justify-content:space-between;margin-top:18px;font-size:13px}.downloads{font-size:13px}
@media(max-width:640px){.filters{grid-template-columns:1fr}.search{grid-column:auto}.captures{grid-template-columns:1fr}.trial-heading{min-width:170px}.trial-id{display:block}.checks th,.checks td{padding:8px}.trial-body{padding-left:0;padding-right:0}}
:global(.dark) .pass-text{color:#78c6ad}:global(.dark) .fail-text{color:#f4a18c}
</style>
