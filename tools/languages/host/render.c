// Copyright 2026 Luke Steuber. MIT License.
#include "pebble.h"
#include "locale.h"
#include <stdio.h>
#include <string.h>
#include <assert.h>
static uint8_t *data,*pixels;static size_t length;static int w,h,mode;static bool mono;
ResHandle resource_get_handle(uint32_t id){return id;}
size_t resource_size(ResHandle r){(void)r;return length;}
size_t resource_load_byte_range(ResHandle r,uint32_t off,uint8_t*dst,size_t n){(void)r;if(off>length||n>length-off)return 0;memcpy(dst,data+off,n);return n;}
static void put(int x,int y,uint8_t g,void*u){(void)u;assert(x>=0&&y>=0&&x<w&&y<h);if(mode==2)g=255-g;if(!mono)g=((g+42)/85)*85;pixels[y*w+x]=g;}
int main(int argc,char**argv){assert(argc==3||argc==6);FILE*f=fopen(argv[1],"rb");assert(f);fseek(f,0,SEEK_END);length=ftell(f);rewind(f);data=malloc(length);assert(data);assert(fread(data,1,length,f)==length);fclose(f);w=data[4]+256*data[5];h=data[6]+256*data[7];mode=data[10];pixels=calloc(w*h,1);assert(pixels);if(argc==3){for(int m=0;m<1440;m++){memset(pixels,0,w*h);assert(locale_render(1,w,h,m/60,m%60,false,put,NULL));}size_t old=length;length=19;assert(!locale_render(1,w,h,0,0,false,put,NULL));length=old;data[0]='X';assert(!locale_render(1,w,h,0,0,false,put,NULL));puts("All 1440 minute projections and malformed headers passed");}else{mono=atoi(argv[4]);assert(locale_render(1,w,h,atoi(argv[2]),atoi(argv[3]),mono,put,NULL));f=fopen(argv[5],"wb");assert(f);fprintf(f,"P5\n%d %d\n255\n",w,h);assert(fwrite(pixels,1,w*h,f)==(size_t)(w*h));fclose(f);}free(data);free(pixels);return 0;}
