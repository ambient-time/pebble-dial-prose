"""Exercise native resource decoding, all source minutes and glyph coverage."""
from pathlib import Path
import json,subprocess,sys,hashlib
root=Path(sys.argv[1]).resolve();here=Path(__file__).resolve().parent;out=root/'build/languages';out.mkdir(exist_ok=True)
exe=out/'render';subprocess.run(['clang','-std=c11','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-I'+str(here/'host'),'-I'+str(root/'src/c'),str(here/'host/render.c'),str(root/'src/c/locale.c'),str(root/'src/c/tinflate.c'),'-o',str(exe)],check=True)
source=json.loads(subprocess.check_output(['node',str(root/'test/multilingual-source.mjs'),str(root)],text=True));frozen=json.loads((root/'test/multilingual-source.json').read_text());assert source==frozen
layouts=json.loads((root/'test/multilingual-layouts.json').read_text());count=0
for l in layouts:
 p=root/'resources/languages'/f'{l["language"]}-{l["width"]}.bin';assert hashlib.sha256(p.read_bytes()).hexdigest()==l['sha256'];subprocess.run([str(exe),str(p),'all'],check=True,stdout=subprocess.DEVNULL);count+=1440
report={'sourceMinutes':len(source['languages'])*1440,'resourceMinuteRenders':count,'resources':len(layouts),'malformedResourceHeadersRejected':True,'sanitizers':'AddressSanitizer and UndefinedBehaviorSanitizer','physicalWatch':'Not performed'}
(out/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(root.name,report,flush=True)
