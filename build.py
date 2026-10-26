"""Build two Java-only auxiliary modules. Signing material must be outside source."""
from pathlib import Path
import argparse,subprocess,json,os,zipfile,hashlib,xml.sax.saxutils as xml
root=Path(__file__).resolve().parent;p=argparse.ArgumentParser(description=__doc__)
for arg in ['sdk','xposed-api','keystore','password-file','out']:p.add_argument('--'+arg,type=Path,required=True)
p.add_argument('--alias',required=True);p.add_argument('--target',choices=['phigros','phira','all'],default='all');a=p.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
for sensitive in [a.keystore.resolve(),a.password_file.resolve()]:assert root not in sensitive.parents,'Keep credentials outside repository'
sdk=a.sdk.resolve();tools=sdk/'build-tools/36.0.0';android=sdk/'platforms/android-36/android.jar';api=a.xposed_api.resolve()
def run(*args):return subprocess.run(list(map(str,args)),check=True)
def digest(p):
 with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
targets=json.loads((root/'targets.json').read_text(encoding='utf-8'));reports={}
for key,t in targets.items():
 if a.target not in ['all',key]:continue
 stage=out/(key+'-build');stage.mkdir(exist_ok=True);classes=stage/'classes';classes.mkdir(exist_ok=True)
 for f in classes.rglob('*.class'):f.unlink()
 target=stage/'Target.java';target.write_text('package org.rhythmlab.assist;public final class Target{public static final String NAME='+json.dumps(t['name'])+',HOST='+json.dumps(t['host'])+',MODULE='+json.dumps(t['module'])+',ACTIVITY_PREFIX='+json.dumps(t['activity_prefix'])+';public static final boolean PHIRA='+str(t['phira']).lower()+';}',encoding='utf-8')
 run('javac','--release','8','-encoding','UTF-8','-classpath',str(android)+os.pathsep+str(api),'-d',classes,*sorted((root/'common').glob('*.java')),target)
 dex=stage/'dex';dex.mkdir(exist_ok=True);run('java','-Djava.io.tmpdir='+str(stage),'-cp',tools/'lib/d8.jar','com.android.tools.r8.D8','--min-api','26','--lib',android,'--lib',api,'--output',dex,*sorted(classes.rglob('*.class')))
 manifest=stage/'AndroidManifest.xml';manifest.write_text('''<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="MODULE" android:versionCode="1" android:versionName="0.1.0-assist-test"><uses-sdk android:minSdkVersion="26" android:targetSdkVersion="34"/><queries><package android:name="HOST"/></queries><application android:label="NAME 纯辅助" android:theme="@android:style/Theme.Material.Light.NoActionBar" android:allowBackup="false"><meta-data android:name="xposedmodule" android:value="true"/><meta-data android:name="xposedminversion" android:value="93"/><meta-data android:name="xposeddescription" android:value="显示与皮肤资源辅助；不修改游玩判定或成绩"/><meta-data android:name="xposedscope" android:resource="@array/assist_scope"/><activity android:name="org.rhythmlab.assist.Dashboard" android:exported="true"><intent-filter><action android:name="android.intent.action.MAIN"/><category android:name="android.intent.category.LAUNCHER"/></intent-filter></activity></application></manifest>'''.replace('MODULE',t['module']).replace('HOST',t['host']).replace('NAME',xml.escape(t['name'])),encoding='utf-8')
 values=stage/'res/values';values.mkdir(parents=True,exist_ok=True);(values/'scope.xml').write_text('<resources><string-array name="assist_scope"><item>'+t['host']+'</item></string-array></resources>')
 compiled=stage/'compiled.zip';run(tools/'aapt2.exe','compile','--dir',stage/'res','-o',compiled);resources=stage/'resources.apk';run(tools/'aapt2.exe','link','-I',android,'--manifest',manifest,'-o',resources,compiled)
 unsigned=stage/'unsigned.apk';aligned=stage/'aligned.apk'
 with zipfile.ZipFile(resources)as res,zipfile.ZipFile(unsigned,'w')as z:
  for e in res.infolist():z.writestr(e,res.read(e))
  z.write(dex/'classes.dex','classes.dex',compress_type=zipfile.ZIP_DEFLATED);z.writestr('assets/xposed_init','org.rhythmlab.assist.Entry\n')
 run(tools/'zipalign.exe','-f','4',unsigned,aligned);apk=out/(t['name']+'-Assist-LSPosed-v0.1.0-TEST.apk')
 run('java','-Djava.io.tmpdir='+str(stage),'-jar',tools/'lib/apksigner.jar','sign','--ks',a.keystore.resolve(),'--ks-key-alias',a.alias,'--ks-pass','file:'+str(a.password_file.resolve()),'--min-sdk-version','26','--v1-signing-enabled','false','--v2-signing-enabled','true','--v3-signing-enabled','true','--v4-signing-enabled','false','--out',apk,aligned)
 run('java','-jar',tools/'lib/apksigner.jar','verify',apk);run(tools/'zipalign.exe','-c','4',apk)
 permissions=subprocess.check_output([str(tools/'aapt2.exe'),'dump','permissions',str(apk)],encoding='utf-8');assert 'uses-permission'not in permissions
 with zipfile.ZipFile(apk)as z:
  assert z.testzip()is None;assert not any(n.endswith('.so')for n in z.namelist());assert z.read('assets/xposed_init')==b'org.rhythmlab.assist.Entry\n';assert '免责声明'.encode()in z.read('classes.dex')
 reports[key]=dict(artifact=apk.name,sha256=digest(apk),bytes=apk.stat().st_size,package=t['module'],scope=t['host'],recommended_scope_resource_array=True,signature_verified=True,no_native_libraries=True,no_requested_permissions=True,device_tested=False,full_game_skin_replacement=False)
 for f in [unsigned,aligned,resources,compiled]:f.unlink()
(out/'verification.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(reports,ensure_ascii=False))
