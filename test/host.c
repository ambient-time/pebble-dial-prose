// Copyright 2026 Luke Steuber. MIT License.
#include "../src/c/prose.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static uint8_t pixels[260*260];
static int width,height,mono;
static void pixel(int x,int y,uint8_t gray,void *user){(void)user;assert(x>=0&&y>=0&&x<width&&y<height);if(width==height){int dx=2*x+1-width,dy=2*y+1-height;assert(dx*dx+dy*dy<=(width-2)*(width-2));}pixels[y*width+x]=mono?(gray>=128?255:0):((gray+42)/85)*85;}
int main(int argc,char **argv){
 if(argc==2&&!strcmp(argv[1],"phrases")){for(int i=0;i<1440;i++){ProsePhrase p=prose_phrase(i/60,i%60);printf("%02d:%02d|",i/60,i%60);for(int j=0;j<p.count;j++)printf("%s%s",j?" ":"",prose_run_text(p.ids[j]));puts("");}return 0;}
 if(argc==2&&!strcmp(argv[1],"exhaustive")){
  const int sizes[][3]={{144,168,0},{144,168,1},{180,180,0},{200,228,0},{260,260,0}};
  for(unsigned k=0;k<sizeof(sizes)/sizeof(sizes[0]);k++){width=sizes[k][0];height=sizes[k][1];mono=sizes[k][2];assert(prose_bounds_errors(width,height)==0);for(int i=0;i<1440;i++){memset(pixels,0,sizeof(pixels));prose_render(width,height,i/60,i%60,mono,pixel,NULL);int count=0;for(int j=0;j<width*height;j++)count+=pixels[j]>0;assert(count>150);}}
  return 0;
 }
 assert(argc==7);width=atoi(argv[1]);height=atoi(argv[2]);mono=atoi(argv[5]);assert(width<=260&&height<=260);assert(prose_bounds_errors(width,height)==0);prose_render(width,height,atoi(argv[3]),atoi(argv[4]),mono,pixel,NULL);FILE*f=fopen(argv[6],"wb");assert(f);fprintf(f,"P5\n%d %d\n255\n",width,height);assert(fwrite(pixels,1,width*height,f)==(size_t)(width*height));fclose(f);return 0;
}
