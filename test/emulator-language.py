"""Native Dial Prose screenshots; isolated persistent profiles, no physical watches.

Run with the installed pebble-tool Python after make test and pebble build.
Copyright 2026 Luke Steuber. MIT License.
"""
import argparse
import datetime
import hashlib
import json
import re
import os
from pathlib import Path
import time
import tempfile
import subprocess
from uuid import UUID
from types import SimpleNamespace

SDK=Path.home()/'Library/Application Support/Pebble SDK/SDKs/4.33.1'
toolchain=str(SDK.resolve()/'toolchain/bin')
os.environ.setdefault('PEBBLE_QEMU_PATH',toolchain+'/qemu-pebble')
os.environ['PATH']=toolchain+os.pathsep+os.environ['PATH']
import png
from pebble_tool.commands.screenshot import ScreenshotCommand
from pebble_tool.commands.install import ToolAppInstaller
from libpebble2.protocol.apps import AppRunState,AppRunStateStart,AppRunStateStop
from libpebble2.services.appmessage import AppMessageService, Int32, CString
from libpebble2.protocol.logs import AppLogMessage,AppLogShippingControl
import pebble_tool.sdk.emulator as emulator
from libpebble2.communication.transports.qemu.protocol import QemuButton
from pebble_tool.commands.emucontrol import send_data_to_qemu

ROOT=Path(__file__).resolve().parent.parent
PBW=ROOT/'build'/f'{ROOT.name}.pbw' # The SDK uses the checkout folder's name.
APP=UUID(json.loads((ROOT/'package.json').read_text())['pebble']['uuid'])

