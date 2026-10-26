"""Bounded source/APK capability audit; not proof of real-device compatibility."""
from pathlib import Path
import argparse,hashlib,json,re,struct,zipfile
root=Path(__file__).resolve().parent;p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();report={}
expected={'AssistPanel.java','Dashboard.java','Entry.java','FrameStats.java','Notice.java','SkinArchive.java','HudSample.java','LiveHud.java','ReadOnlySource.java'};assert {p.name for p in(root/'common').glob('*.java')}==expected
entry=(root/'common/Entry.java').read_text(encoding='utf-8');assert entry.count('findAndHookMethod(')==1 and 'Application.class,"attach"'in entry
for path in(root/'common').glob('*.java'):
 s=path.read_text(encoding='utf-8');assert 'Runtime.getRuntime'not in s,path
 if path.name=='ReadOnlySource.java':assert s.count('native long[] read()')==1 and s.count('System.loadLibrary("assist_observer")')==1
 else:assert not re.search(r'\bnative\s+\w+\s+\w+\s*\(',s)and 'System.load'not in s,path
native=(root/'native/observer.c').read_text(encoding='utf-8');core=(root/'native/observer-core.h').read_text(encoding='utf-8')
assert native.count('JNIEXPORT jlongArray')==1 and 'Java_org_rhythmlab_assist_ReadOnlySource_read('in native
for forbidden in ['mprotect(','process_vm_writev(','ptrace(','setenv(','fopen(','write(','memset(self','memcpy(self','memcpy(judge','memset(judge','setEnabled','ControlConfig','input_api','touch_api']:
 assert forbidden not in native+core,forbidden
assert 'phigros_update_original(self,method);'in core and 'phira_commit_original(inner,what,diff);'in core and 'phira_update_original(judge,resource,chart,bad);'in core and 'phira_reset_original(judge);'in core
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
 types=[strings[struct.unpack_from('<I',d,to+4*i)[0]]for i in range(tc)];classes=[];native_defs=[]
 for i in range(cc):
  record=struct.unpack_from('<8I',d,co+32*i);name=types[record[0]];assert name.startswith('Lorg/rhythmlab/assist/'),name;classes.append(name);at=record[6]
  if not at:continue
  counts=[]
  for _ in range(4):v,at=uleb(at);counts.append(v)
  for _ in range(sum(counts[:2])):_,at=uleb(at);_,at=uleb(at)
  for count in counts[2:]:
   idx=0
   for _ in range(count):
    diff,at=uleb(at);idx+=diff;flags,at=uleb(at);_,at=uleb(at)
    if flags&0x100:
     clazz,_,method_name=struct.unpack_from('<HHI',d,mo+8*idx);native_defs.append((types[clazz],strings[method_name]))
 methods=[]
 for i in range(mc):
  clazz,_,name=struct.unpack_from('<HHI',d,mo+8*i);owner=types[clazz];method=strings[name];methods.append((owner,method))
  assert not owner.startswith(('Ljava/net/','Ljavax/net/','Ldalvik/system/DexClassLoader;','Landroid/app/Instrumentation;','Landroid/hardware/input/InputManager;')),(owner,method)
  assert not(owner=='Ljava/lang/System;'and method=='load'),(owner,method)
 assert native_defs==[('Lorg/rhythmlab/assist/ReadOnlySource;','read')],native_defs
 assert methods.count(('Ljava/lang/System;','loadLibrary'))==1
 return dict(owned_classes=len(classes),native_method_definitions=native_defs,forbidden_network_or_injection_method_references=0,method_references=len(methods))

def elf_exports(data):
 assert data[:6]==b'\x7fELF\x02\x01'and struct.unpack_from('<H',data,18)[0]==183
 phoff=struct.unpack_from('<Q',data,32)[0];stride,count=struct.unpack_from('<HH',data,54)
 for i in range(count):
  row=struct.unpack_from('<IIQQQQQQ',data,phoff+i*stride)
  if row[0]==1:assert row[7]>=16384 and row[2]%16384==row[3]%16384
 off=struct.unpack_from('<Q',data,40)[0];stride,count=struct.unpack_from('<HH',data,58);sections=[struct.unpack_from('<IIQQQQIIQQ',data,off+i*stride)for i in range(count)];exports=[]
 for s in sections:
  if s[1]!=11:continue
  strings=sections[s[6]];table=data[strings[4]:strings[4]+strings[5]]
  for pos in range(s[4],s[4]+s[5],s[9]):
   name,info,other,index,value,size=struct.unpack_from('<IBBHQQ',data,pos)
   if index and info>>4 in [1,2]and other&3==0:exports.append(table[name:table.index(0,name)].decode())
 assert set(exports)=={'native_init','JNI_OnLoad','Java_org_rhythmlab_assist_ReadOnlySource_read'},exports
 return exports
for target,v in json.loads((a.out/'verification.json').read_text(encoding='utf-8')).items():
 apk=a.out/v['artifact'];assert hashlib.sha256(apk.read_bytes()).hexdigest()==v['sha256']
 with zipfile.ZipFile(apk)as z:
  assert set(z.namelist())== {'AndroidManifest.xml','resources.arsc','classes.dex','assets/xposed_init','assets/native_init','lib/arm64-v8a/libassist_observer.so'}
  assert z.read('assets/native_init')==b'libassist_observer.so\n'
  exports=elf_exports(z.read('lib/arm64-v8a/libassist_observer.so'))
  report[target]=dict(**dex_capabilities(z.read('classes.dex')),scope=v['scope'],read_only_native_exports=exports,no_host_engine_or_old_module_classes=True,source_java_hook_allowlist=['android.app.Application.attach'],native_observer_hooks=1 if target=='phigros'else 3,device_tested=False)
(a.out/'capability-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('PASS: owned classes only; exact read-only JNI/ELF export allowlist; no network/input-injection APIs; 16KB ELF alignment; bounded source forwarding checks (not device proof)')
