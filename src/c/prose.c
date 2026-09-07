// Copyright 2026 Luke Steuber. MIT License.
#include "prose.h"
#include <stddef.h>
#include <stdio.h>
#ifndef PROSE_HOST
#include <pebble.h>
#endif
#include "assets.h"
static const char *const RUNS[]={"it is","five","ten","a quarter","twenty","twenty five","half","past","till","o'clock","one","two","three","four","five","six","seven","eight","nine","ten","eleven","twelve"};
const char *prose_run_text(int id){return id>=0&&id<22?RUNS[id]:"";}
ProsePhrase prose_phrase(int hour,int minute){
  hour=((hour%24)+24)%24;minute=((minute%60)+60)%60;
  ProsePhrase p={{0,0,0,0},0,{0}};snprintf(p.exact,sizeof(p.exact),"%02d:%02d",hour,minute);
  int bucket=minute/5,shown=(hour+(bucket>6))%12;int hour_id=10+(shown+11)%12;
  p.ids[p.count++]=0;
  if(!bucket){p.ids[p.count++]=hour_id;p.ids[p.count++]=9;}
  else{static const uint8_t minutes[]={0,1,2,3,4,5,6,5,4,3,2,1};p.ids[p.count++]=minutes[bucket];p.ids[p.count++]=bucket<=6?7:8;p.ids[p.count++]=hour_id;}
  return p;
}
static bool inside(const ProseLayout *l,int x,int y){
  if(x<1||y<1||x>=l->width-1||y>=l->height-1)return false;
  if(l->width!=l->height)return true;
  int dx=2*x+1-l->width,dy=2*y+1-l->height,r=l->width-2;return dx*dx+dy*dy<=r*r;
}
static int top_for(const ProseLayout *l,int id,bool exact_hour){
  if(exact_hour){if(id==0)return l->exact_top[0];if(id==9)return l->exact_top[2];return l->exact_top[1];}
  return id==0?l->top[0]:id<=6?l->top[1]:id<=9?l->top[2]:l->top[3];
}
static int check_sprite(const ProseLayout*l,int id,int x,int y){
  const ProseSprite*s=l->sprites+id;return !inside(l,x,y)||!inside(l,x+s->w-1,y)||!inside(l,x,y+s->h-1)||!inside(l,x+s->w-1,y+s->h-1);
}
int prose_bounds_errors(int width,int height){
  const ProseLayout*l=prose_layout(width,height);if(!l)return 1;int errors=0;
  for(int h=0;h<24;h++)for(int m=0;m<60;m++){
    ProsePhrase p=prose_phrase(h,m);int previous_bottom=0;
    for(int i=0;i<p.count;i++){int id=p.ids[i];const ProseSprite*s=l->sprites+id;int x=(width-s->w)/2,y=top_for(l,id,p.count==3);errors+=check_sprite(l,id,x,y);if(y<=previous_bottom+2)errors++;previous_bottom=y+s->h-1;}
  }
  return errors;
}
static void sprite(const ProseLayout*l,int id,int x,int y,uint8_t ink,bool mono,ProsePixel pixel,void*user){
  const ProseSprite*s=l->sprites+id;unsigned total=(unsigned)s->w*s->h,pos=0,index=s->offset;
  while(pos<total){uint8_t run=l->data[index++],level=run>>6;unsigned length=(run&63)+1;
    for(unsigned j=0;j<length&&pos<total;j++,pos++){int xx=x+pos%s->w,yy=y+pos/s->w;if(level&&inside(l,xx,yy))pixel(xx,yy,mono?255:level*ink/3,user);}
  }
}
void prose_render(int width,int height,int hour,int minute,bool monochrome,ProsePixel pixel,void*user){
  const ProseLayout*l=prose_layout(width,height);if(!l)return;
  ProsePhrase p=prose_phrase(hour,minute);
  for(int i=0;i<p.count;i++){int id=p.ids[i];const ProseSprite*s=l->sprites+id;uint8_t ink=(id==0||(id>=7&&id<=9))?170:255;sprite(l,id,(width-s->w)/2,top_for(l,id,p.count==3),ink,monochrome,pixel,user);}
  int total=l->footer_step*5,x=(width-total)/2;
  for(int i=0;i<5;i++){int id=p.exact[i]==':'?32:22+p.exact[i]-'0';const ProseSprite*s=l->sprites+id;sprite(l,id,x+i*l->footer_step+(l->footer_step-s->w)/2,l->footer_top,170,monochrome,pixel,user);}
  for(int k=0;k<l->rule_length;k++){pixel(width/2-total/2-8-k,l->footer_top+l->footer_height/2,monochrome?255:85,user);pixel(width/2+total/2+7+k,l->footer_top+l->footer_height/2,monochrome?255:85,user);}
}
