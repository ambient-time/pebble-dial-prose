// Execute the shipped phone bundle, including Clay, not a settings mock.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const root=path.resolve(process.argv[2]),events={},sent=[],storage={};let url;
const context={console,setTimeout,clearTimeout,encodeURIComponent,decodeURIComponent,localStorage:{getItem:k=>storage[k]??null,setItem:(k,v)=>storage[k]=v},Pebble:{platform:'basalt',addEventListener:(n,f)=>{(events[n]??=[]).push(f)},openURL:u=>url=u,sendAppMessage:d=>sent.push(d),getActiveWatchInfo:()=>({platform:'basalt'}),getAccountToken:()=>'',getWatchToken:()=>''}};
vm.runInNewContext(fs.readFileSync(path.join(root,'build/pebble-js-app.js'),'utf8'),context);
const fire=(n,e)=>events[n].forEach(f=>f(e));const config=JSON.parse(fs.readFileSync(path.join(root,'src/pkjs/config.json')));const total=config[1].options.length;
fire('showConfiguration',{});assert(url.startsWith('data:'));fs.writeFileSync(path.join(root,'build/languages/settings.html'),decodeURIComponent(url.slice(url.indexOf(',')+1)));
for(let i=0;i<total;i++){fire('webviewclosed',{response:encodeURIComponent(JSON.stringify({LANGUAGE:{value:String(i)}}))});assert.equal(sent.at(-1).LANGUAGE,i)}
const count=sent.length;for(const value of [-1,total,'garbage','',null,{},true,1.2])fire('webviewclosed',{response:encodeURIComponent(JSON.stringify({LANGUAGE:{value}}))});fire('webviewclosed',{response:''});fire('webviewclosed',{response:'bad json'});assert.equal(sent.length,count);
fire('webviewclosed',{response:encodeURIComponent(JSON.stringify({LANGUAGE:{value:'1'}}))});fire('showConfiguration',{});assert.equal(JSON.parse(storage['clay-settings']).LANGUAGE,'1');fs.writeFileSync(path.join(root,'build/languages/settings-saved.html'),decodeURIComponent(url.slice(url.indexOf(',')+1)));
console.log(root,total,'settings choices reach numeric AppMessage; invalid input and cancellation rejected');
