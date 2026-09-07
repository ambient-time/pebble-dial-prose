// Copyright 2026 Luke Steuber. MIT License.
// Run the pinned source's pure grammar independently of the native implementation.
import fs from 'node:fs';
import vm from 'node:vm';
import crypto from 'node:crypto';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const source=fs.readFileSync(path.join(root,'reference/source.html'),'utf8');
const hash=crypto.createHash('sha256').update(source).digest('hex');
if(hash!=='663fe9590e6780df70a8938528a6a5fbd0175585d3e541de832b7596b6272166')throw Error('Source fingerprint changed');
const start=source.indexOf('(function (root) {'),end=source.indexOf('</script>',start);
if(start<0||end<0)throw Error('Missing source grammar');
const ctx=vm.createContext({});vm.runInContext(source.slice(start,end),ctx,{timeout:1000});
const result=vm.runInContext(String.raw`(()=>{const W=WORD_TIME,layout=W.DIAL_LAYOUT.en,labels={};for(const group of ['minutes','connectors','articles'])for(const t of layout[group])labels[t.word]=t.label.replace(/\s*\n\s*/g,' ');return Array.from({length:1440},(_,i)=>({time:String(Math.floor(i/60)).padStart(2,'0')+':'+String(i%60).padStart(2,'0'),sentence:W.timeWords('en',Math.floor(i/60),i%60).words.map(t=>labels[t.word]||t.word).join(' ')}));})()`,ctx);
console.log(JSON.stringify({sourceSHA256:hash,phrases:result}));
