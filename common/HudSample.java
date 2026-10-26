package org.rhythmlab.assist;
/** Strict decoding of observer-owned counters. No game pointers cross JNI. */
public final class HudSample {
 public final boolean available;public final int stage,perfect,good,bad,miss,total,partial,points;public final long epoch,age;private final long[] data;
 private HudSample(long[] a,boolean valid){data=a;available=valid;stage=(int)a[0];epoch=a[1];perfect=(int)a[2];good=(int)a[3];bad=(int)a[4];miss=(int)a[5];total=(int)a[6];partial=(int)a[8];age=a[10];points=valid?(int)a[11]:0;}
 public static HudSample parse(long[] a){boolean ok=a!=null&&a.length>=12;if(ok){long n=0;for(int i=2;i<=5;i++){ok&=a[i]>=0&&a[i]<=20000;n+=a[i];}ok&=n<=20000&&a[11]>=0&&a[11]<=514&&a.length==12+2*a[11]&&a[10]>=0&&a[6]>=-1&&a[6]<=20000;long last=0;if(ok)for(int i=0;i<a[11];i++){long x=a[12+i*2],y=a[13+i*2];ok&=x>last&&x<=n&&y>=0&&y<=10000;last=x;}}if(!ok)return new HudSample(new long[12],false);return new HudSample(a.clone(),a[0]==5&&a[7]==1);}
 public int hit(){return perfect+good;}public int judged(){return hit()+bad+miss;}public double accuracy(){return available&&judged()>0?(perfect+good*.65)/judged()*100:Double.NaN;}
 public int x(int i){return (int)data[12+i*2];}public double y(int i){return data[13+i*2]/100.;}
}
