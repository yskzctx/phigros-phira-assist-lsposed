#ifndef ASSIST_OBSERVER_CORE_H
#define ASSIST_OBSERVER_CORE_H
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <pthread.h>
#include <time.h>
#define HUD_MAX_NOTES 20000
#define HUD_VIEW_POINTS 514
typedef struct {int x,y;} HudPoint;
static pthread_mutex_t hud_lock=PTHREAD_MUTEX_INITIALIZER;
static struct {int p,g,b,m,total,valid,partial;unsigned epoch,revision;size_t length;void *owner,*chart;double at;uint64_t seen;HudPoint series[HUD_MAX_NOTES];} hud_state;
static uint64_t hud_now(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return (uint64_t)t.tv_sec*1000+(uint64_t)t.tv_nsec/1000000;}
static int hud_accuracy(int p,int g,int b,int m){int n=p+g+b+m;return n?(int)(((int64_t)p*10000+(int64_t)g*6500+n/2)/n):-1;}
static void hud_reset_locked(void *owner,void *chart){unsigned epoch=hud_state.epoch+1;memset(&hud_state,0,sizeof(hud_state));hud_state.epoch=epoch;hud_state.owner=owner;hud_state.chart=chart;hud_state.total=-1;}
static void hud_append_locked(void){int n=hud_state.p+hud_state.g+hud_state.b+hud_state.m;if(n>0&&n<=HUD_MAX_NOTES&&hud_state.length<HUD_MAX_NOTES){HudPoint point={n,hud_accuracy(hud_state.p,hud_state.g,hud_state.b,hud_state.m)};hud_state.series[hud_state.length++]=point;}hud_state.revision++;}
static void hud_commit_locked(unsigned what){if(what>3||hud_state.p+hud_state.g+hud_state.b+hud_state.m>=HUD_MAX_NOTES)return;switch(what){case 0:hud_state.p++;break;case 1:hud_state.g++;break;case 2:hud_state.b++;break;case 3:hud_state.m++;break;}hud_state.valid=1;hud_state.seen=hud_now();hud_append_locked();}
/* Keep first/last and the min/max of each bucket in chronological order. */
static size_t hud_series_locked(HudPoint *out,size_t cap){size_t n=hud_state.length;if(cap<4||!n)return 0;if(n<=cap){memcpy(out,hud_state.series,n*sizeof(*out));return n;}size_t count=0,buckets=(cap-2)/2;out[count++]=hud_state.series[0];for(size_t k=0;k<buckets;k++){size_t start=1+(n-2)*k/buckets,end=1+(n-2)*(k+1)/buckets,lo=start,hi=start;for(size_t j=start;j<end;j++){if(hud_state.series[j].y<hud_state.series[lo].y)lo=j;if(hud_state.series[j].y>hud_state.series[hi].y)hi=j;}if(lo>hi){size_t swap=lo;lo=hi;hi=swap;}out[count++]=hud_state.series[lo];if(hi!=lo)out[count++]=hud_state.series[hi];}out[count++]=hud_state.series[n-1];return count;}
static void (*phigros_update_original)(void*,const void*);
static void phigros_update(void *self,const void *method){phigros_update_original(self,method);if(!self)return;int counts[4];memcpy(counts,(char*)self+0x58,sizeof(counts));int n=0;for(int i=0;i<4;i++){if(counts[i]<0||counts[i]>HUD_MAX_NOTES)return;n+=counts[i];}if(n>HUD_MAX_NOTES)return;void *list=NULL;memcpy(&list,(char*)self+0x88,sizeof(list));int total=-1;if(list){memcpy(&total,(char*)list+0x18,4);if(total<0||total>HUD_MAX_NOTES)total=-1;}pthread_mutex_lock(&hud_lock);int previous=hud_state.p+hud_state.g+hud_state.b+hud_state.m;if(hud_state.owner!=self||n<previous){hud_reset_locked(self,NULL);if(n)hud_state.partial=2;previous=0;}hud_state.p=counts[0];hud_state.g=counts[1];hud_state.b=counts[2];hud_state.m=counts[3];hud_state.total=total;hud_state.valid=1;hud_state.seen=hud_now();if(n!=previous)hud_append_locked();pthread_mutex_unlock(&hud_lock);}
static void (*phira_update_original)(void*,void*,void*,void*);
static void (*phira_commit_original)(void*,unsigned,double);
static void (*phira_reset_original)(void*);
static _Thread_local void *phira_current_inner;
static void phira_commit(void *inner,unsigned what,double diff){phira_commit_original(inner,what,diff);if(inner!=phira_current_inner||!inner||what>3)return;pthread_mutex_lock(&hud_lock);hud_commit_locked(what);pthread_mutex_unlock(&hud_lock);}
static void phira_reset(void *judge){phira_reset_original(judge);pthread_mutex_lock(&hud_lock);hud_reset_locked(judge,NULL);pthread_mutex_unlock(&hud_lock);}
static void phira_update(void *judge,void *resource,void *chart,void *bad){if(!judge||!resource){phira_update_original(judge,resource,chart,bad);return;}double at;memcpy(&at,(char*)resource+0x9e0,8);pthread_mutex_lock(&hud_lock);int first=hud_state.owner==NULL;if(hud_state.owner!=judge||(hud_state.chart&&hud_state.chart!=chart)||(isfinite(at)&&at<hud_state.at-.25)){hud_reset_locked(judge,chart);if(first&&at>.2)hud_state.partial=3;}hud_state.chart=chart;if(isfinite(at))hud_state.at=at;hud_state.valid=1;hud_state.seen=hud_now();pthread_mutex_unlock(&hud_lock);void *previous=phira_current_inner;phira_current_inner=(char*)judge+0x58;phira_update_original(judge,resource,chart,bad);phira_current_inner=previous;}
#endif
