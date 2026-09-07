// Copyright 2026 Luke Steuber. MIT License.
#pragma once
#include <stdbool.h>
#include <stdint.h>
typedef struct { uint8_t ids[4], count; } ProsePhrase;
typedef void (*ProsePixel)(int x, int y, uint8_t gray, void *user);
ProsePhrase prose_phrase(int hour, int minute);
const char *prose_run_text(int id);
int prose_bounds_errors(int width, int height);
void prose_render(int width, int height, int hour, int minute, bool monochrome, ProsePixel pixel, void *user);
