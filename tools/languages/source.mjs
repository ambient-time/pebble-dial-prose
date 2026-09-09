// Copyright 2026 Luke Steuber. MIT License.
import fs from 'node:fs';import vm from 'node:vm';import path from 'node:path';import crypto from 'node:crypto';
const root=path.resolve(process.argv[2]||'.'),dir=path.join(root,'reference/multilingual');
const source=fs.readFileSync(path.join(dir,'source.html'),'utf8'),shared=fs.readFileSync(path.join(dir,'word-time.js'),'utf8');
const pin=JSON.parse(fs.readFileSync(path.join(dir,'provenance.json')));
for(const [name,text] of [['source.html',source],['word-time.js',shared]])if(crypto.createHash('sha256').update(text).digest('hex')!==pin.files[name])throw Error('Source drift '+name);
const prose=JSON.parse(fs.readFileSync(path.join(root,'package.json'))).name==='dial-prose',ctx=vm.createContext({window:{}});
if(prose){vm.runInContext(shared,ctx);vm.runInContext('const WT=window.WORD_TIME; const LANGUAGES=WT.LANGUAGES;'+source.slice(source.indexOf('const ARTICLE_WORDS'),source.indexOf('const STORAGE'))+source.slice(source.indexOf('const labelCache'),source.indexOf('// =============================================================================\n// Prose renderer')),ctx);}
else {vm.runInContext(source.slice(source.indexOf('const LANGUAGES ='),source.indexOf('const STORAGE =')),ctx);vm.runInContext('const WT={LANGUAGES,HOURS,SUBJECT_PHRASE,DIAL_LAYOUT,timeWords};',ctx);}
const result=vm.runInContext(`(()=>{const phrases={};for(const lang of LANGUAGES){phrases[lang]=[];for(let slot=0;slot<288;slot++){const h=Math.floor(slot/12),m=(slot%12)*5,words=WT.timeWords(lang,h,m).words;for(let k=1;k<5;k++)if(JSON.stringify(WT.timeWords(lang,h,m+k).words)!==JSON.stringify(words))throw Error('Sub-five-minute grammar');phrases[lang].push({hour:h,minute:m,words,lines:${prose?'groupLines(lang,words)':'[]'}});}}return {languages:LANGUAGES,subject:WT.SUBJECT_PHRASE,layout:WT.DIAL_LAYOUT,phrases};})()`,ctx,{timeout:5000});
console.log(JSON.stringify(result));
