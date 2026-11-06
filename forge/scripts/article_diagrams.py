"""Editable SVG explanations of the recorded course workflow; no generated UI."""
from pathlib import Path
from html import escape

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/en/forge/assets/diagrams'
OUT.mkdir(parents=True,exist_ok=True)

def diagram(name,title,description,height,parts):
    source=f'''<svg xmlns="http://www.w3.org/2000/svg" width="680" height="{height}" viewBox="0 0 680 {height}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>
<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="#62665e"/></marker></defs>
<rect width="680" height="{height}" rx="8" fill="#faf9f6"/>
<style>text{{font-family:Arial,Helvetica,sans-serif;fill:#242722}}.title{{font-size:25px;font-weight:700}}.head{{font-size:20px;font-weight:700}}.body{{font-size:16px}}.note{{font-size:15px;fill:#62665e}}</style>
<text class="title" x="28" y="40">{escape(title)}</text>
{''.join(parts)}</svg>'''
    (OUT/(name+'.svg')).write_text(source+'\n')

def text(x,y,content,cls='body'):
    return f'<text class="{cls}" x="{x}" y="{y}">{escape(content)}</text>'
def box(y,heading,lines,fill='#ffffff',stroke='#d6d6ce',height=100,x=28,width=624):
    return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="6" fill="{fill}" stroke="{stroke}"/>'+text(x+18,y+30,heading,'head')+''.join(text(x+18,y+57+i*22,line) for i,line in enumerate(lines))
def arrow(y1,y2,label=None):
    return f'<path d="M340 {y1} L340 {y2}" stroke="#62665e" stroke-width="2" marker-end="url(#arrow)"/>'+ (text(355,(y1+y2)/2+5,label,'note') if label else '')

diagram('trial-evidence-chain','A grade follows the exported patch',
    'The same frozen starter is staged for each treatment. Pi edits an actor sandbox, exports its patch, and stops. A fresh grader applies that patch and runs services plus Electron. The result links back to the exact patch and source.',715,[
    box(65,'1  Freeze the inputs',['Starter code + selected guidance + task + model settings']),arrow(165,190),
    box(200,'2  Pi edits in an actor sandbox',['Model and tool conversations → candidate.diff']),arrow(300,325,'collect evidence; terminate actor'),
    box(335,'3  A fresh grader applies the patch',['Same baseline; protected checker is outside the actor']),arrow(435,460),
    box(470,'4  Execute services and the Electron window',['Import · chunks · retrieval · Q&A · Xvfb/UI assertions']),arrow(570,595),
    box(605,'5  Record the observed outcome',['Grade + patch checksum + source + run + trace IDs'],fill='#e7f0eb',height=85),
])

diagram('session-boundary','A new conversation, a surviving workspace',
    'Session one writes source and a handoff into the actor workspace. Session two starts with fresh model context and reads that workspace. Prior messages are not replayed. The coordinator and app persistence are separate state owners.',590,[
    box(65,'Session 1 · first Pi context',['12-call allowance; edit code and record what was checked']),arrow(165,195,'files remain on disk'),
    box(205,'Actor workspace survives',['Edited source + handoff + application data files'],fill='#e7f0eb'),arrow(305,335,'read files; verify their claims'),
    box(345,'Session 2 · fresh Pi context',['12-call allowance; the prior message history is not replayed']),
    text(28,485,'Conversation reset is the tested boundary, not an arbitrary machine crash.','note'),
    text(28,515,'The coordinator owns trial IDs and exported evidence.','note'),
    text(28,545,'Application services own the consistency of persisted documents and indexes.','note'),
])

diagram('graph-attempts','Three Pi candidates; one approval pause',
    'In the explicit-contract graph run, attempt one fails the architecture guard and rolls back. Attempt two fails compilation and rolls back. Attempt three passes the protected grade and independent service and Electron lanes, then pauses for human approval. A separate manual candidate was approved later.',755,[
    box(65,'Attempt 1 · 3e5cd770',['Guard accepts a prohibited Node import.','Protected grade fails; the graph rolls back.'],fill='#f5e5df',height=112),arrow(177,207,'restore starting point'),
    box(217,'Attempt 2 · 43ad509b',['TypeScript compilation fails.','The graph records the failure and rolls back.'],fill='#f5e5df',height=112),arrow(329,359,'restore starting point'),
    box(369,'Attempt 3 · 03ca01ca',['Protected grade passes.','Independent services + Electron lanes also pass.'],fill='#e7f0eb',height=112),arrow(481,511),
    box(521,'STOP · explicit human decision required',['Pi candidate c74cf9cf3716… remains at approval.','Passing tests do not approve or merge the patch.'],fill='#f5eddc',height=112),
    text(28,680,'Separate manual candidate 91c4a2df7b9a… was approved later.','note'),
    text(28,710,'That decision changed only its own qualification checkpoint.','note'),
])
print('Wrote 3 editable workflow SVGs.')
