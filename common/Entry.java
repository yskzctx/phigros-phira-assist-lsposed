package org.rhythmlab.assist;
import android.app.*;import android.content.Context;import android.os.Bundle;
import de.robv.android.xposed.*;import de.robv.android.xposed.callbacks.XC_LoadPackage;
/** Bootstrap and Activity lifecycle; gameplay observer only reads original results. */
public final class Entry implements IXposedHookLoadPackage {
 private static void ui(Runnable action){try{action.run();}catch(Throwable error){XposedBridge.log("RhythmAssist: window helper unavailable ("+error.getClass().getSimpleName()+")");}}
 public void handleLoadPackage(XC_LoadPackage.LoadPackageParam p)throws Throwable{
  if(!Target.HOST.equals(p.packageName)||!Target.HOST.equals(p.processName))return;
  XposedHelpers.findAndHookMethod(Application.class,"attach",Context.class,new XC_MethodHook(){protected void afterHookedMethod(MethodHookParam hook){
   ReadOnlySource.start((Context)hook.thisObject);
   ((Application)hook.thisObject).registerActivityLifecycleCallbacks(new Application.ActivityLifecycleCallbacks(){
    public void onActivityResumed(Activity a){ui(()->AssistPanel.attach(a));}public void onActivityPaused(Activity a){ui(()->AssistPanel.pause(a));}public void onActivityDestroyed(Activity a){ui(()->AssistPanel.detach(a));}
    public void onActivityCreated(Activity a,Bundle b){}public void onActivityStarted(Activity a){}public void onActivityStopped(Activity a){}public void onActivitySaveInstanceState(Activity a,Bundle b){}
   });
  }});
 }
}
