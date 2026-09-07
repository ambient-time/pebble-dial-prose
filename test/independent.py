"""Rebuild the delivered source ZIP and compare native payloads.
Copyright 2026 Luke Steuber. MIT License.
"""
import datetime,hashlib,json,struct,subprocess,sys,tempfile,zipfile
from pathlib import Path
from libpebble2.util.stm32_crc import crc32
ROOT=Path(__file__).resolve().parent.parent
def sha(data):return hashlib.sha256(data).hexdigest()
def normalize(data):
 assert data[:6]==b'PBLAPP';size=struct.unpack_from('<H',data,0x0e)[0]
 assert crc32(data[0x82:size])==struct.unpack_from('<I',data,0x14)[0]
 assert data[0x84:0x94]==struct.pack('<III',4,20,3)+b'GNU\0'
 out=bytearray(data)
 for offset,count in [(0x14,4),(0x7c,4),(0x94,20)]:out[offset:offset+count]=bytes(count)
 return bytes(out)
def main():
 package=json.loads((ROOT/'package.json').read_text());slug=package['name'];version=package['version'];archive=ROOT/'release'/f'{slug}-{version}-source.zip';pbw=ROOT/'release'/f'{slug}-{version}.pbw';evidence=ROOT/'evidence';evidence.mkdir(exist_ok=True)
 report={'sourceZipSHA256':sha(archive.read_bytes()),'productionPBWSHA256':sha(pbw.read_bytes()),'result':'incomplete'}
 (evidence/'independent-build.json').write_text(json.dumps(report,indent=2)+'\n')
 with tempfile.TemporaryDirectory(prefix=slug+'-source-') as temp:
  # Different checkout folder proves package-name independence.
  checkout=Path(temp)/'imported-source';checkout.mkdir()
  with zipfile.ZipFile(archive) as z:
   assert z.testzip() is None;assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist());z.extractall(checkout)
  log=[]
  for command in [['make','test','PYTHON='+sys.executable],['make','build','PYTHON='+sys.executable]]:
   run=subprocess.run(command,cwd=checkout,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);log.append(run.stdout);(evidence/'independent-build.log').write_text('\n'.join(log));assert run.returncode==0,'Unpacked source failed; inspect independent-build.log'
  rebuilt=checkout/'build/imported-source.pbw';checks={}
  with zipfile.ZipFile(pbw) as a,zipfile.ZipFile(rebuilt) as b:
   assert json.loads(a.read('appinfo.json'))==json.loads(b.read('appinfo.json'))
   for target in package['pebble']['targetPlatforms']:
    old=a.read(target+'/pebble-app.bin');new=b.read(target+'/pebble-app.bin');assert normalize(old)==normalize(new),target+' executable changed'
    resources=a.read(target+'/app_resources.pbpack');assert resources==b.read(target+'/app_resources.pbpack'),target+' resources changed'
    checks[target]={'codeIdenticalOutsideCRCResourceTimestampAndGNUBuildID':True,'resourcesIdentical':True,'resourceSHA256':sha(resources),'changedBinaryByteOffsets':[i for i,(x,y) in enumerate(zip(old,new)) if x!=y]}
  report.update({'result':'passed','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'independentPBWSHA256':sha(rebuilt.read_bytes()),'sdk':'4.33.1','hostTestsPassed':True,'allDeclaredTargetsBuilt':True,'payloadChecks':checks,'limits':'Independent local source ZIP build. Physical-watch and publication evidence are separate.'})
 (evidence/'independent-build.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
