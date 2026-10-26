from pathlib import Path
import subprocess,struct,zlib,tempfile,zipfile,os
root=Path(__file__).resolve().parent
import argparse
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
def png(w,h):
 def chunk(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
 rows=b''.join(b'\0'+bytes([50,150,240,255])*w for _ in range(h))
 return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(rows))+chunk(b'IEND',b'')
fixture=a.out/'original-test-skin.zip'
with zipfile.ZipFile(fixture,'w')as z:
 z.writestr('info.yml','name: Original high contrast\nauthor: Test fixture\nholdAtlas: [4, 4]\nholdAtlasMH: [4, 4]\n')
 for name in ['click','drag','flick','hold','click_mh','drag_mh','flick_mh','hold_mh']:z.writestr(name+'.png',png(64,32))
classes=a.out/'test-classes';classes.mkdir(exist_ok=True)
subprocess.run(['javac','--release','8','-encoding','UTF-8','-d',str(classes),str(root/'common/FrameStats.java'),str(root/'common/SkinArchive.java'),str(root/'tests/CoreTest.java')],check=True)
subprocess.run(['java','-Djava.io.tmpdir='+str(a.out.resolve()),'-cp',str(classes),'org.rhythmlab.assist.CoreTest',str(fixture)],check=True)
subprocess.run(['javac','--release','8','-encoding','UTF-8','-d',str(classes),str(root/'common/HudSample.java'),str(root/'tests/HudSampleTest.java')],check=True)
subprocess.run(['java','-cp',str(classes),'org.rhythmlab.assist.HudSampleTest'],check=True)
observer=a.out/'observer-test.exe'
subprocess.run(['gcc','-std=c11','-Wall','-Wextra','-Werror','-pthread',str(root/'tests/observer_test.c'),'-o',str(observer),'-lm'],check=True)
subprocess.run([str(observer.resolve())],check=True)
