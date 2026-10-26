#define _GNU_SOURCE
#include <jni.h>
#include <dlfcn.h>
#include <link.h>
#include <stdatomic.h>
#include "observer-core.h"
#include "profile.h"
typedef void (*OnLoaded)(const char*,void*);
typedef struct {uint32_t version;int (*hook)(void*,void*,void**);int (*unhook)(void*);} NativeAPI;
static NativeAPI api;
static pthread_mutex_t install_lock=PTHREAD_MUTEX_INITIALIZER;
static atomic_int stage;
typedef struct {uintptr_t base;unsigned valid;} Ranges;
static int check_ranges(struct dl_phdr_info *info,size_t unused,void *data){(void)unused;Ranges *r=data;if(info->dlpi_addr!=r->base)return 0;for(size_t j=0;j<info->dlpi_phnum;j++){const ElfW(Phdr)*p=&info->dlpi_phdr[j];if(p->p_type!=PT_LOAD||!(p->p_flags&PF_X))continue;for(size_t i=0;i<PROFILE_COUNT;i++)if(PROFILE_RVAS[i]>=p->p_vaddr&&PROFILE_RVAS[i]-p->p_vaddr<=p->p_memsz&&p->p_memsz-(PROFILE_RVAS[i]-p->p_vaddr)>=16)r->valid|=1u<<i;}return 1;}
static void loaded(const char *name,void *handle){if(!name||!handle)return;const char *leaf=strrchr(name,'/');if(strcmp(leaf?leaf+1:name,PROFILE_LIBRARY))return;pthread_mutex_lock(&install_lock);if(atomic_load(&stage)!=1){pthread_mutex_unlock(&install_lock);return;}Dl_info info;void *symbol=dlsym(handle,PROFILE_SYMBOL);if(!symbol||!dladdr(symbol,&info)||!info.dli_fbase){atomic_store(&stage,-2);pthread_mutex_unlock(&install_lock);return;}Ranges ranges={(uintptr_t)info.dli_fbase,0};dl_iterate_phdr(check_ranges,&ranges);int valid=ranges.valid==((1u<<PROFILE_COUNT)-1);if(valid)for(size_t i=0;i<PROFILE_COUNT;i++)if(memcmp((void*)(ranges.base+PROFILE_RVAS[i]),PROFILE_PREFIXES[i],16))valid=0;if(!valid){atomic_store(&stage,-3);pthread_mutex_unlock(&install_lock);return;}
#ifdef OBSERVER_PHIGROS
 void *replacements[]={(void*)phigros_update};void **backups[]={(void**)&phigros_update_original};
#else
 void *replacements[]={(void*)phira_commit,(void*)phira_reset,(void*)phira_update};void **backups[]={(void**)&phira_commit_original,(void**)&phira_reset_original,(void**)&phira_update_original};
#endif
 size_t installed=0;for(size_t i=0;i<PROFILE_COUNT;i++){void *target=(void*)(ranges.base+PROFILE_RVAS[i]);if(api.hook(target,replacements[i],backups[i]))break;installed++;if(!*backups[i])break;}if(installed==PROFILE_COUNT&&*backups[installed-1])atomic_store(&stage,5);else{int failed=0;while(installed)if(api.unhook((void*)(ranges.base+PROFILE_RVAS[--installed])))failed=1;atomic_store(&stage,failed?-5:-4);}pthread_mutex_unlock(&install_lock);
}
__attribute__((visibility("default"),used)) OnLoaded native_init(const NativeAPI *entries){if(!entries||entries->version<1||entries->version>2||!entries->hook||!entries->unhook){atomic_store(&stage,-1);return NULL;}api=*entries;atomic_store(&stage,1);void *handle=dlopen(PROFILE_LIBRARY,RTLD_NOW|RTLD_NOLOAD);if(handle){loaded(PROFILE_LIBRARY,handle);dlclose(handle);}return loaded;}
/* Only exported Java operation: copy our own observation snapshot. */
JNIEXPORT jlongArray JNICALL Java_org_rhythmlab_assist_ReadOnlySource_read(JNIEnv *env,jclass type){(void)type;jlong values[12+HUD_VIEW_POINTS*2];HudPoint points[HUD_VIEW_POINTS];pthread_mutex_lock(&hud_lock);size_t count=hud_series_locked(points,HUD_VIEW_POINTS);uint64_t now=hud_now();jlong header[]={atomic_load(&stage),hud_state.epoch,hud_state.p,hud_state.g,hud_state.b,hud_state.m,hud_state.total,hud_state.valid,hud_state.partial,hud_state.revision,hud_state.seen&&now>=hud_state.seen?(jlong)(now-hud_state.seen):0,(jlong)count};memcpy(values,header,sizeof(header));for(size_t i=0;i<count;i++){values[12+2*i]=points[i].x;values[13+2*i]=points[i].y;}pthread_mutex_unlock(&hud_lock);jlongArray result=(*env)->NewLongArray(env,(jsize)(12+count*2));if(result)(*env)->SetLongArrayRegion(env,result,0,(jsize)(12+count*2),values);return result;}
JNIEXPORT jint JNICALL JNI_OnLoad(JavaVM *vm,void *unused){(void)vm;(void)unused;return JNI_VERSION_1_6;}
