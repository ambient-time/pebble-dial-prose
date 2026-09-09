#pragma once
#include <stdint.h>
#include <stddef.h>
#include <stdlib.h>
typedef unsigned ResHandle;
ResHandle resource_get_handle(uint32_t id);
size_t resource_size(ResHandle h);
size_t resource_load_byte_range(ResHandle h,uint32_t start,uint8_t*dst,size_t length);
