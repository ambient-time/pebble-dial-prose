"""Generate compact serif runs from the bundled, pinned Cormorant fonts.

Copyright 2026 Luke Steuber. MIT License. Font outlines retain their OFL license.
"""
from pathlib import Path
import argparse, hashlib, json, subprocess
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent.parent
WORDS=['it is','five','ten','a quarter','twenty','twenty five','half','past','till',"o'clock",'one','two','three','four','five','six','seven','eight','nine','ten','eleven','twelve']
# Each watch shape has its own type size and vertical rhythm. No text wraps.
LAYOUTS=[
 {'width':144,'height':168,'sizes':(18,27,38),'top':(22,47,82,106),'exact_top':(38,65,111),'platforms':['BASALT','DIORITE','FLINT']},
 {'width':180,'height':180,'sizes':(20,31,43),'top':(23,50,89,116),'exact_top':(42,70,125),'platforms':['CHALK']},
 {'width':200,'height':228,'sizes':(25,38,53),'top':(32,65,115,150),'exact_top':(55,90,158),'platforms':['EMERY']},
 {'width':260,'height':260,'sizes':(29,44,60),'top':(38,79,131,168),'exact_top':(67,109,190),'platforms':['GABBRO']},
]

def load_font(size,italic=False):
 name='CormorantGaramond-Italic[wght].ttf' if italic else 'CormorantGaramond[wght].ttf'
 font=ImageFont.truetype(str(ROOT/'resources/fonts'/name),size)
 font.set_variation_by_axes([600])
 return font

def pack(image):
 levels=[min(3,(p+42)//85) for p in image.get_flattened_data()]
 runs=[];pos=0
 while pos<len(levels):
  level=levels[pos];end=pos+1
  while end<len(levels) and levels[end]==level and end-pos<64:end+=1
  runs.append((level<<6)|(end-pos-1));pos=end
 return runs

def build():
 provenance=json.loads((ROOT/'resources/fonts/provenance.json').read_text())
 for item in provenance['files']:
  assert hashlib.sha256((ROOT/'resources/fonts'/item['file']).read_bytes()).hexdigest()==item['sha256']
 source=json.loads(subprocess.check_output(['node',str(ROOT/'test/source.mjs')],text=True))
 header=['// Generated font bitmap data retains the SIL OFL. See resources/fonts/ for credits and licenses.\n#pragma once\n#include <stdint.h>\n#include <stddef.h>\ntypedef struct {uint32_t offset;uint16_t w,h;} ProseSprite;\ntypedef struct {int width,height;int top[4],exact_top[3];const ProseSprite *sprites;const uint8_t *data;} ProseLayout;\n']
 metadata=[]
 for index,layout in enumerate(LAYOUTS):
  sizes=layout['sizes'];data=[];sprites=[]
  for id,text in enumerate(WORDS):
   italic=id==0 or 7<=id<=9
   size=sizes[0] if italic else sizes[1] if id<=6 else sizes[2]
   font=load_font(size,italic)
   box=font.getbbox(text)
   # Shared vertical metrics keep each semantic role on the same baseline.
   group='it is past till oclock' if italic else ' '.join(WORDS[1:7] if id<=6 else WORDS[10:22])
   allbox=font.getbbox(group);box=(box[0],allbox[1],box[2],allbox[3])
   image=Image.new('L',(box[2]-box[0],box[3]-box[1]));ImageDraw.Draw(image).text((-box[0],-box[1]),text,font=font,fill=255)
   assert image.getbbox(),text
   encoded=pack(image);sprites.append([len(data),image.width,image.height]);data.extend(encoded)
  condition=' || '.join(['defined(PROSE_HOST)']+['defined(PBL_PLATFORM_'+p+')' for p in layout['platforms']])
  header.append('#if '+condition+'\n')
  header.append('static const uint8_t prose_data_'+str(index)+'[]={\n'+',\n'.join(','.join(map(str,data[i:i+32])) for i in range(0,len(data),32))+'\n};\n')
  header.append('static const ProseSprite prose_sprites_'+str(index)+'[]={'+','.join('{'+','.join(map(str,s))+'}' for s in sprites)+'};\n')
  fields=[str(layout['width']),str(layout['height']),'{'+','.join(map(str,layout['top']))+'}','{'+','.join(map(str,layout['exact_top']))+'}','prose_sprites_'+str(index),'prose_data_'+str(index)]
  header.append('static const ProseLayout prose_layout_'+str(index)+'={'+','.join(fields)+'};\n#endif\n')
  metadata.append({**layout,'bytes':len(data),'sprites':sprites})
 header.append('static const ProseLayout *prose_layout(int width,int height){\n')
 for index,l in enumerate(LAYOUTS):
  condition=' || '.join(['defined(PROSE_HOST)']+['defined(PBL_PLATFORM_'+p+')' for p in l['platforms']])
  header.append('#if '+condition+'\nif(width=='+str(l['width'])+'&&height=='+str(l['height'])+')return &prose_layout_'+str(index)+';\n#endif\n')
 header.append('return NULL;\n}\n')
 source.update({'words':WORDS,'layouts':metadata})
 return ''.join(header),json.dumps(source,indent=2)+'\n'

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
 header,oracle=build()
 for name,text in [('src/c/assets.h',header),('test/oracle.json',oracle)]:
  path=ROOT/name
  if args.check:assert path.read_text()==text,name+' is stale; run make assets'
  else:path.write_text(text)
 if not args.check:
  icon=Image.new('1',(25,25));d=ImageDraw.Draw(icon);font=load_font(23);box=font.getbbox('p');d.text(((25-(box[2]-box[0]))//2-box[0],(25-(box[3]-box[1]))//2-box[1]),'p',font=font,fill=1);icon.save(ROOT/'resources/images/menu-icon.png')
 print('Pinned serif assets verified' if args.check else 'Generated four native serif layouts')
if __name__=='__main__':main()
