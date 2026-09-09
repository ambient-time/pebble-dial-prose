"""Validate, freeze and independently build one Pebble draft."""
import hashlib,json,shutil,subprocess,sys,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
pkg=json.loads((ROOT/'package.json').read_text());slug=pkg['name'];version=pkg['version']
platforms=set(pkg['pebble']['targetPlatforms'])
assert platforms and platforms <= {'basalt','chalk','diorite','emery','flint','gabbro'}
pbw=ROOT/'build'/f'{ROOT.name}.pbw';digest=sha(pbw)
with zipfile.ZipFile(pbw) as z:
 assert z.testzip() is None
 info=json.loads(z.read('appinfo.json'))
 assert info['uuid']==pkg['pebble']['uuid'] and info['versionLabel']==version
 assert set(info['targetPlatforms'])==platforms
 assert info['appKeys']=={'LANGUAGE':0} and info['capabilities']==['configurable']
 assert 'pebble-js-app.js' in z.namelist()
 for target in platforms:
  m=json.loads(z.read(target+'/manifest.json'))
  for part in ['application','resources']:
   assert len(z.read(target+'/'+m[part]['name']))==m[part]['size']
   if part=='resources':assert m[part]['size']<=262144, 'Store resource budget exceeded'
evidence=ROOT/'evidence';evidence.mkdir(exist_ok=True)
for target in sorted(platforms):
 report=json.loads((ROOT/f'build/evidence/{target}-report.json').read_text())
 assert report['pbwSHA256']==digest
 assert report['naturalNoonRollover'] and report['naturalMidnightRollover']
 assert not any(any(term in line.lower() for term in ['crash','fault','allocation failed','unavailable']) for line in report['logs'])
 assert report['languagePersistence'] and report['invalidLanguagesRejected']
 assert report['languageChoices']==len(json.loads((ROOT/'test/multilingual-source.json').read_text())['languages'])
 frames=[]
 for file in report['frames']:
  p=ROOT/file
  if p.stem.endswith('-boot'):continue
  shutil.copy2(p,evidence/p.name);frames.append('evidence/'+p.name)
 report['frames']=frames;(evidence/f'{target}-report.json').write_text(json.dumps(report,indent=2)+'\n')
(evidence/'validation.json').write_text(json.dumps({'pbwSHA256':digest,'version':version,'targets':sorted(platforms),'nativeChecks':'Passed declared-target rollover and capture checks','physicalValidation':'Not performed'},indent=2)+'\n')
shutil.copy2(ROOT/'build/languages/validation.json',evidence/'languages-validation.json')
out=ROOT/'release';out.mkdir(exist_ok=True);artifact=out/f'{slug}-{version}.pbw';shutil.copy2(pbw,artifact)
archive=out/f'{slug}-{version}-source.zip'
files=[ROOT/n for n in ['package.json','package-lock.json','wscript','Makefile','README.md','LICENSE','.gitignore','.gitattributes'] if (ROOT/n).is_file()]
for directory in ['src','resources','reference','test','tools']:
 files.extend(p for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(files):z.write(p,p.relative_to(ROOT))
 assert z.testzip() is None
with tempfile.TemporaryDirectory(prefix=slug+'-portable-') as tmp:
 target=Path(tmp)/slug;target.mkdir()
 with zipfile.ZipFile(archive) as z:z.extractall(target)
 with (evidence/'independent-build.log').open('w') as log:
  subprocess.run(['make','test'],cwd=target,stdout=log,stderr=subprocess.STDOUT,check=True)
  subprocess.run([str(Path.home()/'.local/bin/pebble'),'build','--sdk','4.33.1'],cwd=target,stdout=log,stderr=subprocess.STDOUT,check=True)
 with zipfile.ZipFile(target/'build'/f'{slug}.pbw') as z:
  assert z.testzip() is None
  built=json.loads(z.read('appinfo.json'));assert built['uuid']==info['uuid'] and built['versionLabel']==version
  assert set(built['targetPlatforms'])==platforms
  with zipfile.ZipFile(pbw) as original:
   assert original.read('pebble-js-app.js')==z.read('pebble-js-app.js'), 'Phone bundle changed'
   for platform in platforms:
    assert original.read(platform+'/app_resources.pbpack')==z.read(platform+'/app_resources.pbpack'), 'Resource payload changed'
    a=bytearray(original.read(platform+'/pebble-app.bin'));b=bytearray(z.read(platform+'/pebble-app.bin'))
    for offset,count in [(0x14,4),(0x7c,4),(0x94,20)]:a[offset:offset+count]=b[offset:offset+count]=bytes(count)
    assert a==b, 'Native code changed outside CRC resource timestamp and GNU build ID'
 report={'sourceArchive':archive.name,'archiveSHA256':sha(archive),'independentPBWSHA256':sha(target/'build'/f'{slug}.pbw'),'targets':sorted(platforms),'buildOutsideSourceTree':'passed','note':'Canonical PBW is the binary tied to native captures.'}
(evidence/'independent-build.json').write_text(json.dumps(report,indent=2)+'\n')
p=evidence/'independent-build.log';p.write_text('\n'.join(l.rstrip() for l in p.read_text().splitlines())+'\n')
(out/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.name}\n' for p in sorted(out.glob('*.pbw'))+sorted(out.glob('*-source.zip'))))
print(slug,digest,'portable build passed')
