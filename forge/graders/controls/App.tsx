// Protected positive control; never included in an agent workspace.
import {useEffect,useState} from 'react';
import type {Document,QAResponse,QAHistory} from '../shared/types';
type Api={documents:{list:()=>Promise<Document[]>;pickImport:()=>Promise<Document|null>;getContent:(id:string)=>Promise<string>};qa:{ask:(q:string)=>Promise<QAResponse>;history:()=>Promise<QAHistory[]>;clear:()=>Promise<void>};app:{reset:()=>Promise<void>}};
const api=window.knowledgeBase as unknown as Api;
export function App(){
  const [docs,setDocs]=useState<Document[]>([]),[question,setQuestion]=useState(''),[answer,setAnswer]=useState<QAResponse|null>(null),[selected,setSelected]=useState(''),[history,setHistory]=useState<QAHistory[]>([]),[historyOpen,setHistoryOpen]=useState(false);
  const refresh=async()=>{setDocs(await api.documents.list());setHistory(await api.qa.history());};
  useEffect(()=>{void refresh();},[]);
  return <main style={{padding:24,color:'#eeeeee',background:'#16213e',minHeight:'100vh'}}>
    <h1>Knowledge Base</h1><button onClick={()=>void refresh()}>Refresh</button>
    <button onClick={async()=>{await api.documents.pickImport();await refresh();}}>+ Import</button>
    <button onClick={async()=>{await refresh();setHistoryOpen(!historyOpen);}}>Conversation history</button>
    <button onClick={async()=>{if(confirm('Reset all data?')){await api.app.reset();setAnswer(null);setSelected('');setHistory([]);setDocs([]);await refresh();}}}>Reset</button>
    <section>{docs.map(doc=><button key={doc.id} onClick={async()=>setSelected(await api.documents.getContent(doc.id))}>{doc.title}</button>)}</section>
    {selected&&<article>{selected}</article>}
    <input type="text" value={question} onChange={event=>setQuestion(event.target.value)}/>
    <button onClick={async()=>{setAnswer(await api.qa.ask(question));await refresh();}}>Ask</button>
    {answer&&<article><p>{answer.answer}</p>{answer.citations.map((c,i)=><p key={i}>{c.excerpt}</p>)}</article>}
    {historyOpen&&<section><button onClick={async()=>{if(confirm('Clear history?')){await api.qa.clear();setHistory([]);}}}>Clear history</button>
      {history.map((item,i)=><article key={i}><h2>{item.question}</h2><p>{item.response.answer}</p><p>Confidence {item.response.confidence}</p><time>{item.response.timestamp}</time><details><summary>Citations</summary>{item.response.citations.map((c,j)=><p key={j}>{c.excerpt}</p>)}</details></article>)}
    </section>}
  </main>;
}
