// Copyright 2026 Luke Steuber. MIT License.
#include "locale.h"
#include "tinf.h"
#include <pebble.h>
#include <string.h>
typedef struct {ResHandle handle;uint32_t size,sprites,data;int w,h,count,mode,block;uint32_t stored;uint16_t blocks;bool packed,mono;LocalePixel pixel;void*user;} Scene;
typedef struct {uint32_t offset,length;int w,h,x,y;uint8_t ink,role;} Sprite;
static uint16_t u16(const uint8_t*p){return p[0]|((uint16_t)p[1]<<8);}
static uint32_t u32(const uint8_t*p){return u16(p)|((uint32_t)u16(p+2)<<16);}
// Independent deflate blocks bound working memory and permit random sprite reads.
static uint8_t expanded[8192],compressed[8210];
static bool raw_read(Scene*s,uint32_t off,uint8_t*dst,size_t n){return off<=s->stored&&n<=s->stored-off&&resource_load_byte_range(s->handle,off,dst,n)==n;}
static bool init_scene(Scene*s){uint8_t h[28];s->stored=resource_size(s->handle);s->size=s->stored;s->block=-1;if(!raw_read(s,0,h,20))return false;if(memcmp(h,"MZ01",4))return true;if(!raw_read(s,0,h,sizeof h)||u16(h+24)!=8192)return false;s->packed=true;s->size=u32(h+20);s->blocks=u16(h+26);return s->size>0&&s->size<=131072&&s->blocks==(s->size+8191)/8192;}
static bool read_bytes(Scene*s,uint32_t off,uint8_t*dst,size_t n){
 if(off>s->size||n>s->size-off)return false;
 if(!s->packed)return raw_read(s,off,dst,n);
 while(n){unsigned block=off/8192,within=off%8192;if((int)block!=s->block){uint8_t pair[8];if(block>=s->blocks||!raw_read(s,28+block*4,pair,8))return false;uint32_t start=u32(pair),end=u32(pair+4);if(start<28u+4u*(s->blocks+1u)||end<=start||end-start>sizeof compressed||!raw_read(s,start,compressed,end-start))return false;unsigned int length=s->size-block*8192;if(length>8192)length=8192;unsigned int expected=length;if(tinf_uncompress(expanded,&length,compressed,end-start)!=TINF_OK||length!=expected)return false;s->block=(int)block;}size_t take=8192-within;if(take>n)take=n;memcpy(dst,expanded+within,take);off+=take;dst+=take;n-=take;}
 return true;
}
static bool sprite_info(Scene*s,int id,Sprite*p){uint8_t b[18];if(id<0||id>=s->count||!read_bytes(s,s->sprites+id*18,b,sizeof b))return false;p->offset=u32(b);p->length=u32(b+4);p->w=u16(b+8);p->h=u16(b+10);p->x=(int16_t)u16(b+12);p->y=(int16_t)u16(b+14);p->ink=b[16];p->role=b[17];return p->w>0&&p->h>0&&p->w<=s->w&&p->h<=s->h&&p->offset<=s->size-s->data&&p->length<=s->size-s->data-p->offset;}
static void dot(Scene*s,int x,int y,uint8_t gray){if(x<1||y<1||x>=s->w-1||y>=s->h-1)return;if(s->w==s->h){int dx=2*x+1-s->w,dy=2*y+1-s->h,r=s->w-2;if(dx*dx+dy*dy>r*r)return;}s->pixel(x,y,gray,s->user);}
static void rect(Scene*s,int x,int y,int w,int h,uint8_t g){for(int yy=y;yy<y+h;yy++)for(int xx=x;xx<x+w;xx++)dot(s,xx,yy,g);}
static void line(Scene*s,int x,int y,int ex,int ey,uint8_t g){int dx=abs(ex-x),dy=-abs(ey-y),sx=x<ex?1:-1,sy=y<ey?1:-1,err=dx+dy;for(;;){dot(s,x,y,g);if(x==ex&&y==ey)break;int e=2*err;if(e>=dy){err+=dy;x+=sx;}if(e<=dx){err+=dx;y+=sy;}}}
static void circle(Scene*s,int cx,int cy,int r,uint8_t g){int x=r,y=0,err=0;while(x>=y){dot(s,cx+x,cy+y,g);dot(s,cx+y,cy+x,g);dot(s,cx-y,cy+x,g);dot(s,cx-x,cy+y,g);dot(s,cx-x,cy-y,g);dot(s,cx-y,cy-x,g);dot(s,cx+y,cy-x,g);dot(s,cx+x,cy-y,g);y++;err+=1+2*y;if(2*(err-x)+1>0){x--;err+=1-2*x;}}}
static bool paint(Scene*s,Sprite*p,int x,int y,uint8_t ink,uint8_t bg,bool transparent){uint8_t buf[128];uint32_t used=0,pos=0,total=p->w*p->h;while(used<p->length){size_t n=p->length-used;if(n>sizeof buf)n=sizeof buf;if(!read_bytes(s,s->data+p->offset+used,buf,n))return false;used+=n;for(size_t k=0;k<n;k++){unsigned level=buf[k]>>6,len=(buf[k]&63)+1;if(len>total-pos)return false;for(unsigned j=0;j<len;j++,pos++){if(transparent&&!level)continue;uint8_t gray=transparent?(s->mono?255:level*ink/3):((3-level)*bg+level*ink)/3;dot(s,x+pos%p->w,y+pos/p->w,gray);}}}return pos==total;}
bool locale_render(uint32_t resource,int width,int height,int hour,int minute,bool mono,LocalePixel pixel,void*user){Scene s={.handle=resource_get_handle(resource),.w=width,.h=height,.mono=mono,.pixel=pixel,.user=user};if(!init_scene(&s))return false;uint8_t header[20];if(!read_bytes(&s,0,header,sizeof header)||memcmp(header,"ML01",4)||u16(header+4)!=width||u16(header+6)!=height)return false;s.count=u16(header+8);s.mode=u16(header+10);s.sprites=u32(header+12);s.data=u32(header+16);if(s.data>s.size||s.sprites>s.data||s.count>256)return false;unsigned slot=((hour%24+24)%24)*12+((minute%60+60)%60)/5;
 if(s.mode==1){uint8_t f[37];if(!read_bytes(&s,20+slot*37,f,sizeof f)||f[0]>6)return false;for(int i=0;i<f[0];i++){Sprite p;uint8_t*b=f+1+i*6;if(!sprite_info(&s,u16(b),&p)||!paint(&s,&p,(int16_t)u16(b+2),(int16_t)u16(b+4),p.ink,0,true))return false;}return true;}
 if(s.mode!=2){return false;}
 uint8_t f[17];if(!read_bytes(&s,20+slot*17,f,sizeof f)||f[0]>8)return false;uint16_t ids[8];for(int i=0;i<f[0];i++){ids[i]=u16(f+1+i*2);if(ids[i]>=s.count)return false;}rect(&s,0,0,width,height,255);int cx=width/2,cy=height/2;circle(&s,cx,cy,width*34/100,170);int px=cx,py=cy;
 for(int i=0;i<f[0];i++){Sprite p;if(!sprite_info(&s,ids[i],&p))return false;int nx=p.x+p.w/2,ny=p.y+p.h/2,mx=(px+nx)/2,my=(py+ny)/2,qx=mx+(cx-mx)/4,qy=my+(cy-my)/4,lx=px,ly=py;for(int t=1;t<=20;t++){int a=20-t,x=(a*a*px+2*a*t*qx+t*t*nx)/400,y=(a*a*py+2*a*t*qy+t*t*ny)/400;line(&s,lx,ly,x,y,170);lx=x;ly=y;}px=nx;py=ny;}
 for(int pass=0;pass<2;pass++)for(int i=0;i<s.count;i++){Sprite p;if(!sprite_info(&s,i,&p))return false;if((p.role&127)==0)continue;bool on=false;for(int j=0;j<f[0];j++)if(ids[j]==i)on=true;if((p.role&128)&&!on)continue;if(on!=(pass==1))continue;if(on){rect(&s,p.x-2,p.y-2,p.w+4,p.h+4,255);line(&s,p.x-2,p.y-2,p.x+p.w+1,p.y-2,85);line(&s,p.x-2,p.y+p.h+1,p.x+p.w+1,p.y+p.h+1,85);line(&s,p.x-2,p.y-2,p.x-2,p.y+p.h+1,85);line(&s,p.x+p.w+1,p.y-2,p.x+p.w+1,p.y+p.h+1,85);}if(!paint(&s,&p,p.x,p.y,on?0:170,255,false))return false;}
 for(int i=0;i<s.count;i++){Sprite p;if(!sprite_info(&s,i,&p))return false;if((p.role&127)==0){bool any_alt=false,on=false;for(int k=0;k<f[0];k++){Sprite other;if(!sprite_info(&s,ids[k],&other))return false;if(other.role==128)any_alt=true;if(ids[k]==i)on=true;}if((p.role==0&&any_alt)||(p.role==128&&!on))continue;rect(&s,p.x-3,p.y-3,p.w+6,p.h+6,255);if(!paint(&s,&p,p.x,p.y,0,255,false))return false;}}return true;
}
