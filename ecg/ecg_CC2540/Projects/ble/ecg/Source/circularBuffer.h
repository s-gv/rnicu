#ifndef __CIRCBUF_H__
#define __CIRCBUF_H__

#include "OSAL.h"
#include<ioCC2540.h>

#define CIRCBUF_TYPE uint16

#define CIRCBUF_SIZE 32
#define CIRCBUF_SIZE_DTYPE uint8

#define DISABLE_INTERRUPTS IEN0 &= ~(0x80);
#define ENABLE_INTERRUPTS IEN0 |= 0x80;

typedef struct  {
  
  CIRCBUF_TYPE buf[CIRCBUF_SIZE];
  CIRCBUF_SIZE_DTYPE start;
  CIRCBUF_SIZE_DTYPE end;
  
} CircularBuffer;

void circBufferInit(volatile CircularBuffer* cbuf);
uint8 circBufferAdd(volatile CircularBuffer* cbuf, CIRCBUF_TYPE data); // returns 0 on success, 1 on full
uint8 circBufferRemove(volatile CircularBuffer* cbuf, CIRCBUF_TYPE* data); // returns 0 on success, 1 on empty

#endif