package org.rhythmlab.assist;
import java.io.*;import java.nio.charset.StandardCharsets;import java.util.*;import java.util.zip.*;import java.util.regex.*;
/** Read-only inspector. Never extracts or executes resources, never edits a game save. */
public final class SkinArchive {
 private static final long MAX_FILE=32L*1024*1024,MAX_TOTAL=128L*1024*1024;
 private static final String[] NOTES={"click.png","drag.png","flick.png","hold.png","click_mh.png","drag_mh.png","flick_mh.png","hold_mh.png"};
 public final File file;public final List<String> images=new ArrayList<>(),audio=new ArrayList<>(),texts=new ArrayList<>();public final Set<String> members=new LinkedHashSet<>();
 public boolean standardPhira;public String name="未命名皮肤",author="未填写",report;public long unpacked;
 private SkinArchive(File f){file=f;}
 static void safeName(String name)throws IOException{if(name==null||name.length()>240||name.startsWith("/")||name.contains("\\")||name.contains(":"))throw new IOException("包内路径不安全");for(char c:name.toCharArray())if(c<32)throw new IOException("文件名含控制字符");for(String part:name.split("/",-1))if(part.equals("..")||part.equals("."))throw new IOException("包内路径越界");}
 public static SkinArchive open(File file)throws IOException{
  if(!file.isFile()||file.length()>64L*1024*1024)throw new IOException("请选择不超过64MB的皮肤ZIP");SkinArchive p=new SkinArchive(file);Set<String> folded=new HashSet<>();int count=0;String meta=null;
  try(ZipFile z=new ZipFile(file)){Enumeration<? extends ZipEntry> entries=z.entries();while(entries.hasMoreElements()){
   ZipEntry e=entries.nextElement();String n=e.getName();safeName(n);if(++count>1024||!folded.add(n.toLowerCase(Locale.ROOT)))throw new IOException("包内文件过多或名称冲突");if(e.isDirectory())continue;
   String lower=n.toLowerCase(Locale.ROOT);boolean image=lower.endsWith(".png")||lower.endsWith(".jpg")||lower.endsWith(".jpeg")||lower.endsWith(".webp"),sound=lower.endsWith(".ogg")||lower.endsWith(".wav")||lower.endsWith(".mp3"),text=lower.endsWith(".yml")||lower.endsWith(".yaml")||lower.endsWith(".json")||lower.endsWith(".txt");if(!image&&!sound&&!text)throw new IOException("仅接收图片、音效与皮肤元数据，不接收代码或未知文件");
   long length=0;CRC32 crc=new CRC32();try(InputStream in=z.getInputStream(e)){byte[] b=new byte[16384];int k;while((k=in.read(b))!=-1){length+=k;p.unpacked+=k;if(length>MAX_FILE||p.unpacked>MAX_TOTAL||text&&length>65536)throw new IOException("解压体积超出安全上限");crc.update(b,0,k);}}if(length!=e.getSize()||crc.getValue()!=e.getCrc())throw new IOException("ZIP资源CRC或大小不匹配，文件可能损坏");
   p.members.add(n);if(image)p.images.add(n);else if(sound)p.audio.add(n);else p.texts.add(n);
   if(n.equals("info.yml")||n.endsWith("/info.yml")){if(meta!=null)throw new IOException("包含多份info.yml，请分别打包");meta=n;}
  }}
  StringBuilder detail=new StringBuilder();if(meta!=null){String prefix=meta.substring(0,meta.length()-8),raw=new String(p.read(meta,65536),StandardCharsets.UTF_8);Map<String,String> values=new HashMap<>();for(String line:raw.split("\\r?\\n")){line=line.trim();if(line.isEmpty()||line.startsWith("#"))continue;int at=line.indexOf(':');if(at<=0)continue;String key=line.substring(0,at).trim(),value=line.substring(at+1).trim();if(values.put(key,value)!=null)throw new IOException("元数据字段重复");}
   p.name=plain(values.get("name"),p.name);p.author=plain(values.get("author"),p.author);boolean complete=values.containsKey("name")&&values.containsKey("author");for(String note:NOTES){String path=prefix+note;if(!p.members.contains(path)){complete=false;detail.append("缺少 ").append(note).append('\n');}else{int[] size=p.pngSize(path);if(note.equals("hold.png")||note.equals("hold_mh.png")){String key=note.equals("hold.png")?"holdAtlas":"holdAtlasMH";if(!atlas(values.get(key),size[1])){complete=false;detail.append(key).append(" 无效或越过图片边界\n");}}}}
   p.standardPhira=complete;detail.insert(0,complete?"标准Phira八图包：基础图片与长条图集检查通过。\n":"Phira皮肤：基础字段不完整。\n");
  }else detail.append("通用资源包：没有识别为标准Phira皮肤。仅提供资源检查和预览，不表示能在任一游戏内使用。\n");
  detail.append("图片 ").append(p.images.size()).append(" · 音效 ").append(p.audio.size()).append(" · 元数据 ").append(p.texts.size()).append("\n检查不等于游戏完整渲染；特效、音效和判定线颜色仍由目标游戏的实际支持决定。");p.report=detail.toString();return p;
 }
 static boolean atlas(String text,int height){if(text==null)return false;Matcher m=Pattern.compile("\\[\\s*([0-9]{1,4})\\s*,\\s*([0-9]{1,4})\\s*\\]").matcher(text);if(!m.matches())return false;int tail=Integer.parseInt(m.group(1)),head=Integer.parseInt(m.group(2));return tail>0&&head>0&&tail+head<height;}
 static String plain(String text,String fallback){if(text==null)return fallback;if(text.length()>120)return text.substring(0,120);if(text.length()>1&&text.charAt(0)=='"'&&text.endsWith("\""))return text.substring(1,text.length()-1);return text;}
 public byte[] read(String member,int limit)throws IOException{if(limit<0||limit>MAX_FILE||!members.contains(member))throw new IOException("资源未在检查清单内");safeName(member);try(ZipFile z=new ZipFile(file)){ZipEntry e=z.getEntry(member);if(e==null||e.isDirectory())throw new IOException("资源不存在");ByteArrayOutputStream out=new ByteArrayOutputStream();try(InputStream in=z.getInputStream(e)){byte[] b=new byte[8192];int n;while((n=in.read(b))!=-1){if(out.size()+n>limit)throw new IOException("资源过大");out.write(b,0,n);}}return out.toByteArray();}}
 public int[] pngSize(String member)throws IOException{byte[] b=read(member,(int)MAX_FILE);byte[] signature={(byte)137,80,78,71,13,10,26,10};if(b.length<24||!Arrays.equals(Arrays.copyOf(b,8),signature)||b[12]!='I'||b[13]!='H'||b[14]!='D'||b[15]!='R')throw new IOException("PNG头无效: "+member);int w=integer(b,16),h=integer(b,20);if(w<1||h<1||w>4096||h>4096)throw new IOException("PNG尺寸须在1～4096内");return new int[]{w,h};}
 static int integer(byte[] b,int p){return(b[p]&255)<<24|(b[p+1]&255)<<16|(b[p+2]&255)<<8|b[p+3]&255;}
}
