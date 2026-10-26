"""Bounded source/APK capability audit; not proof of real-device compatibility."""
from pathlib import Path
import argparse,hashlib,json,re,struct,zipfile
root=Path(__file__).resolve().parent;p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();report={}
expected={'AssistPanel.java','Dashboard.java','Entry.java','FrameStats.java','Notice.java','SkinArchive.java'};assert {p.name for p in(root/'common').glob('*.java')}==expected
entry=(root/'common/Entry.java').read_text(encoding='utf-8');assert entry.count('findAndHookMethod(')==1 and 'Application.class,"attach"'in entry
for path in(root/'common').glob('*.java'):
 s=path.read_text(encoding='utf-8');assert not re.search(r'\bnative\s+\w+\s+\w+\s*\(',s),path;assert 'System.load'not in s and 'Runtime.getRuntime'not in s,path
def dex_capabilities(d):
 def uleb(at):
  val=shift=0
  while True:
   b=d[at];at+=1;val|=(b&127)<<shift
   if b<128:return val,at
   shift+=7;assert shift<35
 sc,so=struct.unpack_from('<II',d,56);tc,to=struct.unpack_from('<II',d,64);mc,mo=struct.unpack_from('<II',d,88);cc,co=struct.unpack_from('<II',d,96);strings=[]
 for i in range(sc):
  at=struct.unpack_from('<I',d,so+4*i)[0];_,at=uleb(at);strings.append(d[at:d.index(0,at)].decode('utf-8','replace'))
 types=[strings[struct.unpack_from('<I',d,to+4*i)[0]]for i in range(tc)];classes=[]
 for i in range(cc):
  record=struct.unpack_from('<8I',d,co+32*i);name=types[record[0]];assert name.startswith('Lorg/rhythmlab/assist/'),name;classes.append(name);at=record[6]
  if not at:continue
  counts=[]
  for _ in range(4):v,at=uleb(at);counts.append(v)
  for _ in range(sum(counts[:2])):_,at=uleb(at);_,at=uleb(at)
  for _ in range(sum(counts[2:])):
   _,at=uleb(at);flags,at=uleb(at);_,at=uleb(at);assert not flags&0x100,'native method definition'
 methods=[]
 for i in range(mc):
  clazz,_,name=struct.unpack_from('<HHI',d,mo+8*i);owner=types[clazz];method=strings[name];methods.append((owner,method))
  assert not owner.startswith(('Ljava/net/','Ljavax/net/','Ldalvik/system/DexClassLoader;','Landroid/app/Instrumentation;','Landroid/hardware/input/InputManager;')),(owner,method)
  assert not(owner=='Ljava/lang/System;'and method in ['load','loadLibrary']),(owner,method)
 return dict(owned_classes=len(classes),native_method_definitions=0,forbidden_network_or_injection_method_references=0,method_references=len(methods))
for target,v in json.loads((a.out/'verification.json').read_text(encoding='utf-8')).items():
 apk=a.out/v['artifact'];assert hashlib.sha256(apk.read_bytes()).hexdigest()==v['sha256']
 with zipfile.ZipFile(apk)as z:
  assert not any(n.endswith(('.so','.dex'))and n!='classes.dex'for n in z.namelist());assert set(z.namelist())<= {'AndroidManifest.xml','resources.arsc','classes.dex','assets/xposed_init'}
  report[target]=dict(**dex_capabilities(z.read('classes.dex')),scope=v['scope'],no_native_libraries=True,no_host_engine_or_old_module_classes=True,source_hook_allowlist=['android.app.Application.attach'],device_tested=False)
(a.out/'capability-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('PASS: two APK DEX/source audits; owned classes only, no native/network/input-injection entry points, one Android lifecycle hook')
