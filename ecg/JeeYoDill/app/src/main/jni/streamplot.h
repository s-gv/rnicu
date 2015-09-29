/*
Copyright (c) 2015, Sagar Gubbi <sagar.writeme@gmail.com>
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of JeeYo nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#ifndef __STREAMPLOT_H__
#define __STREAMPLOT_H__

#include "platform.h"

#include <jni.h>
#include <android/log.h>

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <assert.h>

#ifdef __cplusplus
extern "C" {
#endif

#define STREAMPLOT_N_MAX_PLOTS 10
#define STREAMPLOT_N_MAX_POINTS 3200

#define STREAMPLOT_MAX_ZOOM 15.0f

#define STREAMPLOT_EPS 1e-6

#define STREAMPLOT_SCALE_HI_THRESH 0.99f
#define STREAMPLOT_SCALE_LO_THRESH 0.25f
#define STREAMPLOT_SCALE_TARG_THRESH 0.7f

#define STREAMPLOT_COLOR_RED 1
#define STREAMPLOT_COLOR_BLUE 2
#define STREAMPLOT_COLOR_GREEN 3

#define STREAMPLOT_STYLE_1 1
#define STREAMPLOT_STYLE_2 2

#define STREAMPLOT_EVENT_DOWN 1
#define STREAMPLOT_EVENT_UP 2
#define STREAMPLOT_EVENT_PINCH 3

#define STREAMPLOT_N_H_GRID_LINES 120
#define STREAMPLOT_N_HT_GRID_LINES (STREAMPLOT_N_H_GRID_LINES/5)
#define STREAMPLOT_N_V_GRID_LINES 400
#define STREAMPLOT_N_VT_GRID_LINES (STREAMPLOT_N_V_GRID_LINES/5)
#define STREAMPLOT_GRID_MIN -32768.0f
#define STREAMPLOT_GRID_MAX 32768.0f

typedef struct StreamplotType {
    GLfloat color[4];
    GLfloat thickness;
    GLint style
} StreamplotType;

typedef struct StreamplotEvent {
    int event;
    float eventX0, eventY0;
    float eventX1, eventY1;
} StreamplotEvent;

void StreamplotInit(int numPlots, StreamplotType* plotTypes, int screenWidth, int screenHeight, int showPlayPauseButton, int* resHandles);


// data is layed out like:
// [
//    (ch0_data0, ch_1_data0, ch_2_data0),
//    (ch0_data1, ch_1_data1, ch_2_data1),
//    (ch0_data2, ch_1_data2, ch_2_data2),
//    (ch0_data3, ch_1_data3, ch_2_data3),
// ]
// nDataPoints = 12 in the above case
void StreamplotMainLoop(int nDataPoints, float* data, StreamplotEvent evt, char* strLeftTop);

#ifdef __cplusplus
}
#endif
#endif