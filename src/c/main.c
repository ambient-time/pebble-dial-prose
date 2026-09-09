// Copyright 2026 Luke Steuber. MIT License.
#include <pebble.h>
#include "theme.h"
uint8_t face_theme;
#include "locale.h"
#include "language-resources.h"
static unsigned s_language;
#include "prose.h"
static Window *s_window;
static Layer *s_layer;
static bool s_focused;
typedef struct {GBitmap *frame;} Destination;
static void put_pixel(int x,int y,uint8_t gray,void *user){
 Destination*d=user;GBitmapDataRowInfo row=gbitmap_get_data_row_info(d->frame,y);if(x<row.min_x||x>row.max_x)return;
#ifdef PBL_COLOR
 uint32_t bg=theme_colors[face_theme][THEME_BG],ink=theme_colors[face_theme][THEME_INK];
 uint8_t rgb[3];for(int i=0;i<3;i++){int shift=16-i*8;int a=(bg>>shift)&255,b=(ink>>shift)&255;int v=a+(b-a)*gray/255;rgb[i]=((v+42)/85)*85;}
 row.data[x]=GColorFromRGB(rgb[0],rgb[1],rgb[2]).argb;
#else
 if(gray>=128){if(theme_light[face_theme])row.data[x/8]&=~(1u<<(x%8));else row.data[x/8]|=(1u<<(x%8));}
#endif
}
static void draw(Layer*layer,GContext*ctx){
 APP_LOG(APP_LOG_LEVEL_INFO,"Language frame=%u",s_language);time_t begin;uint16_t begin_ms;time_ms(&begin,&begin_ms);time_t now=time(NULL);struct tm t=*localtime(&now);GRect b=layer_get_bounds(layer);
 graphics_context_set_fill_color(ctx,theme_color(THEME_BG));graphics_fill_rect(ctx,b,0,GCornerNone);
 GBitmap*frame=graphics_capture_frame_buffer(ctx);if(!frame){APP_LOG(APP_LOG_LEVEL_ERROR,"Prose frame unavailable");return;}
 Destination d={frame};if(!s_language)prose_render(b.size.w,b.size.h,t.tm_hour,t.tm_min,PBL_IF_COLOR_ELSE(false,true),put_pixel,&d);else if(!locale_render(language_resources[s_language],b.size.w,b.size.h,t.tm_hour,t.tm_min,PBL_IF_COLOR_ELSE(false,true),put_pixel,&d))APP_LOG(APP_LOG_LEVEL_ERROR,"Locale render failed");graphics_release_frame_buffer(ctx,frame);
 ProsePhrase p=prose_phrase(t.tm_hour,t.tm_min);time_t end;uint16_t end_ms;time_ms(&end,&end_ms);
 APP_LOG(APP_LOG_LEVEL_INFO,"Prose time=%02d:%02d:%02d ids=%d,%d,%d,%d count=%d frame_ms=%ld free=%lu",t.tm_hour,t.tm_min,t.tm_sec,p.ids[0],p.ids[1],p.ids[2],p.ids[3],p.count,(long)((end-begin)*1000+end_ms-begin_ms),(unsigned long)heap_bytes_free());
}
static void inbox(DictionaryIterator*iter,void*context){
 (void)context;theme_receive(iter);int32_t value;
 if(theme_integer(dict_find(iter,MESSAGE_KEY_LANGUAGE),&value)&&value>=0&&value<LANGUAGE_COUNT){
  if(value==(int32_t)s_language||persist_write_int(301,value)==(int)sizeof(int32_t))s_language=value;
  APP_LOG(APP_LOG_LEVEL_INFO,"Language saved=%u",s_language);
 }
 if(s_layer)layer_mark_dirty(s_layer);
 DictionaryIterator*out;if(app_message_outbox_begin(&out)==APP_MSG_OK&&out){dict_write_uint8(out,MESSAGE_KEY_THEME,face_theme);dict_write_uint8(out,MESSAGE_KEY_LANGUAGE,s_language);app_message_outbox_send();}
}
static void tick(struct tm*time,TimeUnits units){(void)time;(void)units;if(s_focused&&s_layer)layer_mark_dirty(s_layer);}
static void focus(bool focused){s_focused=focused;if(focused&&s_layer)layer_mark_dirty(s_layer);}
static void load(Window*window){Layer*root=window_get_root_layer(window);s_layer=layer_create(layer_get_bounds(root));if(!s_layer){APP_LOG(APP_LOG_LEVEL_ERROR,"Prose layer allocation failed");return;}layer_set_update_proc(s_layer,draw);layer_add_child(root,s_layer);}
static void unload(Window*window){(void)window;if(s_layer)layer_destroy(s_layer);s_layer=NULL;}
int main(void){theme_restore();int saved=persist_read_int(301);if(persist_exists(301)&&saved>=0&&saved<LANGUAGE_COUNT)s_language=saved;app_message_register_inbox_received(inbox);app_message_open(128,128);APP_LOG(APP_LOG_LEVEL_INFO,"Language boot=%u",s_language);s_window=window_create();if(!s_window)return 1;window_set_background_color(s_window,GColorBlack);window_set_window_handlers(s_window,(WindowHandlers){.load=load,.unload=unload});s_focused=true;window_stack_push(s_window,false);tick_timer_service_subscribe(MINUTE_UNIT,tick);app_focus_service_subscribe(focus);app_event_loop();s_focused=false;tick_timer_service_unsubscribe();app_focus_service_unsubscribe();window_destroy(s_window);return 0;}
