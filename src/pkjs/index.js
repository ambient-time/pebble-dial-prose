// Copyright 2026 Luke Steuber. MIT License.
var Clay = require('@rebble/clay');
var config = require('./config.json');
var clay = new Clay(config, null, {autoHandleEvents:false});
Pebble.addEventListener('showConfiguration', function() { Pebble.openURL(clay.generateUrl()); });
Pebble.addEventListener('webviewclosed', function(event) {
  if (!event.response) return;
  try {
    var settings = JSON.parse(event.response.charAt(0) === '{' ? event.response : decodeURIComponent(event.response));
    var raw = settings.LANGUAGE === undefined ? settings[0] : settings.LANGUAGE;
    if (raw && typeof raw === 'object') raw = raw.value;
    var language = Number(raw);
    if ((typeof raw !== 'string' && typeof raw !== 'number') || raw === '' || !isFinite(language) || language % 1 || language < 0 || language >= config[1].options.length) return;
    clay.getSettings(event.response, false);
    Pebble.sendAppMessage({LANGUAGE:language});
  } catch (error) { console.log('Language selection was not saved.'); }
});
