package org.rhythmlab.assist;
public final class HudSampleTest {public static void main(String[] args){
 long[] packet={5,1,3,1,1,1,10,1,0,9,0,2,1,10000,6,6083};HudSample s=HudSample.parse(packet);if(!s.available||s.hit()!=4||s.judged()!=6||s.miss!=1||Math.abs(s.accuracy()-60.833333)>.0001)throw new AssertionError("weighted current accuracy");
 if(s.points!=2||s.x(1)!=6||s.y(1)!=60.83)throw new AssertionError("real series");
 HudSample empty=HudSample.parse(new long[12]);if(empty.available||!Double.isNaN(empty.accuracy()))throw new AssertionError("fake data when disconnected");
 long[] first={5,2,0,0,0,0,99,1,0,1,0,0};if(!Double.isNaN(HudSample.parse(first).accuracy()))throw new AssertionError("fake100 before first note");
 long[] malformed=packet.clone();malformed[11]=30000;if(HudSample.parse(malformed).available)throw new AssertionError("length bounds");malformed=packet.clone();malformed[2]=-1;if(HudSample.parse(malformed).available)throw new AssertionError("negative counts");
 malformed=packet.clone();malformed[14]=1;if(HudSample.parse(malformed).available)throw new AssertionError("nonmonotonic graph");malformed=packet.clone();malformed[15]=10001;if(HudSample.parse(malformed).available)throw new AssertionError("accuracy bounds");malformed=packet.clone();malformed[8]=3;malformed[10]=3000;HudSample partial=HudSample.parse(malformed);if(!partial.available||partial.partial!=3||partial.age!=3000)throw new AssertionError("coverage/stale metadata");
 System.out.println("PASS: observed P/G/Bad/Miss weights, hit/miss, real graph points, absent/empty and malformed packet handling");
}}
