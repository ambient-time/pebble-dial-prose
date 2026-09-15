"""Rasterize source-language runs into bounded native resources. Luke Steuber, MIT.
Run with requirements.txt. Arabic is shaped before rasterization; fonts retain OFL.
"""
from pathlib import Path
import json,subprocess,sys,math,struct,hashlib,shutil,os,zlib
from PIL import Image,ImageDraw,ImageFont
from fontTools.ttLib import TTFont
from fontTools import subset
import arabic_reshaper
from bidi.algorithm import get_display
ROOT=Path(sys.argv[1]).resolve();PROSE=json.loads((ROOT/'package.json').read_text())['name']=='dial-prose';HERE=Path(__file__).resolve().parent
SOURCE=ROOT/'test/multilingual-source.mjs'
if not SOURCE.exists():shutil.copyfile(HERE/'source.mjs',SOURCE)
data=json.loads(subprocess.check_output(['node',str(SOURCE),str(ROOT)],text=True))
LANGS=data['languages'];FONTS=ROOT/'resources/fonts/multilingual';FONTS.mkdir(exist_ok=True)
fonts_dir=Path(os.environ['PEBBLE_LANGUAGE_FONTS']) if 'PEBBLE_LANGUAGE_FONTS' in os.environ else None
font_names={'ja':'NotoSansJP.otf','ko':'NotoSansKR.otf','zh':'NotoSansSC.otf','ar':'NotoNaskhArabic.ttf'}
def shaped(s,lang):return get_display(arabic_reshaper.reshape(s)) if lang=='ar' else s
# Preserve text and grammatical role independently of raster data.
(ROOT/'test/multilingual-source.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
fontproof={}
for lang in LANGS:
 if lang not in font_names:continue
 name=font_names[lang];dst=FONTS/name
 if not dst.exists():
  if fonts_dir is None:raise RuntimeError('Missing bundled subset font '+name+'; set PEBBLE_LANGUAGE_FONTS to the documented upstream font directory to bootstrap.')
  src=fonts_dir/name;f=TTFont(src);chars=set()
  for p in data['phrases'][lang]:
   for line in p['lines']:chars.update(shaped(line['text'],lang))
   for w in p['words']:chars.update(shaped(w['word'],lang))
  for group in ['minutes','connectors','articles']:
   for w in data['layout'][lang].get(group,[]):chars.update(shaped(w['label'],lang))
  for h in data['layout'][lang]['hours']:chars.update(shaped(h,lang))
  chars.update(shaped(data['subject'][lang],lang));chars.update(' ')
  opt=subset.Options();opt.layout_features=['*'];sub=subset.Subsetter(options=opt);sub.populate(text=''.join(chars));sub.subset(f)
  for n in f['name'].names:
   if n.nameID in [1,4,6]:n.string=('AmbientTime '+lang if n.nameID!=6 else 'AmbientTime-'+lang).encode(n.getEncoding())
  f.save(dst);fontproof[lang]={'upstreamSHA256':hashlib.sha256(src.read_bytes()).hexdigest(),'subsetSHA256':hashlib.sha256(dst.read_bytes()).hexdigest(),'upstream':name,'subset':'Required source glyphs and Arabic presentation forms; renamed AmbientTime '+lang}
  shutil.copyfile(fonts_dir/('OFL-Arabic.txt' if lang=='ar' else 'OFL-CJK.txt'),FONTS/('OFL-Arabic.txt' if lang=='ar' else 'OFL-CJK.txt'))
if fontproof:(FONTS/'provenance.json').write_text(json.dumps(fontproof,indent=2)+'\n')
cache={}
def raster(text,size,lang,role):
 key=(text,size,lang,role)
 if key in cache:return cache[key]
 if lang in font_names:path=FONTS/font_names[lang]
 elif PROSE:path=ROOT/'resources/fonts'/('CormorantGaramond-Italic[wght].ttf' if role=='desc' else 'CormorantGaramond[wght].ttf')
 else:path=ROOT/'resources/fonts/NotoSans-Bold.ttf'
 f=ImageFont.truetype(str(path),max(6,size))
 if PROSE and lang not in font_names:f.set_variation_by_axes([600])
 text=shaped(text,lang);cmap=TTFont(path).getBestCmap() if str(path) not in cache else cache[str(path)];cache[str(path)]=cmap
 assert all(ord(c) in cmap or c=='\n' for c in text),(lang,text,'missing font glyph')
 lines=text.split('\n');boxes=[f.getbbox(s) for s in lines];width=max(max(1,b[2]-b[0]) for b in boxes);heights=[max(1,b[3]-b[1]) for b in boxes];height=sum(heights)+max(0,len(lines)-1)*2
 im=Image.new('L',(width,height));draw=ImageDraw.Draw(im);y=0
 for s,b,h in zip(lines,boxes,heights):draw.text(((width-(b[2]-b[0]))/2-b[0],y-b[1]),s,font=f,fill=255);y+=h+2
 assert im.getbbox(),(lang,text);cache[key]=im;return im

def pack(im):
 vals=[min(3,(v+42)//85) for v in im.get_flattened_data()];out=bytearray();i=0
 while i<len(vals):
  j=i+1
  while j<len(vals) and vals[j]==vals[i] and j-i<64:j+=1
  out.append(vals[i]*64+j-i-1);i=j
 return out

def inside(w,h,x,y,pad=1):
 if x<pad or y<pad or x>=w-pad or y>=h-pad:return False
 return w!=h or (2*x+1-w)**2+(2*y+1-h)**2<=(w-2*pad)**2

def fits(w,h,x,y,im,pad=1):return all(inside(w,h,xx,yy,pad) for xx in [x,x+im.width-1] for yy in [y,y+im.height-1])

sizes=[(144,168,['basalt','diorite','flint']),(180,180,['chalk']),(200,228,['emery']),(260,260,['gabbro'])] if PROSE else [(180,180,['chalk']),(260,260,['gabbro'])]
declared=set(json.loads((ROOT/'package.json').read_text())['pebble']['targetPlatforms'])
sizes=[(w,h,[t for t in targets if t in declared]) for w,h,targets in sizes if declared.intersection(targets)]
resources=[];proof=[]
for w,h,targets in sizes:
 for lang in LANGS[1:]:
  sprites=[];lookup={};blob=bytearray();frames=[];info=[]
  def sprite(im,text,role,x=0,y=0):
   key=(text,role,im.size,im.tobytes(),x,y)
   if key in lookup:return lookup[key]
   encoded=pack(im);i=len(sprites);lookup[key]=i;sprites.append((len(blob),len(encoded),im.width,im.height,x,y,170 if role=='desc' else 255,{'subject':0,'hours':1,'hours-alt':129,'desc-alt':130,'subject-alt':128}.get(role,2)));blob.extend(encoded);return i
  if PROSE:
   for p in data['phrases'][lang]:
    lines=p['lines'];n=len(lines);assert 1<=n<=6
    # Fit complete shaped runs as a stack; shrink only this phrase when necessary.
    for scale in range(100,54,-1):
     ims=[];pts=[];font_sizes=[]
     for ln in lines:
      base=23 if ln['type']=='desc' else 33 if ln['type']=='minutes' else 42
      fs=round(base*(w/180)*scale/100);text=ln['text'];im=raster(text,fs,lang,ln['type'])
      if im.width>w-12 and ' ' in text:
       words=text.split(' ');choices=[' '.join(words[:i])+'\n'+' '.join(words[i:]) for i in range(1,len(words))];text=min(choices,key=lambda t:raster(t,fs,lang,ln['type']).width);im=raster(text,fs,lang,ln['type'])
      while im.width>w-12 and fs>12:fs-=1;im=raster(text,fs,lang,ln['type'])
      ims.append(im);font_sizes.append(fs)
     gap=max(5,round(h*.045));total=sum(im.height for im in ims)+(n-1)*gap;y=(h-total)//2
     for im in ims:pts.append(((w-im.width)//2,y));y+=im.height+gap
     if all(fits(w,h,x,y,im,4) for (x,y),im in zip(pts,ims)):break
    else:raise AssertionError((lang,p,'cannot fit'))
    frame=[]
    for ln,im,(x,y) in zip(lines,ims,pts):frame.append((sprite(im,ln['text'],ln['type']),x,y))
    frames.append(bytes([n])+b''.join(struct.pack('<Hhh',*t) for t in frame)+bytes((6-n)*6))
    info.append({'hour':p['hour'],'minute':p['minute'],'fontSizes':font_sizes,'placements':[list(t) for t in frame]})
  else:
   layout=data['layout'][lang];tokens=[];centers=[]
   for i,text in enumerate(layout['hours']):
    angle=(i+1)*math.pi/6-math.pi/2;tokens.append({'word':text,'label':text,'type':'hours'});centers.append((50+42*math.cos(angle),50+42*math.sin(angle)))
   for group in ['minutes','connectors','articles']:
    items=layout.get(group,[])
    for i,t in enumerate(items):
     if group=='articles':x,y=50,17
     else:
      a=(i+.5)/len(items)*math.pi+(math.pi if group=='minutes' else 0);x,y=50+28*math.cos(a),50+24*math.sin(a)
     tokens.append(t);centers.append((x,y))
   # Fit every label inside the circular canvas; keep hours in clock order.
   for t,(cx,cy) in zip(tokens,centers):
    fs=round((12 if t['type']=='hours' else 10)*w/180);im=raster(t['label'],fs,lang,t['type']);x=round(cx*w/100-im.width/2);y=round(cy*h/100-im.height/2)
    while not fits(w,h,x-2,y-2,Image.new('L',(im.width+4,im.height+4)),2):
     cx=50+(cx-50)*.97;cy=50+(cy-50)*.97;x=round(cx*w/100-im.width/2);y=round(cy*h/100-im.height/2)
    sprite(im,t['label'],t['type'],x,y)
   subj=data['subject'][lang];subj_im=raster(subj.replace(' ','\n') if lang!='ar' else subj,round(10*w/180),lang,'subject');sprite(subj_im,subj,'subject',(w-subj_im.width)//2,(h-subj_im.height)//2)
   keys=[t['word']+'|'+t['type'] for t in tokens]
   aliases={'de':[('ein','hours','eins')],'fr':[('minuit','hours','midi'),('heure','desc','heures')]}.get(lang,[])
   for word,role,original in aliases:
    original_id=keys.index(original+'|'+role);base=sprites[original_id];fs=round((12 if role=='hours' else 10)*w/180);im=raster(word,fs,lang,role);x=base[4]+base[2]//2-im.width//2;y=base[5]+base[3]//2-im.height//2
    sprite(im,word,role+'-alt',x,y);keys.append(word+'|'+role)
   subject_alt={'es':'es la','pt':'é a'}.get(lang)
   alt_id=None
   if subject_alt:
    im=raster(subject_alt.replace(' ','\n'),round(10*w/180),lang,'subject');alt_id=sprite(im,subject_alt,'subject-alt',(w-im.width)//2,(h-im.height)//2)
   # Subject occupies a resource sprite but is not part of the token-key list.
   token_ids=list(range(len(tokens)))+list(range(len(tokens)+1,len(tokens)+1+len(aliases)))
   for p in data['phrases'][lang]:
    ids=[]
    for t in p['words']:
     key=t['word']+'|'+t['type']
     if key in keys:ids.append(token_ids[keys.index(key)])
     elif subject_alt and t['word'] in subject_alt.split(' '):
      if alt_id not in ids:ids.append(alt_id)
     else:assert t['word'] in subj.split(' '),(lang,t,'unplaced source token')
    assert len(ids)<=8;frames.append(bytes([len(ids)])+b''.join(struct.pack('<H',i) for i in ids)+bytes((8-len(ids))*2))
   info={'tokens':tokens,'placements':[list(s[2:6]) for s in sprites]}
  assert len(frames)==288
  framebytes=b''.join(frames);spriteoff=20+len(framebytes);dataoff=spriteoff+len(sprites)*18
  header=struct.pack('<4sHHHHII',b'ML01',w,h,len(sprites),1 if PROSE else 2,spriteoff,dataoff)
  records=b''.join(struct.pack('<IIHHhhBB',off,length,sw,sh,x,y,ink,role) for off,length,sw,sh,x,y,ink,role in sprites)
  resource=header+framebytes+records+blob
  if PROSE:
   blocks=[zlib.compress(resource[i:i+8192],9)[2:-4] for i in range(0,len(resource),8192)]
   offsets=[28+4*(len(blocks)+1)]
   for block in blocks:offsets.append(offsets[-1]+len(block))
   resource=b'MZ01'+header[4:]+struct.pack('<IHH',len(resource),8192,len(blocks))+b''.join(struct.pack('<I',v) for v in offsets)+b''.join(blocks)
  folder=ROOT/'resources/languages' ;folder.mkdir(exist_ok=True);name=f'{lang}-{w}.bin';(folder/name).write_bytes(resource)
  resources.append({'type':'raw','name':'LANG_'+lang.upper(),'file':'languages/'+name,'targetPlatforms':targets});proof.append({'language':lang,'width':w,'height':h,'bytes':len(resource),'sha256':hashlib.sha256(resource).hexdigest(),'sprites':len(sprites),'frames':info})
(ROOT/'test/multilingual-layouts.json').write_text(json.dumps(proof,ensure_ascii=False,separators=(',',':'))+'\n')
p=ROOT/'package.json';pkg=json.loads(p.read_text());pkg['pebble']['resources']['media']=[r for r in pkg['pebble']['resources']['media'] if not r['name'].startswith('LANG_')]+resources;p.write_text(json.dumps(pkg,indent=2)+'\n')
(ROOT/'src/c/language-resources.h').write_text('// Generated stable language order. Luke Steuber, MIT.\n#pragma once\n#define LANGUAGE_COUNT '+str(len(LANGS))+'\nstatic const uint32_t language_resources[]={0,'+','.join('RESOURCE_ID_LANG_'+l.upper() for l in LANGS[1:])+'};\n')
print(ROOT.name,len(LANGS),'languages',sum(p['bytes'] for p in proof),'bytes across target layouts',flush=True)
