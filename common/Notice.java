package org.rhythmlab.assist;
import android.app.*;import android.view.ContextThemeWrapper;import android.widget.*;
public final class Notice {
 public static final String TEXT="本工具为非官方使用辅助，与Phigros、Phira、Malody官方无隶属关系。资源权利归各自权利人所有，请仅检查和使用本人有权使用的皮肤。\n\n本项目只提供显示辅助、界面刷新采样和皮肤资源检查预览；不提供自动游玩、自动输入、判定或成绩修改、RKS/解锁修改，不绕过账号、购买、服务器、签名完整性或反作弊校验。\n\n皮肤预览和检查不能代表游戏实际渲染。测试工具可能存在兼容问题；手机效果尚需验证。模块不上传数据，不读取游戏存档，游戏自身的登录联网由原版处理。\n\n本声明用于说明功能范围和风险，不替代合法授权，也不免除依法应承担的责任。";
 private static boolean read;private static Dialog shown;
 public static boolean accepted(){return read;}
 public static void show(Activity a,Runnable next){show(a,next,a::finish);}
 public static void show(Activity a,Runnable next,Runnable decline){if(read){next.run();return;}if(shown!=null||a.isFinishing())return;TextView t=new TextView(a);t.setText(TEXT);t.setTextColor(0xff25354a);t.setTextSize(15);t.setPadding(24,16,24,16);ScrollView scroll=new ScrollView(a);scroll.addView(t);AlertDialog d=new AlertDialog.Builder(new ContextThemeWrapper(a,android.R.style.Theme_Material_Light_Dialog_Alert)).setTitle("辅助模块 · 使用说明与免责声明").setView(scroll).setPositiveButton("已阅读，继续",(v,w)->{read=true;shown=null;next.run();}).setNegativeButton("暂不使用",(v,w)->{shown=null;decline.run();}).setCancelable(false).create();shown=d;d.setOnDismissListener(v->{if(shown==d)shown=null;});d.show();}
 private Notice(){}
}