def run(platform,fresh=False):
    installed_sha=hashlib.sha256(PBW.read_bytes()).hexdigest()
    oracle=json.loads((ROOT/'test/oracle.json').read_text())
    parity=[]
    out=ROOT/'build/evidence';out.mkdir(exist_ok=True)
    state=Path(tempfile.mkdtemp(prefix='emulator-fresh-',dir=ROOT/'build')) if fresh else ROOT/'build/emulator-state'
    state.mkdir(exist_ok=True)
    def persist(target,version=None):
        p=state/target;p.mkdir(exist_ok=True);return str(p)
    emulator.get_sdk_persist_dir=persist
    emulator.get_emulator_info_path=lambda:str(state/'emulators.json')
    emulator.get_default_account=lambda:SimpleNamespace(is_logged_in=False)
    bridge_log=(out/f'{platform}-bridge.log').open('w')
    emulator.ManagedEmulatorTransport._get_output=lambda self:bridge_log
    cmd=ScreenshotCommand();cmd._set_debugging(0)
    def shutdown():
        info=emulator.get_emulator_info(platform,'4.33.1')
        if info:
            for key in ('qemu','pypkjs','websockify'):
                pid=info.get(key,{}).get('pid')
                if not pid:continue
                process=subprocess.run(['ps','-p',str(pid),'-o','command='],capture_output=True,text=True)
                if process.returncode==0 and str(state/platform) not in process.stdout:
                    raise RuntimeError(f'Refusing to stop PID {pid}: outside this test profile')
        cmd._shutdown_platform_emulator(platform,'4.33.1')
    shutdown()
    try:
        watch=cmd._connect_emulator(platform,'4.33.1');cmd.pebble=watch
    except BaseException:
        shutdown();bridge_log.close();raise
    language=0
    logs=[];frames=[]
    def log(packet):logs.append(str(packet.message));print(str(packet.message),flush=True)
    handle=watch.register_endpoint(AppLogMessage,log)
    watch.send_packet(AppLogShippingControl(enable=True))
    args=argparse.Namespace(no_correction=True,scale=1,no_open=True,v=0)
    source=json.loads((ROOT/'test/multilingual-source.json').read_text());languages=source['languages']
    layout_proof=json.loads((ROOT/'test/multilingual-layouts.json').read_text())
    def grab(name,clock=None):
        if clock:
            h,m,s=clock;target=datetime.datetime.now().replace(hour=h,minute=m,second=s,microsecond=0)
            watch.send_packet(AppRunState(data=AppRunStateStop(uuid=APP)))
            time.sleep(.15);cmd._set_time(watch,target)
            start=len(logs);watch.send_packet(AppRunState(data=AppRunStateStart(uuid=APP)))
            expected=f'time={h:02d}:{m:02d}:'
            deadline=time.monotonic()+4
            while not any(expected in l for l in logs[start:]) and time.monotonic()<deadline:time.sleep(.03)
            assert any(expected in l for l in logs[start:]),'Native target minute not rendered'
            # Window startup can request several redraws before the first frame settles.
            time.sleep(1.1)
        pixels=cmd._grab_processed_image(args,show_progress=False)
        file=out/f'{platform}-{name}.png';png.from_array(pixels,mode='RGBA;8').save(str(file));frames.append(str(file.relative_to(ROOT)))
        if clock:
            from PIL import Image
            actual=Image.open(file).convert('L');w,h=actual.size;mono=platform in ('diorite','flint')
            expected=out/f'{platform}-expected.pgm'
            if language:
                resource=ROOT/'resources/languages'/f'{languages[language]}-{w}.bin'
                subprocess.run([str(ROOT/'build/languages/render'),str(resource),str(clock[0]),str(clock[1]),str(int(mono)),str(expected)],check=True)
            else:subprocess.run([str(ROOT/'build/host/render'),str(w),str(h),str(clock[0]),str(clock[1]),str(int(mono)),str(expected)],check=True)
            ref=Image.open(expected);errors=[]
            for y in range(h):
                for x in range(w):
                    if w==h and (2*x+1-w)**2+(2*y+1-h)**2>(w-2)**2:continue
                    if actual.getpixel((x,y))!=ref.getpixel((x,y)):errors.append((x,y))
            assert not errors,f'{platform} {name}: {len(errors)} native pixels differ from the tested renderer, first {errors[:3]}'
            parity.append(name)
        return pixels
    try:
        time.sleep(4)
        send_data_to_qemu(watch.transport,QemuButton(state=QemuButton.Button.Back));time.sleep(.2)
        send_data_to_qemu(watch.transport,QemuButton(state=0));time.sleep(.5)
        grab('boot');ToolAppInstaller(watch,str(PBW),quiet=True).install()
        watch.send_packet(AppRunState(data=AppRunStateStart(uuid=APP)));time.sleep(1)
        hero=grab('hero',(10,8,1));start=len(logs);time.sleep(2.2);idle=grab('idle')
        assert idle==hero,'Face changed within a minute'
        assert not any('Prose time=' in line for line in logs[start:]),'Unexpected sub-minute update'
        poses=[('quarter',(3,15,1)),('twentyfive',(7,25,1)),('eleven-till',(10,35,1)),('seven-quarter',(6,45,1)),('eight-oclock',(8,0,1)),('eight-till',(7,55,1)),('noon',(12,0,1)),('midnight',(0,0,1))]
        for name,clock in poses:grab(name,clock)
        for name,clock,expected in [('five',(10,4,55),'time=10:05:'),('noon',(11,59,55),'time=12:00:'),('midnight',(23,59,55),'time=00:00:')]:
            grab('before-'+name,clock);start=len(logs);deadline=time.monotonic()+8
            while not any(expected in l for l in logs[start:]) and time.monotonic()<deadline:time.sleep(.03)
            assert any(expected in l for l in logs[start:]),'No natural '+name+' rollover';time.sleep(.05);grab(name+'-rollover')
        count=0
        for line in logs:
            match=re.search(r'Prose time=(\d+):(\d+):\d+ ids=(\d+),(\d+),(\d+),(\d+) count=(\d+)',line)
            if not match:continue
            h,m,*ids,n=map(int,match.groups());sentence=' '.join(oracle['words'][i] for i in ids[:n])
            assert sentence==oracle['phrases'][h*60+m]['sentence'],'Native phrase differs from source';count+=1
        assert count>=14,'Missing native frames'
        assert not any(any(term in l.lower() for term in ['crash','fault','allocation failed','unavailable']) for l in logs),'Native fault'
        service=AppMessageService(watch)
        def select(value):
            start=len(logs);service.send_message(APP,{0:Int32(value)})
            deadline=time.monotonic()+5
            while not any(f'Language saved={value}' in l for l in logs[start:]) and time.monotonic()<deadline:time.sleep(.03)
            assert any(f'Language saved={value}' in l for l in logs[start:]),'Language selection not saved'
            time.sleep(.2)
        language_frames=[]
        for language in range(1,len(languages)):
            code=languages[language];select(language)
            width={'basalt':144,'diorite':144,'flint':144,'emery':200,'chalk':180,'gabbro':260}[platform]
            proof=next(x for x in layout_proof if x['language']==code and x['width']==width)
            if ROOT.name=='dial-prose':
                worst=min(proof['frames'],key=lambda f:min(f['fontSizes']))
                longest=(worst['hour'],worst['minute'],1)
            else:
                candidate=max(source['phrases'][code],key=lambda p:sum(len(w['word']) for w in p['words']))
                longest=(candidate['hour'],candidate['minute'],1)
            for pose,clock in [('hero',(10,8,1)),('longest',longest)]:
                name='lang-'+code+'-'+pose;grab(name,clock);language_frames.append(name)
                assert any(f'Language boot={language}' in l for l in logs[-12:]),'Language did not survive app restart'
        before=len(logs)
        for value in [Int32(-1),Int32(len(languages)),CString('1')]:service.send_message(APP,{0:value});time.sleep(.25)
        assert not any('Language saved=' in l for l in logs[before:]),'Invalid language accepted'
        select(0);language=0
        assert not any(any(term in line.lower() for term in ['crash','fault','allocation failed','unavailable']) for line in logs),'Native fault during language checks'
        assert hashlib.sha256(PBW.read_bytes()).hexdigest()==installed_sha,'PBW changed during test'
        report={'languageChoices':len(languages),'languageFrames':language_frames,'languagePersistence':True,'invalidLanguagesRejected':True,'platform':platform,'pbwSHA256':installed_sha,'capturedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'nativePhrases':True,'pixelParity':True,'parityFrames':parity,'minuteCadence':True,'naturalFiveRollover':True,'naturalNoonRollover':True,'naturalMidnightRollover':True,'frames':frames,'logs':logs,'limits':'Isolated native emulator. Physical-watch daylight readability and battery testing remain open.'}
        (out/f'{platform}-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2),flush=True)
    finally:
        watch.unregister_endpoint(handle);cmd._close_pebble_connection(watch);cmd.pebble=None;shutdown();bridge_log.close()

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('platform',choices=json.loads((ROOT/'package.json').read_text())['pebble']['targetPlatforms']);parser.add_argument('--fresh',action='store_true');args=parser.parse_args();run(args.platform,args.fresh)
