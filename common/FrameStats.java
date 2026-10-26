package org.rhythmlab.assist;
import java.util.Arrays;
/** Measures Android callback intervals, not Unity/game render FPS or judgment. */
public final class FrameStats {
 private final double[] intervals=new double[240];private int count,cursor;private long previous=Long.MIN_VALUE;
 public void add(long nanos){if(previous!=Long.MIN_VALUE){if(nanos<=previous)return;double ms=(nanos-previous)/1000000.;if(ms<=1000){intervals[cursor++%intervals.length]=ms;count=Math.min(count+1,intervals.length);}}previous=nanos;}
 public void reset(){count=cursor=0;previous=Long.MIN_VALUE;}
 public int samples(){return count;}
 public double meanMs(){double sum=0;for(int i=0;i<count;i++)sum+=intervals[i];return count==0?0:sum/count;}
 public double p95Ms(){if(count==0)return 0;double[] sorted=Arrays.copyOf(intervals,count);Arrays.sort(sorted);return sorted[(int)Math.ceil(.95*count)-1];}
}
