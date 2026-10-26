"""Extract immutable executable prologues from separately supplied original ELF samples."""
import argparse,hashlib,json,struct
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--phigros',type=Path,required=True);p.add_argument('--phira',type=Path,required=True);a=p.parse_args()
specs={
 'phigros':(a.phigros,157,'libil2cpp.so','il2cpp_domain_get','511e15b9324c171b585ae954e87266437b5de439289918331d1afce9c2b88433',[0x1d87a54]),
 'phira':(a.phira,39,'libphira.so','Java_quad_1native_QuadNative_setDataPath','5c2c484265d05b36e792fba328244b195360e799da296292a569446b42dee782',[0xdb6b78,0xdc9108,0xdc9288])}
result={}
for name,(path,version,library,symbol,digest,rvas)in specs.items():
 data=path.read_bytes();assert hashlib.sha256(data).hexdigest()==digest;assert data[:6]==b'\x7fELF\x02\x01'and struct.unpack_from('<H',data,18)[0]==183
 phoff=struct.unpack_from('<Q',data,32)[0];size,count=struct.unpack_from('<HH',data,54);prefixes=[]
 for rva in rvas:
  found=[]
  for i in range(count):
   typ,flags,off,va,pa,fs,ms,al=struct.unpack_from('<IIQQQQQQ',data,phoff+i*size)
   if typ==1 and flags&1 and va<=rva and rva-va+16<=fs:found.append(data[off+rva-va:off+rva-va+16].hex())
  assert len(found)==1;prefixes.append(found[0])
 result[name]=dict(version=version,library=library,symbol=symbol,sha256=digest,rvas=rvas,prefixes=prefixes)
(Path(__file__).parent/'native/profiles.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('PASS: exact original ELF hashes; AArch64 executable prologues extracted; no game binary copied')
