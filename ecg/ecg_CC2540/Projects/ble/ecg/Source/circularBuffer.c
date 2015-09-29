#include "circularBuffer.h"


void circBufferInit(volatile CircularBuffer* cbuf)
{
  cbuf->start = 0;
  cbuf->end = 0;
}

uint8 circBufferAdd(volatile CircularBuffer* cbuf, CIRCBUF_TYPE data)
{
  DISABLE_INTERRUPTS;
  
  CIRCBUF_SIZE_DTYPE start = cbuf->start;
  CIRCBUF_SIZE_DTYPE end = cbuf->end;
  
  if( ((end + 1) % CIRCBUF_SIZE) == start )
  {
    // buffer is full
    ENABLE_INTERRUPTS;
    return 1;
  }
  cbuf->buf[end] = data;
  cbuf->end = (end + 1) % CIRCBUF_SIZE;
  
  ENABLE_INTERRUPTS;
  return 0;
}

uint8 circBufferRemove(volatile CircularBuffer* cbuf, CIRCBUF_TYPE* data)
{
  DISABLE_INTERRUPTS;
  
  CIRCBUF_SIZE_DTYPE start = cbuf->start;
  CIRCBUF_SIZE_DTYPE end = cbuf->end;
  
  if( start == end )
  {
    *data = 65535;
    ENABLE_INTERRUPTS;
    return 1;
  }
  *data = cbuf->buf[start];
  cbuf->start = (start + 1) % CIRCBUF_SIZE;
  
  ENABLE_INTERRUPTS;
  return 0;
}