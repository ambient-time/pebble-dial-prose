// Copyright 2026 Luke Steuber. MIT License.
// Bundled, named controls. The watch owns settings; a phone never replays defaults.
'use strict';
var config = require('./theme-settings.json');
var state = {}, opening = false, timer = null, confirmed = false;
config.controls.forEach(function(c) { state[c.key] = c.default; });
function integer(v, c) { return typeof v === 'number' && isFinite(v) && v % 1 === 0 && v >= 0 && v < c.options.length; }
function escape(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/"/g,'&quot;'); }
function request() { Pebble.sendAppMessage({REQUEST_STATE:1}); }
function openPage() {
  if (!opening) return;
  opening = false; clearTimeout(timer);
  var controls = config.controls.map(function(c) {
    return '<label for="'+c.key+'">'+escape(c.label)+'</label><select id="'+c.key+'"'+(!confirmed?' disabled':'')+'>'+c.options.map(function(s,i) {
      return '<option value="'+i+'"'+(state[c.key]===i?' selected':'')+'>'+escape(s)+'</option>';
    }).join('')+'</select>';
  }).join('');
  var keys = JSON.stringify(config.controls.map(function(c){return c.key;}));
  var initial = JSON.stringify(state);
  var html = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+escape(config.title)+' settings</title><style>body{font:18px/1.5 system-ui,sans-serif;background:#fff;color:#111;max-width:30rem;margin:0 auto;padding:20px}h1{font-size:26px}label{display:block;font-weight:600;margin-top:20px}select,button{box-sizing:border-box;display:block;width:100%;min-height:48px;font:inherit;padding:10px;margin:8px 0 20px;color:#111;background:#fff;border:2px solid #555;border-radius:6px}button{background:#111;color:white}a{display:inline-block;padding:12px 0;color:#003366}:focus-visible{outline:3px solid #0055aa;outline-offset:3px}</style><h1>'+escape(config.title)+'</h1><p>'+ (confirmed?'Themes keep the same time layout. Monochrome watches use black and white.':'Reconnect your watch, then close and reopen settings to load its saved choices.')+'</p><form id="settings">'+controls+'<button type="submit"'+(!confirmed?' disabled':'')+'>Save to watch</button></form><a href="pebblejs://close#">Cancel</a><script>var initial='+initial+';document.getElementById("settings").onsubmit=function(e){e.preventDefault();var result={};'+keys+'.forEach(function(k){var v=Number(document.getElementById(k).value);if(v!==initial[k])result[k]=v;});location.href="pebblejs://close#"+encodeURIComponent(JSON.stringify(result));};<\/script></html>';
  Pebble.openURL('data:text/html;charset=utf-8,'+encodeURIComponent(html));
}
Pebble.addEventListener('ready',request);
Pebble.addEventListener('showConfiguration',function(){opening=true;confirmed=false;clearTimeout(timer);timer=setTimeout(openPage,2000);request();});
Pebble.addEventListener('appmessage',function(e){
  var p=e&&e.payload;if(!p)return;
  // Accept only a complete, validated snapshot; no stale mixed settings page.
  if(!config.controls.every(function(c){return integer(p[c.key],c);}))return;
  config.controls.forEach(function(c){state[c.key]=p[c.key];});confirmed=true;openPage();
});
Pebble.addEventListener('webviewclosed',function(e){
  if(!e||!e.response||e.response==='CANCELLED')return;
  try{
    var r=JSON.parse(e.response.charAt(0)==='{'?e.response:decodeURIComponent(e.response)),out={};
    if(!r||typeof r!=='object'||Array.isArray(r))return;
    var keys=Object.keys(r);if(!keys.length)return;
    for(var i=0;i<keys.length;i++){
      var key=keys[i],control=config.controls.filter(function(c){return c.key===key;})[0];
      if(!control||!integer(r[key],control))return;out[key]=r[key];
    }
    Pebble.sendAppMessage(out,request,function(){console.log('Settings were not delivered. Reconnect and try again.');});
  }catch(error){console.log('Invalid settings response ignored.');}
});
