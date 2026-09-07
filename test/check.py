"""Exhaustive independent grammar, layout and native rendering checks.

Copyright 2026 Luke Steuber. MIT License.
"""
from pathlib import Path
import json,subprocess,sys
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
subprocess.run([sys.executable,str(ROOT/'test/generate.py'),'--check'],check=True)
output=ROOT/'build/host';output.mkdir(parents=True,exist_ok=True);exe=output/'render'
subprocess.run(['cc','-std=c11','-g','-DPROSE_HOST','-fsanitize=address,undefined','-Wall','-Wextra','-Werror',str(ROOT/'test/host.c'),str(ROOT/'src/c/prose.c'),'-o',str(exe)],check=True)
actual=[line.split('|') for line in subprocess.check_output([str(exe),'phrases'],text=True).splitlines()]
oracle=json.loads(subprocess.check_output(['node',str(ROOT/'test/source.mjs')],text=True))
assert actual==[[p['time'],p['sentence']] for p in oracle['phrases']], 'C phrase/exact time differs from the pinned source'
# Exact-time output advances every minute; prose changes only at five-minute boundaries.
for i,(time,sentence) in enumerate(actual):
 assert time==f'{i//60:02d}:{i%60:02d}'
 if i%5:assert sentence==actual[i-1][1],(i,'premature phrase change')
 elif i:assert sentence!=actual[i-1][1],(i,'missing five-minute rollover')
assert actual[0][1]=='it is twelve o\'clock'
assert actual[34][1]=='it is half past twelve'
assert actual[35][1]=='it is twenty five till one'
assert actual[1439][1]=='it is five till twelve'
# Test all 7,200 layouts through the production renderer under sanitizers.
subprocess.run([str(exe),'exhaustive'],check=True)
poses=[(10,8,'hero'),(3,15,'quarter'),(7,25,'twentyfive'),(10,35,'eleven-till'),(6,45,'seven-quarter'),(12,0,'noon'),(23,59,'before-midnight'),(0,0,'midnight')]
for width,height,mono in [(144,168,0),(144,168,1),(180,180,0),(200,228,0),(260,260,0)]:
 for h,m,name in poses:
  path=output/f'{width}-{mono}-{name}.pgm';subprocess.run([str(exe),str(width),str(height),str(h),str(m),str(mono),str(path)],check=True);Image.open(path).save(path.with_suffix('.png'))
print('Dial Prose: all 1440 source phrases and exact times, all rollovers, and 7200 bounded sanitized renders passed')
