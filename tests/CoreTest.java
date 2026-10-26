package org.rhythmlab.assist;
import java.io.*;import java.nio.file.*;import java.util.zip.*;
public final class CoreTest {
 static File zip(String... names)throws Exception{File f=Files.createTempFile("assist-pack-",".zip").toFile();try(ZipOutputStream z=new ZipOutputStream(new FileOutputStream(f))){for(String name:names){z.putNextEntry(new ZipEntry(name));z.write("fixture".getBytes("UTF-8"));z.closeEntry();}}return f;}
 public static void main(String[] args)throws Exception{
  FrameStats f=new FrameStats();for(int i=0;i<=60;i++)f.add(i*16666667L);if(Math.abs(f.meanMs()-16.666667)>.001||f.samples()!=60)throw new AssertionError("frame interval");f.add(-1);if(f.samples()!=60)throw new AssertionError("non-monotonic");f.reset();if(f.samples()!=0)throw new AssertionError("reset");
  for(String s:new String[]{"../evil.png","/abs.png","C:/evil.png","nested/../../evil.png","bad\\evil.png","bad\n.png"})try{SkinArchive.open(zip(s));throw new AssertionError(s);}catch(IOException expected){}
  try{SkinArchive.open(zip("a.png","A.png"));throw new AssertionError("case collision");}catch(IOException expected){}
  try{SkinArchive.open(zip("payload.so"));throw new AssertionError("executable accepted");}catch(IOException expected){}
  File corrupt=zip("note.png");byte[] bytes=Files.readAllBytes(corrupt.toPath());for(int i=0;i<bytes.length-20;i++)if(bytes[i]==0x50&&bytes[i+1]==0x4b&&bytes[i+2]==1&&bytes[i+3]==2){bytes[i+16]^=1;break;}Files.write(corrupt.toPath(),bytes);try{SkinArchive.open(corrupt);throw new AssertionError("CRC corruption accepted");}catch(IOException expected){}
  SkinArchive incomplete=SkinArchive.open(zip("note.png"));if(incomplete.standardPhira||incomplete.images.size()!=1)throw new AssertionError("claimed support");
  File valid=new File(args[0]);SkinArchive p=SkinArchive.open(valid);if(!p.standardPhira||p.images.size()!=8||!p.name.equals("Original high contrast"))throw new AssertionError("standard pack");
  try{p.read("../anything",100);throw new AssertionError("unchecked member");}catch(IOException expected){}
  System.out.println("PASS: callback frame timing; bounded skin archive inspection; traversal/case/executable rejection; genuine standard-pack metadata; unknown pack not claimed compatible");
 }
}
