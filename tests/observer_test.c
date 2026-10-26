#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "../native/observer-core.h"
static int original_calls;static void *seen_self;static const void *seen_method;
static void update(void *self,const void *method){original_calls++;seen_self=self;seen_method=method;}
static void reset(void *judge){original_calls++;seen_self=judge;}
static void commit(void *inner,unsigned judgment,double diff){original_calls++;assert(inner&&judgment<4&&diff==.012);}
static void judge_update(void *judge,void *resource,void *chart,void *bad){assert(judge&&resource&&chart&&bad==(void*)9);phira_commit((char*)judge+0x58,0,.012);phira_commit((char*)judge+0x58,1,.012);}
int main(void){
 unsigned char score[160]={0},list[40]={0},before[160];void *pointer=list;memcpy(score+0x88,&pointer,8);int value=100;memcpy(list+0x18,&value,4);value=3;memcpy(score+0x58,&value,4);value=1;memcpy(score+0x5c,&value,4);memcpy(score+0x64,&value,4);memcpy(before,score,sizeof(score));
 phigros_update_original=update;phigros_update(score,(void*)7);assert(original_calls==1&&seen_self==score&&seen_method==(void*)7);assert(!memcmp(score,before,sizeof(score)));assert(hud_state.p==3&&hud_state.g==1&&hud_state.m==1&&hud_state.total==100);assert(hud_accuracy(3,1,0,1)==7300);
 unsigned epoch=hud_state.epoch;memset(score+0x58,0,16);phigros_update(score,(void*)7);assert(hud_state.epoch>epoch&&hud_state.length==0);
 unsigned char judge[0x200]={0},res[0xa00]={0},chart[8]={0};memset(judge+0x58,0xa5,0x120);unsigned char protected_bytes[0x120];memcpy(protected_bytes,judge+0x58,sizeof(protected_bytes));double at=0;memcpy(res+0x9e0,&at,8);
 phira_update_original=judge_update;phira_commit_original=commit;phira_reset_original=reset;original_calls=0;phira_update(judge,res,chart,(void*)9);assert(original_calls==2&&hud_state.p==1&&hud_state.g==1);assert(!memcmp(judge+0x58,protected_bytes,sizeof(protected_bytes)));
 phira_commit(judge+0x58,3,.012);assert(hud_state.m==0);epoch=hud_state.epoch;phira_reset(judge);assert(hud_state.epoch>epoch&&hud_state.p==0&&original_calls==4);
 at=5;memcpy(res+0x9e0,&at,8);phira_update(judge,res,chart,(void*)9);at=1;memcpy(res+0x9e0,&at,8);epoch=hud_state.epoch;phira_update(judge,res,chart,(void*)9);assert(hud_state.epoch>epoch);
 hud_reset_locked(0,0);for(int i=0;i<20000;i++)hud_commit_locked(i%7==0?3:0);assert(hud_state.length==20000);HudPoint points[HUD_VIEW_POINTS];size_t n=hud_series_locked(points,HUD_VIEW_POINTS);assert(n<=HUD_VIEW_POINTS&&points[0].x==1&&points[n-1].x==20000);
 int minimum=10000;for(size_t i=0;i<n;i++){if(i)assert(points[i].x>points[i-1].x);if(points[i].y<minimum)minimum=points[i].y;}assert(minimum==0);/* first miss is not averaged away */
 hud_reset_locked(NULL,NULL);at=7;memcpy(res+0x9e0,&at,8);phira_update(judge,res,chart,(void*)9);assert(hud_state.partial==3&&hud_state.p==1&&hud_state.g==1);
 unsigned char second_chart[8]={0};epoch=hud_state.epoch;phira_update(judge,res,second_chart,(void*)9);assert(hud_state.epoch>epoch&&hud_state.p==1&&hud_state.g==1);
 memcpy(before,score,sizeof(score));value=-1;memcpy(score+0x58,&value,4);epoch=hud_state.epoch;phigros_update(score,(void*)7);assert(hud_state.epoch==epoch);memcpy(score,before,sizeof(score));
 puts("PASS: original call/arguments preserved; real counters read-only; reset/retry/chart change and partial attach; no protected-state writes; bounded20000-point history and preserved extrema/endpoints");
}
