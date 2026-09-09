// Copyright 2026 Luke Steuber. MIT License.
#pragma once
#include <stdbool.h>
#include <stdint.h>
typedef void (*LocalePixel)(int,int,uint8_t,void*);
bool locale_render(uint32_t resource,int width,int height,int hour,int minute,bool mono,LocalePixel pixel,void*user);
