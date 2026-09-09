// Execute bundled phone code and its generated page; preserve watch-owned preferences.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,"..");const cfg=JSON.parse(fs.readFileSync(path.join(root,'src/pkjs/theme-settings.json')));
const handlers={},sent=[],urls=[],timers=new Map();let timerID=0;
const context={console,encodeURIComponent,decodeURIComponent,setTimeout:fn=>{timers.set(++timerID,fn);return timerID},clearTimeout:id=>timers.delete(id),Pebble:{addEventListener:(n,f)=>{(handlers[n]??=[]).push(f)},sendAppMessage:(value,ok,fail)=>sent.push({value,ok,fail}),openURL:u=>urls.push(u)}};
const bundle=path.join(root,'build/pebble-js-app.js');
context.require=n=>{assert.equal(n,'./theme-settings.json');return cfg;};
vm.runInNewContext(fs.readFileSync(fs.existsSync(bundle)?bundle:path.join(root,'src/pkjs/index.js'),'utf8'),context);
const fire=(n,e)=>handlers[n].forEach(f=>f(e));
const last=()=>sent.at(-1).value;
fire('ready');assert.deepEqual(JSON.parse(JSON.stringify(last())),{REQUEST_STATE:1});
fire('showConfiguration');assert.equal(urls.length,0);
const state=Object.fromEntries(cfg.controls.map(c=>[c.key,c.options.length-1]));
fire('appmessage',{payload:state});assert.equal(urls.length,1);assert.equal(timers.size,0);
const html=decodeURIComponent(urls[0].split(',').slice(1).join(','));assert(!html.includes(' disabled'));
const elements={settings:{}};for(const c of cfg.controls){elements[c.key]={value:String(state[c.key])};assert(html.includes('<label for="'+c.key+'">'));assert(html.includes('value="'+state[c.key]+'" selected'));}
const page={document:{getElementById:k=>elements[k]},location:{}};vm.runInNewContext(html.match(/<script>([\s\S]*?)<\/script>/)[1],page);
elements.settings.onsubmit({preventDefault(){}});assert.equal(decodeURIComponent(page.location.href.split('#')[1]),'{}');
elements.THEME.value='0';elements.settings.onsubmit({preventDefault(){}});const response=page.location.href.split('#')[1];assert.equal(decodeURIComponent(response),'{"THEME":0}');
let before=sent.length;fire('webviewclosed',{response});assert.equal(sent.length,before+1);assert.deepEqual(JSON.parse(JSON.stringify(last())),{THEME:0});sent.at(-1).ok();assert.equal(last().REQUEST_STATE,1);
for(const c of cfg.controls)for(let i=0;i<c.options.length;i++){before=sent.length;fire('webviewclosed',{response:encodeURIComponent(JSON.stringify({[c.key]:i}))});assert.equal(sent.length,before+1);assert.equal(last()[c.key],i);assert.equal(Object.keys(last()).length,1);}
before=sent.length;for(const response of ['', 'CANCELLED','{}','null','[]','bad json','{"THEME":-1}','{"THEME":999}','{"THEME":"1"}','{"THEME":true}','{"THEME":1.5}','{"THEME":0,"unknown":1}'])fire('webviewclosed',{response});assert.equal(sent.length,before);
for(const c of cfg.controls)for(const value of [-1,c.options.length,1.5,'1',true,null,{}]){before=sent.length;fire('webviewclosed',{response:JSON.stringify({[c.key]:value})});assert.equal(sent.length,before);}
fire('showConfiguration');const count=urls.length;fire('appmessage',{payload:{THEME:999}});assert.equal(urls.length,count);[...timers.values()][0]();assert(decodeURIComponent(urls.at(-1)).includes(' disabled'));assert(decodeURIComponent(urls.at(-1)).includes('Reconnect your watch'));
fs.mkdirSync(path.join(root,'build/themes'),{recursive:true});fs.writeFileSync(path.join(root,'build/themes/settings.html'),html);
console.log(path.basename(root)+': bundled settings pass watch state, all choices, independent changes, cancel, invalid and offline cases');
