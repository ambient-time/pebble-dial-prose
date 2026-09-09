/*
 * Word Time engine — the multilingual spoken-time data and grammar from
 * /clocks/dial/ (Word Dial), extracted verbatim so derivative clocks share
 * one source of truth. Attaches window.WORD_TIME with:
 *   LANGUAGES, HOURS, SUBJECT_PHRASE, DIAL_LAYOUT, timeWords(lang, h, m).
 * Active consumers: dial-matrix, dial-prose, dial-spiral, dial-ticker. The
 * archived dial-bezel also imports this file. Keep grammar edits in sync with /clocks/dial/index.html or
 * migrate the dial itself onto this file deliberately (not casually).
 */
(function (root) {
"use strict";

const LANGUAGES = ['en','de','fr','it','es','pt','nl','sv','uk','ja','zh','ko','ar'];

const HOURS = {
  en: ['one','two','three','four','five','six','seven','eight','nine','ten','eleven','twelve'],
  de: ['eins','zwei','drei','vier','fünf','sechs','sieben','acht','neun','zehn','elf','zwölf'],
  fr: ['une','deux','trois','quatre','cinq','six','sept','huit','neuf','dix','onze','midi'],
  it: ['una','due','tre','quattro','cinque','sei','sette','otto','nove','dieci','undici','dodici'],
  es: ['una','dos','tres','cuatro','cinco','seis','siete','ocho','nueve','diez','once','doce'],
  pt: ['uma','duas','três','quatro','cinco','seis','sete','oito','nove','dez','onze','doze'],
  nl: ['een','twee','drie','vier','vijf','zes','zeven','acht','negen','tien','elf','twaalf'],
  sv: ['ett','två','tre','fyra','fem','sex','sju','åtta','nio','tio','elva','tolv'],
  uk: ['перша','друга','третя','четверта','пʼята','шоста','сьома','восьма','девʼята','десята','одинадцята','дванадцята'],
  ja: ['一時','二時','三時','四時','五時','六時','七時','八時','九時','十時','十一時','十二時'],
  zh: ['一点','两点','三点','四点','五点','六点','七点','八点','九点','十点','十一点','十二点'],
  ko: ['한시','두시','세시','네시','다섯시','여섯시','일곱시','여덟시','아홉시','열시','열한시','열두시'],
  ar: ['الواحدة','الثانية','الثالثة','الرابعة','الخامسة','السادسة','السابعة','الثامنة','التاسعة','العاشرة','الحادية عشرة','الثانية عشرة'],
};

const SUBJECT_PHRASE = {
  en: 'it is',
  de: 'es ist',
  fr: 'il est',
  it: 'sono le',
  es: 'son las',
  pt: 'são as',
  nl: 'het is',
  sv: 'klockan är',
  uk: 'зараз',
  ja: '今は',
  zh: '现在',
  ko: '지금',
  ar: 'الساعة',
};

const DIAL_LAYOUT = {
  en: {
    minutes: [
      { word:'five',       label:'five',          type:'minutes' },
      { word:'ten',        label:'ten',           type:'minutes' },
      { word:'quarter',    label:'quarter',       type:'minutes' },
      { word:'twenty',     label:'twenty',        type:'minutes' },
      { word:'twentyfive', label:'twenty\nfive',  type:'minutes' },
    ],
    connectors: [
      { word:'oclock', label:"o'clock",  type:'desc' },
      { word:'till',   label:'till',     type:'desc' },
      { word:'past',   label:'past',     type:'desc' },
      { word:'half',   label:'half',     type:'minutes' },
    ],
    articles: [
      { word:'a', label:'a', type:'desc' },
    ],
    hours: ['one','two','three','four','five','six','seven','eight','nine','ten','eleven','twelve'],
  },
  de: {
    minutes: [
      { word:'fünf',    label:'fünf',    type:'minutes' },
      { word:'zehn',    label:'zehn',    type:'minutes' },
      { word:'viertel', label:'viertel', type:'minutes' },
      { word:'zwanzig', label:'zwanzig', type:'minutes' },
    ],
    connectors: [
      { word:'uhr',  label:'uhr',  type:'desc' },
      { word:'vor',  label:'vor',  type:'desc' },
      { word:'nach', label:'nach', type:'desc' },
      { word:'halb', label:'halb', type:'minutes' },
    ],
    hours: ['eins','zwei','drei','vier','fünf','sechs','sieben','acht','neun','zehn','elf','zwölf'],
  },
  fr: {
    minutes: [
      { word:'cinq',       label:'cinq',         type:'minutes' },
      { word:'dix',        label:'dix',          type:'minutes' },
      { word:'quart',      label:'quart',        type:'minutes' },
      { word:'vingt',      label:'vingt',        type:'minutes' },
      { word:'vingt-cinq', label:'vingt\ncinq',  type:'minutes' },
    ],
    connectors: [
      { word:'demie',  label:'demie',  type:'minutes' },
      { word:'et',     label:'et',     type:'desc' },
      { word:'moins',  label:'moins',  type:'desc' },
      { word:'heures', label:'heures', type:'desc' },
    ],
    articles: [
      { word:'le', label:'le', type:'desc' },
    ],
    hours: ['une','deux','trois','quatre','cinq','six','sept','huit','neuf','dix','onze','midi'],
  },
  it: {
    minutes: [
      { word:'cinque',      label:'cinque',         type:'minutes' },
      { word:'dieci',       label:'dieci',          type:'minutes' },
      { word:'quarto',      label:'quarto',         type:'minutes' },
      { word:'venti',       label:'venti',          type:'minutes' },
      { word:'venticinque', label:'venti-\ncinque', type:'minutes' },
    ],
    connectors: [
      { word:'mezza',   label:'mezza',    type:'minutes' },
      { word:'e',       label:'e',        type:'desc' },
      { word:'meno',    label:'meno',     type:'desc' },
      { word:'inpunto', label:'in punto', type:'desc' },
    ],
    articles: [
      { word:'un', label:'un', type:'desc' },
    ],
    hours: ['una','due','tre','quattro','cinque','sei','sette','otto','nove','dieci','undici','dodici'],
  },
  es: {
    minutes: [
      { word:'cinco',       label:'cinco',         type:'minutes' },
      { word:'diez',        label:'diez',          type:'minutes' },
      { word:'cuarto',      label:'cuarto',        type:'minutes' },
      { word:'veinte',      label:'veinte',        type:'minutes' },
      { word:'veinticinco', label:'veinti-\ncinco',type:'minutes' },
    ],
    connectors: [
      { word:'media',   label:'media',    type:'minutes' },
      { word:'y',       label:'y',        type:'desc' },
      { word:'menos',   label:'menos',    type:'desc' },
      { word:'enpunto', label:'en punto', type:'desc' },
    ],
    hours: ['una','dos','tres','cuatro','cinco','seis','siete','ocho','nueve','diez','once','doce'],
  },
  pt: {
    minutes: [
      { word:'cinco',     label:'cinco',         type:'minutes' },
      { word:'dez',       label:'dez',           type:'minutes' },
      { word:'quinze',    label:'quinze',        type:'minutes' },
      { word:'vinte',     label:'vinte',         type:'minutes' },
      { word:'vintecinco',label:'vinte e\ncinco',type:'minutes' },
    ],
    connectors: [
      { word:'meia',  label:'meia',  type:'minutes' },
      { word:'e',     label:'e',     type:'desc' },
      { word:'menos', label:'menos', type:'desc' },
      { word:'horas', label:'horas', type:'desc' },
    ],
    hours: ['uma','duas','três','quatro','cinco','seis','sete','oito','nove','dez','onze','doze'],
  },
  nl: {
    minutes: [
      { word:'vijf',  label:'vijf',  type:'minutes' },
      { word:'tien',  label:'tien',  type:'minutes' },
      { word:'kwart', label:'kwart', type:'minutes' },
    ],
    connectors: [
      { word:'over', label:'over', type:'desc' },
      { word:'voor', label:'voor', type:'desc' },
      { word:'half', label:'half', type:'minutes' },
      { word:'uur',  label:'uur',  type:'desc' },
    ],
    hours: ['een','twee','drie','vier','vijf','zes','zeven','acht','negen','tien','elf','twaalf'],
  },
  sv: {
    minutes: [
      { word:'fem',   label:'fem',   type:'minutes' },
      { word:'tio',   label:'tio',   type:'minutes' },
      { word:'kvart', label:'kvart', type:'minutes' },
    ],
    connectors: [
      { word:'över', label:'över', type:'desc' },
      { word:'i',    label:'i',    type:'desc' },
      { word:'halv', label:'halv', type:'minutes' },
    ],
    hours: ['ett','två','tre','fyra','fem','sex','sju','åtta','nio','tio','elva','tolv'],
  },
  uk: {
    // Ukrainian — feminine ordinal hours (used for time). Pattern is a
    // simplified "(hour) і (minute)" past, "(next-hour) без (60-min)" to.
    // This skips the traditional case-shifting forms ("пів на четверту")
    // because the dial can't model dual hour-name shapes per slot.
    minutes: [
      { word:'piat',          label:'пʼять',           type:'minutes' },
      { word:'desiat',        label:'десять',          type:'minutes' },
      { word:'chvert',        label:'чверть',          type:'minutes' },
      { word:'dvadtsiat',     label:'двадцять',        type:'minutes' },
      { word:'dvadtsiatpiat', label:'двадцять\nпʼять', type:'minutes' },
    ],
    connectors: [
      { word:'piv', label:'пів', type:'minutes' },
      { word:'i',   label:'і',   type:'desc' },
      { word:'bez', label:'без', type:'desc' },
    ],
    hours: ['перша','друга','третя','четверта','пʼята','шоста','сьома','восьма','девʼята','десята','одинадцята','дванадцята'],
  },
  ja: {
    minutes: [
      { word:'go',    label:'五',    type:'minutes' },
      { word:'ju',    label:'十',    type:'minutes' },
      { word:'juugo', label:'十五',  type:'minutes' },
      { word:'nijuu', label:'二十',  type:'minutes' },
      { word:'nijuugo', label:'二十\n五', type:'minutes' },
    ],
    connectors: [
      { word:'fun',  label:'分',  type:'desc' },
      { word:'han',  label:'半',  type:'minutes' },
      { word:'mae',  label:'前',  type:'desc' },
      { word:'desu', label:'です', type:'desc' },
    ],
    hours: ['一時','二時','三時','四時','五時','六時','七時','八時','九時','十時','十一時','十二時'],
  },
  zh: {
    minutes: [
      { word:'wu',     label:'五',     type:'minutes' },
      { word:'shi',    label:'十',     type:'minutes' },
      { word:'shiwu',  label:'十五',   type:'minutes' },
      { word:'ershi',  label:'二十',   type:'minutes' },
      { word:'ershiwu',label:'二十\n五', type:'minutes' },
    ],
    connectors: [
      { word:'fen',   label:'分',   type:'desc' },
      { word:'ban',   label:'半',   type:'minutes' },
      { word:'cha',   label:'差',   type:'desc' },
      { word:'xianzai', label:'现在', type:'desc' },
    ],
    hours: ['一点','两点','三点','四点','五点','六点','七点','八点','九点','十点','十一点','十二点'],
  },
  ko: {
    minutes: [
      { word:'o',       label:'오',     type:'minutes' },
      { word:'sip',     label:'십',     type:'minutes' },
      { word:'sipo',    label:'십오',   type:'minutes' },
      { word:'isip',    label:'이십',   type:'minutes' },
      { word:'isipo',   label:'이십\n오', type:'minutes' },
    ],
    connectors: [
      { word:'bun',   label:'분',     type:'desc' },
      { word:'ban',   label:'반',     type:'minutes' },
      { word:'jeon',  label:'전',     type:'desc' },
      { word:'imnida',label:'입니다', type:'desc' },
    ],
    hours: ['한시','두시','세시','네시','다섯시','여섯시','일곱시','여덟시','아홉시','열시','열한시','열두시'],
  },
  ar: {
    // Arabic minute words read right-to-left in their labels (CSS sets
    // direction: rtl on .dial-word for the ar body class). The dial slot
    // positions are unchanged — only glyph shaping inside each label flips.
    minutes: [
      { word:'khams',     label:'خمس',     type:'minutes' },
      { word:'ashr',      label:'عشر',     type:'minutes' },
      { word:'rub',       label:'الربع',   type:'minutes' },
      { word:'ishrun',    label:'عشرون',   type:'minutes' },
      { word:'khamswaishrun', label:'خمس\nوعشرون', type:'minutes' },
    ],
    connectors: [
      { word:'wa',     label:'و',      type:'desc' },
      { word:'illa',   label:'إلا',    type:'desc' },
      { word:'nisf',   label:'النصف',  type:'minutes' },
      { word:'daqaiq', label:'دقائق',  type:'desc' },
    ],
    hours: ['الواحدة','الثانية','الثالثة','الرابعة','الخامسة','السادسة','السابعة','الثامنة','التاسعة','العاشرة','الحادية عشرة','الثانية عشرة'],
  },
};

// =============================================================================
// Time → words (verbatim per language for accuracy)
// =============================================================================

function timeWords(lang, hours, minutes) {
  const wH = HOURS[lang];
  const m5 = minutes - (minutes % 5);
  const h12 = hours > 0 ? hours : 12;
  const out = [];
  const add = (word, type) => out.push({ word, type });
  const wordAtH = off => wH[((h12 - 1 + off) % 12 + 12) % 12];

  if (lang === 'en') {
    add('it', 'desc'); add('is', 'desc');
    if (m5 === 0) { add(wordAtH(0), 'hours'); add('oclock', 'desc'); }
    else if (m5 === 5)  { add('five', 'minutes');                  add('past', 'desc'); add(wordAtH(0), 'hours'); }
    else if (m5 === 10) { add('ten', 'minutes');                   add('past', 'desc'); add(wordAtH(0), 'hours'); }
    else if (m5 === 15) { add('a', 'desc'); add('quarter', 'minutes'); add('past', 'desc'); add(wordAtH(0), 'hours'); }
    else if (m5 === 20) { add('twenty', 'minutes');                add('past', 'desc'); add(wordAtH(0), 'hours'); }
    else if (m5 === 25) { add('twentyfive', 'minutes');            add('past', 'desc'); add(wordAtH(0), 'hours'); }
    else if (m5 === 30) { add('half', 'minutes');                  add('past', 'desc'); add(wordAtH(0), 'hours'); }
    else if (m5 === 35) { add('twentyfive', 'minutes');            add('till', 'desc'); add(wordAtH(1), 'hours'); }
    else if (m5 === 40) { add('twenty', 'minutes');                add('till', 'desc'); add(wordAtH(1), 'hours'); }
    else if (m5 === 45) { add('a', 'desc'); add('quarter', 'minutes'); add('till', 'desc'); add(wordAtH(1), 'hours'); }
    else if (m5 === 50) { add('ten', 'minutes');                   add('till', 'desc'); add(wordAtH(1), 'hours'); }
    else if (m5 === 55) { add('five', 'minutes');                  add('till', 'desc'); add(wordAtH(1), 'hours'); }
  } else if (lang === 'de') {
    add('es', 'desc'); add('ist', 'desc');
    if (m5 === 0 && h12 % 12 === 1) { add('ein', 'hours'); add('uhr', 'desc'); }
    else if (m5 === 0)  { add(wordAtH(0), 'hours'); add('uhr', 'desc'); }
    else if (m5 === 5)  { add('fünf', 'minutes');    add('nach', 'desc'); add(wordAtH(0), 'hours'); }
    else if (m5 === 10) { add('zehn', 'minutes');    add('nach', 'desc'); add(wordAtH(0), 'hours'); }
    else if (m5 === 15) { add('viertel', 'minutes'); add('nach', 'desc'); add(wordAtH(0), 'hours'); }
    else if (m5 === 20) { add('zwanzig', 'minutes'); add('nach', 'desc'); add(wordAtH(0), 'hours'); }
    else if (m5 === 25) { add('fünf', 'minutes');    add('vor', 'desc'); add('halb', 'minutes'); add(wordAtH(1), 'hours'); }
    else if (m5 === 30) { add('halb', 'minutes');    add(wordAtH(1), 'hours'); }
    else if (m5 === 35) { add('fünf', 'minutes');    add('nach', 'desc'); add('halb', 'minutes'); add(wordAtH(1), 'hours'); }
    else if (m5 === 40) { add('zwanzig', 'minutes'); add('vor', 'desc'); add(wordAtH(1), 'hours'); }
    else if (m5 === 45) { add('viertel', 'minutes'); add('vor', 'desc'); add(wordAtH(1), 'hours'); }
    else if (m5 === 50) { add('zehn', 'minutes');    add('vor', 'desc'); add(wordAtH(1), 'hours'); }
    else if (m5 === 55) { add('fünf', 'minutes');    add('vor', 'desc'); add(wordAtH(1), 'hours'); }
  } else if (lang === 'fr') {
    add('il', 'desc'); add('est', 'desc');
    // French grammar wrinkles the canonical word-clock data mishandles:
    //   1. "midi" stands alone — "il est midi", never "il est midi heures".
    //   2. The hour 0 (and rollovers to it, e.g. 23:35) is "minuit", not "midi".
    //   3. One o'clock is singular: "il est une heure", not "une heures".
    // The dial's clock-face only places "midi" and "heures" (no minuit/heure
    // slots), so paintDial falls back: minuit → midi slot, heure → heures slot.
    const namedHour = (off) => (hours + off + 24) % 24;
    const hourWord  = (off) => {
      const w = wordAtH(off);
      return (w === 'midi' && namedHour(off) === 0) ? 'minuit' : w;
    };
    const heures = (off) => {
      const w = hourWord(off);
      if (w === 'midi' || w === 'minuit') return;
      add(w === 'une' ? 'heure' : 'heures', 'desc');
    };
    if (m5 === 0)        { add(hourWord(0), 'hours'); heures(0); }
    else if (m5 === 5)   { add(hourWord(0), 'hours'); heures(0); add('cinq', 'minutes'); }
    else if (m5 === 10)  { add(hourWord(0), 'hours'); heures(0); add('dix', 'minutes'); }
    else if (m5 === 15)  { add(hourWord(0), 'hours'); heures(0); add('et', 'desc'); add('quart', 'minutes'); }
    else if (m5 === 20)  { add(hourWord(0), 'hours'); heures(0); add('vingt', 'minutes'); }
    else if (m5 === 25)  { add(hourWord(0), 'hours'); heures(0); add('vingt-cinq', 'minutes'); }
    else if (m5 === 30)  { add(hourWord(0), 'hours'); heures(0); add('et', 'desc'); add('demie', 'minutes'); }
    else if (m5 === 35)  { add(hourWord(1), 'hours'); heures(1); add('moins', 'desc'); add('vingt-cinq', 'minutes'); }
    else if (m5 === 40)  { add(hourWord(1), 'hours'); heures(1); add('moins', 'desc'); add('vingt', 'minutes'); }
    else if (m5 === 45)  { add(hourWord(1), 'hours'); heures(1); add('moins', 'desc'); add('le', 'desc'); add('quart', 'minutes'); }
    else if (m5 === 50)  { add(hourWord(1), 'hours'); heures(1); add('moins', 'desc'); add('dix', 'minutes'); }
    else if (m5 === 55)  { add(hourWord(1), 'hours'); heures(1); add('moins', 'desc'); add('cinq', 'minutes'); }
  } else if (lang === 'it') {
    add('sono', 'desc'); add('le', 'desc');
    if (m5 === 0)        { add(wordAtH(0), 'hours'); add('inpunto', 'desc'); }
    else if (m5 === 5)   { add(wordAtH(0), 'hours'); add('e', 'desc'); add('cinque', 'minutes'); }
    else if (m5 === 10)  { add(wordAtH(0), 'hours'); add('e', 'desc'); add('dieci', 'minutes'); }
    else if (m5 === 15)  { add(wordAtH(0), 'hours'); add('e', 'desc'); add('un', 'desc'); add('quarto', 'minutes'); }
    else if (m5 === 20)  { add(wordAtH(0), 'hours'); add('e', 'desc'); add('venti', 'minutes'); }
    else if (m5 === 25)  { add(wordAtH(0), 'hours'); add('e', 'desc'); add('venticinque', 'minutes'); }
    else if (m5 === 30)  { add(wordAtH(0), 'hours'); add('e', 'desc'); add('mezza', 'minutes'); }
    else if (m5 === 35)  { add(wordAtH(1), 'hours'); add('meno', 'desc'); add('venticinque', 'minutes'); }
    else if (m5 === 40)  { add(wordAtH(1), 'hours'); add('meno', 'desc'); add('venti', 'minutes'); }
    else if (m5 === 45)  { add(wordAtH(1), 'hours'); add('meno', 'desc'); add('un', 'desc'); add('quarto', 'minutes'); }
    else if (m5 === 50)  { add(wordAtH(1), 'hours'); add('meno', 'desc'); add('dieci', 'minutes'); }
    else if (m5 === 55)  { add(wordAtH(1), 'hours'); add('meno', 'desc'); add('cinque', 'minutes'); }
  } else if (lang === 'es') {
    if ((m5 > 30 && h12 % 12 === 0 && hours === 12) || (m5 < 35 && h12 % 12 === 1 && hours === 1)) {
      add('es', 'desc'); add('la', 'desc');
    } else {
      add('son', 'desc'); add('las', 'desc');
    }
    if (m5 === 0)        { add(wordAtH(0), 'hours'); add('enpunto', 'desc'); }
    else if (m5 === 5)   { add(wordAtH(0), 'hours'); add('y', 'desc'); add('cinco', 'minutes'); }
    else if (m5 === 10)  { add(wordAtH(0), 'hours'); add('y', 'desc'); add('diez', 'minutes'); }
    else if (m5 === 15)  { add(wordAtH(0), 'hours'); add('y', 'desc'); add('cuarto', 'minutes'); }
    else if (m5 === 20)  { add(wordAtH(0), 'hours'); add('y', 'desc'); add('veinte', 'minutes'); }
    else if (m5 === 25)  { add(wordAtH(0), 'hours'); add('y', 'desc'); add('veinticinco', 'minutes'); }
    else if (m5 === 30)  { add(wordAtH(0), 'hours'); add('y', 'desc'); add('media', 'minutes'); }
    else if (m5 === 35)  { add(wordAtH(1), 'hours'); add('menos', 'desc'); add('veinticinco', 'minutes'); }
    else if (m5 === 40)  { add(wordAtH(1), 'hours'); add('menos', 'desc'); add('veinte', 'minutes'); }
    else if (m5 === 45)  { add(wordAtH(1), 'hours'); add('menos', 'desc'); add('cuarto', 'minutes'); }
    else if (m5 === 50)  { add(wordAtH(1), 'hours'); add('menos', 'desc'); add('diez', 'minutes'); }
    else if (m5 === 55)  { add(wordAtH(1), 'hours'); add('menos', 'desc'); add('cinco', 'minutes'); }
  } else if (lang === 'pt') {
    // Portuguese — modelled on Spanish. "São as" / "É a" for plural/singular.
    if (h12 % 12 === 1) { add('é', 'desc'); add('a', 'desc'); }
    else                { add('são', 'desc'); add('as', 'desc'); }
    if (m5 === 0)        { add(wordAtH(0), 'hours'); add('horas', 'desc'); }
    else if (m5 === 5)   { add(wordAtH(0), 'hours'); add('e', 'desc'); add('cinco', 'minutes'); }
    else if (m5 === 10)  { add(wordAtH(0), 'hours'); add('e', 'desc'); add('dez', 'minutes'); }
    else if (m5 === 15)  { add(wordAtH(0), 'hours'); add('e', 'desc'); add('quinze', 'minutes'); }
    else if (m5 === 20)  { add(wordAtH(0), 'hours'); add('e', 'desc'); add('vinte', 'minutes'); }
    else if (m5 === 25)  { add(wordAtH(0), 'hours'); add('e', 'desc'); add('vintecinco', 'minutes'); }
    else if (m5 === 30)  { add(wordAtH(0), 'hours'); add('e', 'desc'); add('meia', 'minutes'); }
    else if (m5 === 35)  { add(wordAtH(1), 'hours'); add('menos', 'desc'); add('vintecinco', 'minutes'); }
    else if (m5 === 40)  { add(wordAtH(1), 'hours'); add('menos', 'desc'); add('vinte', 'minutes'); }
    else if (m5 === 45)  { add(wordAtH(1), 'hours'); add('menos', 'desc'); add('quinze', 'minutes'); }
    else if (m5 === 50)  { add(wordAtH(1), 'hours'); add('menos', 'desc'); add('dez', 'minutes'); }
    else if (m5 === 55)  { add(wordAtH(1), 'hours'); add('menos', 'desc'); add('cinco', 'minutes'); }
  } else if (lang === 'nl') {
    // Dutch — half-hour anticipation. "Half drie" = 2:30.
    add('het', 'desc'); add('is', 'desc');
    if (m5 === 0)        { add(wordAtH(0), 'hours'); add('uur', 'desc'); }
    else if (m5 === 5)   { add('vijf', 'minutes');  add('over', 'desc'); add(wordAtH(0), 'hours'); }
    else if (m5 === 10)  { add('tien', 'minutes');  add('over', 'desc'); add(wordAtH(0), 'hours'); }
    else if (m5 === 15)  { add('kwart', 'minutes'); add('over', 'desc'); add(wordAtH(0), 'hours'); }
    else if (m5 === 20)  { add('tien', 'minutes');  add('voor', 'desc'); add('half', 'minutes'); add(wordAtH(1), 'hours'); }
    else if (m5 === 25)  { add('vijf', 'minutes');  add('voor', 'desc'); add('half', 'minutes'); add(wordAtH(1), 'hours'); }
    else if (m5 === 30)  { add('half', 'minutes'); add(wordAtH(1), 'hours'); }
    else if (m5 === 35)  { add('vijf', 'minutes');  add('over', 'desc'); add('half', 'minutes'); add(wordAtH(1), 'hours'); }
    else if (m5 === 40)  { add('tien', 'minutes');  add('over', 'desc'); add('half', 'minutes'); add(wordAtH(1), 'hours'); }
    else if (m5 === 45)  { add('kwart', 'minutes'); add('voor', 'desc'); add(wordAtH(1), 'hours'); }
    else if (m5 === 50)  { add('tien', 'minutes');  add('voor', 'desc'); add(wordAtH(1), 'hours'); }
    else if (m5 === 55)  { add('vijf', 'minutes');  add('voor', 'desc'); add(wordAtH(1), 'hours'); }
  } else if (lang === 'sv') {
    // Swedish — same half-hour anticipation as Dutch ("halv fyra" = 3:30).
    add('klockan', 'desc'); add('är', 'desc');
    if (m5 === 0)        { add(wordAtH(0), 'hours'); }
    else if (m5 === 5)   { add('fem', 'minutes');   add('över', 'desc'); add(wordAtH(0), 'hours'); }
    else if (m5 === 10)  { add('tio', 'minutes');   add('över', 'desc'); add(wordAtH(0), 'hours'); }
    else if (m5 === 15)  { add('kvart', 'minutes'); add('över', 'desc'); add(wordAtH(0), 'hours'); }
    else if (m5 === 20)  { add('tio', 'minutes');   add('i', 'desc');    add('halv', 'minutes'); add(wordAtH(1), 'hours'); }
    else if (m5 === 25)  { add('fem', 'minutes');   add('i', 'desc');    add('halv', 'minutes'); add(wordAtH(1), 'hours'); }
    else if (m5 === 30)  { add('halv', 'minutes'); add(wordAtH(1), 'hours'); }
    else if (m5 === 35)  { add('fem', 'minutes');   add('över', 'desc'); add('halv', 'minutes'); add(wordAtH(1), 'hours'); }
    else if (m5 === 40)  { add('tio', 'minutes');   add('över', 'desc'); add('halv', 'minutes'); add(wordAtH(1), 'hours'); }
    else if (m5 === 45)  { add('kvart', 'minutes'); add('i', 'desc');    add(wordAtH(1), 'hours'); }
    else if (m5 === 50)  { add('tio', 'minutes');   add('i', 'desc');    add(wordAtH(1), 'hours'); }
    else if (m5 === 55)  { add('fem', 'minutes');   add('i', 'desc');    add(wordAtH(1), 'hours'); }
  } else if (lang === 'uk') {
    // Ukrainian — feminine ordinal hours, і/без as past/to connectors.
    if (m5 === 0)        { add(wordAtH(0), 'hours'); }
    else if (m5 === 5)   { add(wordAtH(0), 'hours'); add('i', 'desc'); add('piat', 'minutes'); }
    else if (m5 === 10)  { add(wordAtH(0), 'hours'); add('i', 'desc'); add('desiat', 'minutes'); }
    else if (m5 === 15)  { add(wordAtH(0), 'hours'); add('i', 'desc'); add('chvert', 'minutes'); }
    else if (m5 === 20)  { add(wordAtH(0), 'hours'); add('i', 'desc'); add('dvadtsiat', 'minutes'); }
    else if (m5 === 25)  { add(wordAtH(0), 'hours'); add('i', 'desc'); add('dvadtsiatpiat', 'minutes'); }
    else if (m5 === 30)  { add(wordAtH(0), 'hours'); add('i', 'desc'); add('piv', 'minutes'); }
    else if (m5 === 35)  { add(wordAtH(1), 'hours'); add('bez', 'desc'); add('dvadtsiatpiat', 'minutes'); }
    else if (m5 === 40)  { add(wordAtH(1), 'hours'); add('bez', 'desc'); add('dvadtsiat', 'minutes'); }
    else if (m5 === 45)  { add(wordAtH(1), 'hours'); add('bez', 'desc'); add('chvert', 'minutes'); }
    else if (m5 === 50)  { add(wordAtH(1), 'hours'); add('bez', 'desc'); add('desiat', 'minutes'); }
    else if (m5 === 55)  { add(wordAtH(1), 'hours'); add('bez', 'desc'); add('piat', 'minutes'); }
  } else if (lang === 'ja') {
    // Japanese — hour-minute order, です at end. After half, the time is
    // read as "(next hour) - (60-min) 前" — N minutes before next hour.
    if (m5 === 0)        { add(wordAtH(0), 'hours'); add('desu', 'desc'); }
    else if (m5 === 5)   { add(wordAtH(0), 'hours'); add('go', 'minutes');    add('fun', 'desc'); add('desu', 'desc'); }
    else if (m5 === 10)  { add(wordAtH(0), 'hours'); add('ju', 'minutes');    add('fun', 'desc'); add('desu', 'desc'); }
    else if (m5 === 15)  { add(wordAtH(0), 'hours'); add('juugo', 'minutes'); add('fun', 'desc'); add('desu', 'desc'); }
    else if (m5 === 20)  { add(wordAtH(0), 'hours'); add('nijuu', 'minutes'); add('fun', 'desc'); add('desu', 'desc'); }
    else if (m5 === 25)  { add(wordAtH(0), 'hours'); add('nijuugo', 'minutes'); add('fun', 'desc'); add('desu', 'desc'); }
    else if (m5 === 30)  { add(wordAtH(0), 'hours'); add('han', 'minutes'); add('desu', 'desc'); }
    else if (m5 === 35)  { add(wordAtH(1), 'hours'); add('nijuugo', 'minutes'); add('fun', 'desc'); add('mae', 'desc'); add('desu', 'desc'); }
    else if (m5 === 40)  { add(wordAtH(1), 'hours'); add('nijuu', 'minutes'); add('fun', 'desc'); add('mae', 'desc'); add('desu', 'desc'); }
    else if (m5 === 45)  { add(wordAtH(1), 'hours'); add('juugo', 'minutes'); add('fun', 'desc'); add('mae', 'desc'); add('desu', 'desc'); }
    else if (m5 === 50)  { add(wordAtH(1), 'hours'); add('ju', 'minutes');    add('fun', 'desc'); add('mae', 'desc'); add('desu', 'desc'); }
    else if (m5 === 55)  { add(wordAtH(1), 'hours'); add('go', 'minutes');    add('fun', 'desc'); add('mae', 'desc'); add('desu', 'desc'); }
  } else if (lang === 'zh') {
    // Mandarin — 现在 + hour + minutes. After half: 差 + N分 + next hour.
    add('xianzai', 'desc');
    if (m5 === 0)        { add(wordAtH(0), 'hours'); }
    else if (m5 === 5)   { add(wordAtH(0), 'hours'); add('wu', 'minutes');     add('fen', 'desc'); }
    else if (m5 === 10)  { add(wordAtH(0), 'hours'); add('shi', 'minutes');    add('fen', 'desc'); }
    else if (m5 === 15)  { add(wordAtH(0), 'hours'); add('shiwu', 'minutes');  add('fen', 'desc'); }
    else if (m5 === 20)  { add(wordAtH(0), 'hours'); add('ershi', 'minutes');  add('fen', 'desc'); }
    else if (m5 === 25)  { add(wordAtH(0), 'hours'); add('ershiwu', 'minutes'); add('fen', 'desc'); }
    else if (m5 === 30)  { add(wordAtH(0), 'hours'); add('ban', 'minutes'); }
    else if (m5 === 35)  { add('cha', 'desc'); add('ershiwu', 'minutes'); add('fen', 'desc'); add(wordAtH(1), 'hours'); }
    else if (m5 === 40)  { add('cha', 'desc'); add('ershi', 'minutes');  add('fen', 'desc'); add(wordAtH(1), 'hours'); }
    else if (m5 === 45)  { add('cha', 'desc'); add('shiwu', 'minutes');  add('fen', 'desc'); add(wordAtH(1), 'hours'); }
    else if (m5 === 50)  { add('cha', 'desc'); add('shi', 'minutes');    add('fen', 'desc'); add(wordAtH(1), 'hours'); }
    else if (m5 === 55)  { add('cha', 'desc'); add('wu', 'minutes');     add('fen', 'desc'); add(wordAtH(1), 'hours'); }
  } else if (lang === 'ko') {
    // Korean — native-Korean hours + Sino-Korean minutes. 입니다 ends polite.
    // After half, "(next hour) (60-min) 분 전 입니다" — N minutes before next hour.
    if (m5 === 0)        { add(wordAtH(0), 'hours'); add('imnida', 'desc'); }
    else if (m5 === 5)   { add(wordAtH(0), 'hours'); add('o', 'minutes');     add('bun', 'desc'); add('imnida', 'desc'); }
    else if (m5 === 10)  { add(wordAtH(0), 'hours'); add('sip', 'minutes');   add('bun', 'desc'); add('imnida', 'desc'); }
    else if (m5 === 15)  { add(wordAtH(0), 'hours'); add('sipo', 'minutes');  add('bun', 'desc'); add('imnida', 'desc'); }
    else if (m5 === 20)  { add(wordAtH(0), 'hours'); add('isip', 'minutes');  add('bun', 'desc'); add('imnida', 'desc'); }
    else if (m5 === 25)  { add(wordAtH(0), 'hours'); add('isipo', 'minutes'); add('bun', 'desc'); add('imnida', 'desc'); }
    else if (m5 === 30)  { add(wordAtH(0), 'hours'); add('ban', 'minutes'); add('imnida', 'desc'); }
    else if (m5 === 35)  { add(wordAtH(1), 'hours'); add('isipo', 'minutes'); add('bun', 'desc'); add('jeon', 'desc'); add('imnida', 'desc'); }
    else if (m5 === 40)  { add(wordAtH(1), 'hours'); add('isip', 'minutes');  add('bun', 'desc'); add('jeon', 'desc'); add('imnida', 'desc'); }
    else if (m5 === 45)  { add(wordAtH(1), 'hours'); add('sipo', 'minutes');  add('bun', 'desc'); add('jeon', 'desc'); add('imnida', 'desc'); }
    else if (m5 === 50)  { add(wordAtH(1), 'hours'); add('sip', 'minutes');   add('bun', 'desc'); add('jeon', 'desc'); add('imnida', 'desc'); }
    else if (m5 === 55)  { add(wordAtH(1), 'hours'); add('o', 'minutes');     add('bun', 'desc'); add('jeon', 'desc'); add('imnida', 'desc'); }
  } else if (lang === 'ar') {
    // Arabic — ordinal feminine hours, و/إلا as past/to connectors. Uses
    // العشرون (twenty) as the 20-minute word; some dialects say الثلث (third)
    // — picking the modern colloquial form here for predictability.
    if (m5 === 0)        { add(wordAtH(0), 'hours'); }
    else if (m5 === 5)   { add(wordAtH(0), 'hours'); add('wa', 'desc'); add('khams', 'minutes'); add('daqaiq', 'desc'); }
    else if (m5 === 10)  { add(wordAtH(0), 'hours'); add('wa', 'desc'); add('ashr', 'minutes');  add('daqaiq', 'desc'); }
    else if (m5 === 15)  { add(wordAtH(0), 'hours'); add('wa', 'desc'); add('rub', 'minutes'); }
    else if (m5 === 20)  { add(wordAtH(0), 'hours'); add('wa', 'desc'); add('ishrun', 'minutes'); add('daqaiq', 'desc'); }
    else if (m5 === 25)  { add(wordAtH(0), 'hours'); add('wa', 'desc'); add('khamswaishrun', 'minutes'); add('daqaiq', 'desc'); }
    else if (m5 === 30)  { add(wordAtH(0), 'hours'); add('wa', 'desc'); add('nisf', 'minutes'); }
    else if (m5 === 35)  { add(wordAtH(1), 'hours'); add('illa', 'desc'); add('khamswaishrun', 'minutes'); add('daqaiq', 'desc'); }
    else if (m5 === 40)  { add(wordAtH(1), 'hours'); add('illa', 'desc'); add('ishrun', 'minutes'); add('daqaiq', 'desc'); }
    else if (m5 === 45)  { add(wordAtH(1), 'hours'); add('illa', 'desc'); add('rub', 'minutes'); }
    else if (m5 === 50)  { add(wordAtH(1), 'hours'); add('illa', 'desc'); add('ashr', 'minutes');  add('daqaiq', 'desc'); }
    else if (m5 === 55)  { add(wordAtH(1), 'hours'); add('illa', 'desc'); add('khams', 'minutes'); add('daqaiq', 'desc'); }
  }
  return { words: out };
}

root.WORD_TIME = {
  LANGUAGES: LANGUAGES,
  HOURS: HOURS,
  SUBJECT_PHRASE: SUBJECT_PHRASE,
  DIAL_LAYOUT: DIAL_LAYOUT,
  timeWords: timeWords,
};
})(typeof window !== "undefined" ? window : globalThis);
