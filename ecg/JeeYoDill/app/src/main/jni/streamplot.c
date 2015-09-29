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

#include "streamplot.h"


typedef struct Streamplot {
    GLfloat color[4];
    GLfloat thickness;
    GLfloat data[4*STREAMPLOT_N_MAX_POINTS];
    GLint style;
} Streamplot;

int nPlots;
int freeze = 0;
int gridEnabled;
int doubleTapCountDown;
int width, height;
int lastEvent;
float initPinchEventDx = 0;
float initPinchEventX = 0;
float lastTranX, lastScaleX;
int startPtr = STREAMPLOT_N_MAX_POINTS/2 - 800, endPtr = STREAMPLOT_N_MAX_POINTS/2 + 800;
int showPlayPause;
int lastFreeze;
//int startPtr = 0, endPtr = STREAMPLOT_N_MAX_POINTS;
int ptr;

Streamplot plots[STREAMPLOT_N_MAX_PLOTS];
GLfloat gridLinesH[4*STREAMPLOT_N_H_GRID_LINES], gridLinesHT[4*(STREAMPLOT_N_HT_GRID_LINES)];
GLfloat gridLinesV[4*STREAMPLOT_N_V_GRID_LINES], gridLinesVT[4*(STREAMPLOT_N_VT_GRID_LINES)];

GLfloat gMVPMatrix[16] = {
        1.0f, 0.0f, 0.0f, 0.0f,
        0.0f, 1.0f, 0.0f, 0.0f,
        0.0f, 0.0f, 1.0f, 0.0f,
        0.0f, 0.0f, 0.0f, 1.0f
    };

static GLfloat playPauseVertices[] = {
    -1.0f, -1.0f,
    -0.8f, -1.0f,
    -1.0f, -0.8f,
    -0.8f, -0.8f
};

static GLfloat playPauseTextureVertices[] = {
    0.0f,  0.0f,
    1.0f, 0.0f,
    0.0f,  1.0f,
    1.0f, 1.0f
};

GLuint gProgram, gProgramTexture;

GLuint gLineHandle;
GLuint gPointSizeHandle;
GLuint gMVPHandle;
GLuint gColorHandle;

GLuint gPauseButtonHandle;
GLuint gPlayButtonHandle;
GLuint gFontHandle;

GLuint gTexturePositionHandle;
GLuint gTextureCoordinateHandle;
GLuint gTextureUniformSamplerHandle;


static const char gVertexShader[] =
    "uniform mat4 u_MVPMatrix;\n"
    "uniform float u_PointSize;\n"
    "attribute vec4 vPosition;\n"
    "void main() {\n"
    "  gl_Position = u_MVPMatrix * vPosition;\n"
    "  gl_PointSize = u_PointSize;\n"
    "}\n";

static const char gFragmentShader[] =
    "precision lowp float;\n"
    "uniform vec4 u_Color;\n"
    "void main() {\n"
    "  gl_FragColor = u_Color;\n"
    "}\n";

static const char tVertexShader[] =
    "attribute vec4 vPosition;\n"
    "attribute vec2 vCoordinate;\n"
    "varying vec2 textureCoordinate;\n"
    "void main() {\n"
    "    gl_Position = vPosition;\n"
    "    textureCoordinate = vCoordinate;\n"
    "}\n";

static const char tFragmentShader[] =
    "precision lowp float;\n"
    "varying vec2 textureCoordinate;\n"
    "uniform sampler2D u_Texture;\n"
    "void main() {\n"
    "    gl_FragColor = texture2D(u_Texture, textureCoordinate);\n"
    "}\n";

static GLuint loadShader(GLenum shaderType, const char* pSource) {
    GLuint shader = glCreateShader(shaderType);
    if (shader) {
        glShaderSource(shader, 1, &pSource, NULL);
        glCompileShader(shader);
        GLint compiled = 0;
        glGetShaderiv(shader, GL_COMPILE_STATUS, &compiled);
        if (!compiled) {
            GLint infoLen = 0;
            glGetShaderiv(shader, GL_INFO_LOG_LENGTH, &infoLen);
            if (infoLen) {
                char* buf = (char*) malloc(infoLen);
                if (buf) {
                    glGetShaderInfoLog(shader, infoLen, NULL, buf);
                    LOGE("Could not compile shader %d:\n%s\n",
                            shaderType, buf);
                    free(buf);
                }
                glDeleteShader(shader);
                shader = 0;
            }
        }
    }
    return shader;
}

static GLuint createProgram(const char* pVertexSource, const char* pFragmentSource) {
    GLuint vertexShader = loadShader(GL_VERTEX_SHADER, pVertexSource);
    if (!vertexShader) {
        return 0;
    }

    GLuint pixelShader = loadShader(GL_FRAGMENT_SHADER, pFragmentSource);
    if (!pixelShader) {
        return 0;
    }

    GLuint program = glCreateProgram();
    if (program) {
        glAttachShader(program, vertexShader);
        checkGlError("glAttachShader");

        glAttachShader(program, pixelShader);
        checkGlError("glAttachShader");

        glLinkProgram(program);
        GLint linkStatus = GL_FALSE;
        glGetProgramiv(program, GL_LINK_STATUS, &linkStatus);
        if (linkStatus != GL_TRUE) {
            GLint bufLength = 0;
            glGetProgramiv(program, GL_INFO_LOG_LENGTH, &bufLength);
            if (bufLength) {
                char* buf = (char*) malloc(bufLength);
                if (buf) {
                    glGetProgramInfoLog(program, bufLength, NULL, buf);
                    LOGE("Could not link program:\n%s\n", buf);
                    free(buf);
                }
            }
            glDeleteProgram(program);
            program = 0;
        }
    }
    return program;
}

static void setYScale() {
    int i, j;
    float maxVal = -INFINITY, minVal = INFINITY, val, scaleY, tranY;

    for(i = 0;i < nPlots; i++) {
        for(j = startPtr; j < endPtr; j++) {
            val = plots[i].data[4*j + 1];
            if(val != INFINITY) {
                if(val > maxVal)
                    maxVal = val;
                if(val < minVal)
                    minVal = val;
            }
        }
    }

    float range = maxVal - minVal;
    float avg = (maxVal + minVal) / 2.0f;

    scaleY = gMVPMatrix[5];
    tranY = gMVPMatrix[13];

    float maxY = maxVal*scaleY + tranY;
    float minY = minVal*scaleY + tranY;

    if( (maxY > STREAMPLOT_SCALE_HI_THRESH) ||
        (minY < -STREAMPLOT_SCALE_HI_THRESH) ||
        ((range*scaleY) < (2.0f * STREAMPLOT_SCALE_LO_THRESH)))
    {
        scaleY = 2.0f * STREAMPLOT_SCALE_TARG_THRESH / (range + STREAMPLOT_EPS);
        if(maxVal == minVal) {
            scaleY = 1;
        }
        tranY = -1.0f * scaleY * avg;
    }
    gMVPMatrix[5] = scaleY;
    gMVPMatrix[13] = tranY;
}

static void clearScreen() {
    glClearColor(1.0f, 1.0f, 1.0f, 1.0f);
    checkGlError("glClearColor");

    glClear( GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT);
    checkGlError("glClear");
}

static void renderPlots() {
    int i;

    glUseProgram(gProgram);
    checkGlError("glUseProgram");

    for(i = 0; i < nPlots; i++) {
        // Draw the line

        glLineWidth(plots[i].thickness);
        checkGlError("glLineWidth");

        glVertexAttribPointer(gLineHandle, 2, GL_FLOAT, GL_FALSE, 0, plots[i].data);
        checkGlError("glVertexAttribPointer");

        glEnableVertexAttribArray(gLineHandle);
        checkGlError("glEnableVertexAttribArray");

        glUniformMatrix4fv(gMVPHandle, 1, GL_FALSE, gMVPMatrix);
        checkGlError("glUniformMatrix4fv");

        glUniform1f(gPointSizeHandle, plots[i].thickness);
        checkGlError("glUniform1f");

        glUniform4fv(gColorHandle, 1, plots[i].color);
        checkGlError("glUniform4fv");

        if(plots[i].style == STREAMPLOT_STYLE_2) {
            glDrawArrays(GL_POINTS, 0, 2*STREAMPLOT_N_MAX_POINTS);
        }
        else {
            glDrawArrays(GL_LINES, 0, 2*STREAMPLOT_N_MAX_POINTS);
        }
        checkGlError("glDrawArrays");

        // Draw the marker point
        GLfloat pointMarker[2] = {plots[i].data[ptr*4 + 2], plots[i].data[ptr*4 + 3]};
        glVertexAttribPointer(gLineHandle, 2, GL_FLOAT, GL_FALSE, 0, pointMarker);
        checkGlError("glVertexAttribPointer");

        glEnableVertexAttribArray(gLineHandle);
        checkGlError("glEnableVertexAttribArray");

        glUniformMatrix4fv(gMVPHandle, 1, GL_FALSE, gMVPMatrix);
        checkGlError("glUniformMatrix4fv");

        glUniform1f(gPointSizeHandle, 20.0f);
        checkGlError("glUniform1f");

        glDrawArrays(GL_POINTS, 0, 1);
        checkGlError("glDrawArrays");
    }
}
static void fillFontPositionVertices(float* fontPositionVertices, float bottomX, float bottomY, float deltaX, float deltaY) {
    fontPositionVertices[0] = bottomX+deltaX;   fontPositionVertices[1] = bottomY;
    fontPositionVertices[2] = bottomX;          fontPositionVertices[3] = bottomY;
    fontPositionVertices[4] = bottomX+deltaX;   fontPositionVertices[5] = bottomY+deltaY;
    fontPositionVertices[6] = bottomX;          fontPositionVertices[7] = bottomY+deltaY;
}
static void fillFontTextureVertices(float* fontTextureVertices, float xStart, float yStart, float xStep, float yStep) {
    fontTextureVertices[0] = xStart + xStep;    fontTextureVertices[1] = yStart + yStep;
    fontTextureVertices[2] = xStart;            fontTextureVertices[3] = yStart + yStep;
    fontTextureVertices[4] = xStart + xStep;    fontTextureVertices[5] = yStart;
    fontTextureVertices[6] = xStart;            fontTextureVertices[7] = yStart;
}
static void StreamplotPrint(const char* str, float locX, float locY) {
    GLfloat fontPositionVertices[8];
    GLfloat fontTextureVertices[8];

    float aspectRatio = width * 1.0f / height;
    float bottomX = locX;
    float bottomY = locY;
    float deltaY = 0.2f;
    float deltaX = 0.07f;


    //convert -background none -fill red -font LiberationMono-Regular.ttf -pointsize 100 label:"ABCDEFGH\nIJKLMNOP\nQRSTUVWX\nYZ012345\n6789" font.png
    while(*str != '\0') {
        fillFontPositionVertices(fontPositionVertices, bottomX, bottomY, deltaX, deltaY);
        int s=0, m=0;
        char c = *str;
        if(c >= 65 && c <= 90) {
            s = (c-65) % 8;
            m = (c-65) / 8;

        }
        if(c >= 48 && c <= 57) {
            s = (c - 48 + 2) % 8;
            m = 3 + (c - 48 + 2) / 8;
        }
        float startx = s / 8.0f;
        float starty = m / 5.0f;
        fillFontTextureVertices(fontTextureVertices, startx, starty, 0.125f, 0.2f);

        glUseProgram(gProgramTexture);
        checkGlError("glUseProgram");

        glActiveTexture(GL_TEXTURE0);
        checkGlError("glActiveTexture");

        glBindTexture(GL_TEXTURE_2D, gFontHandle);
        checkGlError("glBindTexture");

        glUniform1i(gTextureUniformSamplerHandle, 0);
        checkGlError("glUniform1i");

        glVertexAttribPointer(gTexturePositionHandle, 2, GL_FLOAT, GL_FALSE, 0, fontPositionVertices);
        checkGlError("glVertexAttribPointer");

        glEnableVertexAttribArray(gTexturePositionHandle);
        checkGlError("glEnableVertexAttribArray");

        glVertexAttribPointer(gTextureCoordinateHandle, 2, GL_FLOAT, GL_FALSE, 0, fontTextureVertices);
        checkGlError("glVertexAttribPointer");

        glEnableVertexAttribArray(gTextureCoordinateHandle);
        checkGlError("glEnableVertexAttribArray");

        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4);
        checkGlError("glDrawArrays");

        str++;
        bottomX += deltaX;
    }

}
void StreamplotInit(int numPlots, StreamplotType* plotTypes, int screenWidth, int screenHeight, int showPlayPauseButton, int* resHandles) {
    int i, j;
    // Init global vars
    freeze = 0;
    lastEvent = 0;
    doubleTapCountDown = 0;
    gridEnabled = 1;
    initPinchEventDx = 0;
    initPinchEventX = 0;
    lastTranX = 0.0f;
    lastScaleX = 0.0f;
    startPtr = STREAMPLOT_N_MAX_POINTS/2 - 600;
    endPtr = STREAMPLOT_N_MAX_POINTS/2 + 600;
    showPlayPause = 0;
    for(i = 0; i < 16; i++) {
        gMVPMatrix[i] = 0.0f;
    }
    gMVPMatrix[0] = 1.0f;
    gMVPMatrix[5] = 1.0f;
    gMVPMatrix[10] = 1.0f;
    gMVPMatrix[15] = 1.0f;

    // Start usual init now
    int w = screenWidth;
    int h = screenHeight;

    freeze = 0;
    lastFreeze = 0;

    showPlayPause = showPlayPauseButton;

    gPlayButtonHandle = resHandles[0];
    gPauseButtonHandle = resHandles[1];
    gFontHandle = resHandles[2];

    width = w;
    height = h;

    nPlots = numPlots;
    ptr = startPtr;

    float scaleX = (float)STREAMPLOT_N_MAX_POINTS * 1.0f / (endPtr - startPtr);
    gMVPMatrix[0] = scaleX;

    float aspectRatio = w * 1.0f / h;
    playPauseVertices[7] = -1.0f + (1.0f + playPauseVertices[2]) * aspectRatio;
    playPauseVertices[5] = -1.0f + (1.0f + playPauseVertices[2]) * aspectRatio;

    for(i = 0;i < nPlots; i++) {
        for(j = 0; j < 4; j++) {
            plots[i].color[j] = plotTypes[i].color[j];
        }
        plots[i].thickness = plotTypes[i].thickness;
        plots[i].style = plotTypes[i].style;

        for(j = 0;j < STREAMPLOT_N_MAX_POINTS;j++) {
            plots[i].data[4*j] = -1.0f + (j * 2.0f) / STREAMPLOT_N_MAX_POINTS;
            plots[i].data[4*j + 1] = 0.0f;

            plots[i].data[4*j + 2] = -1.0f + ((j+1) * 2.0f) / STREAMPLOT_N_MAX_POINTS;
            plots[i].data[4*j + 3] = 0.0f;
        }
    }

    for(i = 0; i < STREAMPLOT_N_H_GRID_LINES; i++) {
        float yLevel = STREAMPLOT_GRID_MIN + ((STREAMPLOT_GRID_MAX-STREAMPLOT_GRID_MIN)/STREAMPLOT_N_H_GRID_LINES) * i;

        gridLinesH[4*i] = -1.0f;
        gridLinesH[4*i + 1] = yLevel;

        gridLinesH[4*i + 2] = 1.0f;
        gridLinesH[4*i + 3] = yLevel;
    }
    for(i = 0; i < STREAMPLOT_N_HT_GRID_LINES; i++) {
        float yLevel = STREAMPLOT_GRID_MIN + ((STREAMPLOT_GRID_MAX-STREAMPLOT_GRID_MIN)/STREAMPLOT_N_HT_GRID_LINES) * i;

        gridLinesHT[4*i] = -1.0f;
        gridLinesHT[4*i + 1] = yLevel;

        gridLinesHT[4*i + 2] = 1.0f;
        gridLinesHT[4*i + 3] = yLevel;
    }
    for(i = 0; i < STREAMPLOT_N_V_GRID_LINES; i++) {
        float xLevel = -1.0f + (2.0f/STREAMPLOT_N_V_GRID_LINES) * i;

        gridLinesV[4*i] = xLevel;
        gridLinesV[4*i + 1] = STREAMPLOT_GRID_MIN;

        gridLinesV[4*i + 2] = xLevel;
        gridLinesV[4*i + 3] = STREAMPLOT_GRID_MAX;
    }
    for(i = 0; i < STREAMPLOT_N_VT_GRID_LINES; i++) {
        float xLevel = -1.0f + (2.0f/STREAMPLOT_N_VT_GRID_LINES) * i;

        gridLinesVT[4*i] = xLevel;
        gridLinesVT[4*i + 1] = STREAMPLOT_GRID_MIN;

        gridLinesVT[4*i + 2] = xLevel;
        gridLinesVT[4*i + 3] = STREAMPLOT_GRID_MAX;
    }

    LOGI("StreamplotInit(%d, %d)", w, h);

    gProgramTexture = createProgram(tVertexShader, tFragmentShader);
    if (!gProgramTexture) {
        LOGE("Could not create program.");
        return;
    }

    gProgram = createProgram(gVertexShader, gFragmentShader);
    if (!gProgram) {
        LOGE("Could not create program.");
        return;
    }

    gLineHandle = glGetAttribLocation(gProgram, "vPosition");
    checkGlError("glGetAttribLocation");

    gMVPHandle = glGetUniformLocation(gProgram, "u_MVPMatrix");
    checkGlError("glGetUniformLocation");

    gColorHandle = glGetUniformLocation(gProgram, "u_Color");
    checkGlError("glGetUniformLocation");

    gPointSizeHandle = glGetUniformLocation(gProgram, "u_PointSize");
    checkGlError("glGetUniformLocation");

    gTexturePositionHandle = glGetAttribLocation(gProgramTexture, "vPosition");
    checkGlError("glGetAttribLocation");

    gTextureCoordinateHandle = glGetAttribLocation(gProgramTexture, "vCoordinate");
    checkGlError("glGetAttribLocation");

    gTextureUniformSamplerHandle = glGetUniformLocation(gProgramTexture, "u_Texture");
    checkGlError("glGetUniformLocation");

    glViewport(0, 0, w, h);
    checkGlError("glViewport");
}

static void incrementPtr() {
    ptr = ptr + 1;
    if(ptr >= endPtr) {
        ptr = startPtr;
    }
}

static void processEvents(StreamplotEvent evt) {
    if(evt.event != 0) {
        //LOGI("Event: %d", evt.event);

        float scaleX = gMVPMatrix[0];
        float tranX = gMVPMatrix[12];
        float eventDx = abs(evt.eventX0 - evt.eventX1);

        // Pinch start
        if(evt.event == STREAMPLOT_EVENT_PINCH && lastEvent != STREAMPLOT_EVENT_PINCH) {
            initPinchEventX = -1 + (evt.eventX0 + evt.eventX1) / width;
            initPinchEventDx = eventDx;
            lastFreeze = freeze;
            freeze = 1;
            lastScaleX = scaleX;
            lastTranX = tranX;
            //LOGI("Pinch start-X: %f", initPinchEventX);
        }

        // Pinch in progress
        if(evt.event == STREAMPLOT_EVENT_PINCH && lastEvent == STREAMPLOT_EVENT_PINCH) {
            float relDx = (eventDx - initPinchEventDx) / width;
            float scaleFactor = 10.0f;
            if(relDx > 0) {
                scaleX = lastScaleX * (1 + scaleFactor*relDx);
            }
            else {
                scaleX = lastScaleX / (1 - scaleFactor*relDx);
            }
            tranX = initPinchEventX - ((initPinchEventX-lastTranX) / lastScaleX * scaleX);

            float xStart = (-1.0f - tranX) / scaleX;
            float xEnd = (1.0f - tranX) / scaleX;

            if(xStart < -1.0f) {
                tranX = -1 + scaleX;
            }
            if(xEnd > 1.0f) {
                tranX = 1 - scaleX;
            }

            xStart = (-1.0f - tranX) / scaleX;
            xEnd = (1.0f - tranX) / scaleX;

            //LOGI("xStart: %f", xStart);
            //LOGI("xEnd: %f", xEnd);

            if(xStart >= -1.0f && xEnd <= 1.0f && scaleX < STREAMPLOT_MAX_ZOOM) {
                gMVPMatrix[12] = tranX;
                gMVPMatrix[0] = scaleX;
            }
            scaleX = gMVPMatrix[0];
            tranX = gMVPMatrix[12];

            xStart = (-1.0f - tranX) / scaleX;
            xEnd = (1.0f - tranX) / scaleX;

            startPtr = (int)((xStart+1.0f)*STREAMPLOT_N_MAX_POINTS/2);
            endPtr = (int)((xEnd+1.0f)*STREAMPLOT_N_MAX_POINTS/2);

            if(startPtr < 0)
                startPtr = 0;

            if(endPtr > STREAMPLOT_N_MAX_POINTS)
                endPtr = STREAMPLOT_N_MAX_POINTS;

            if(ptr > endPtr || ptr < startPtr)
                ptr = startPtr;


            //LOGI("Pinch in Progress: %f", relDx);
        }

        // Pinch end
        if(evt.event == STREAMPLOT_EVENT_UP && lastEvent == STREAMPLOT_EVENT_PINCH) {
            freeze = lastFreeze;
            //LOGI("Pinch end");
        }

        // Plain touch release
        if(evt.event == STREAMPLOT_EVENT_UP && lastEvent != STREAMPLOT_EVENT_PINCH &&
           ((showPlayPause && evt.eventX0/width < 0.2 && evt.eventY0/height > 0.8) || !showPlayPause))
        {
            freeze = !freeze;
            if(doubleTapCountDown > 0) {
                gridEnabled = !gridEnabled;
            }
            doubleTapCountDown = 18;
        }
        lastEvent = evt.event;
    }
}

static void addData(int nDataPoints, float* data) {
    int i, j;
    int nPoints = nDataPoints / nPlots;

    assert(nPlots*nPoints == nDataPoints);
    if(!freeze) {
        for(i = 0;i < nPoints;i++) {
            int localLastPtr = ptr;
            incrementPtr();
            int localPtr = ptr;
            for(j = 0; j < nPlots; j++) {
                plots[j].data[localPtr*4 + 1] = plots[j].data[localLastPtr*4 + 3];
                plots[j].data[localPtr*4 + 3] = data[i*nPlots + j];
            }
        }
    }
}
static void renderGridLines(GLfloat* data, float thickness, int nLines) {
    GLfloat color[] = { 1.0f, 0.0f, 0.0f, 1.0f };

    glUseProgram(gProgram);
    checkGlError("glUseProgram");

    glLineWidth(thickness);
    checkGlError("glLineWidth");

    glVertexAttribPointer(gLineHandle, 2, GL_FLOAT, GL_FALSE, 0, data);
    checkGlError("glVertexAttribPointer");

    glEnableVertexAttribArray(gLineHandle);
    checkGlError("glEnableVertexAttribArray");

    glUniformMatrix4fv(gMVPHandle, 1, GL_FALSE, gMVPMatrix);
    checkGlError("glUniformMatrix4fv");

    glUniform1f(gPointSizeHandle, thickness);
    checkGlError("glUniform1f");

    glUniform4fv(gColorHandle, 1, color);
    checkGlError("glUniform4fv");

    glDrawArrays(GL_LINES, 0, 2*nLines);
    checkGlError("glDrawArrays");
}
static void renderGrid() {
    renderGridLines(gridLinesH, 1.0f, STREAMPLOT_N_H_GRID_LINES);
    renderGridLines(gridLinesHT, 3.0f, STREAMPLOT_N_HT_GRID_LINES);
    renderGridLines(gridLinesV, 1.0f, STREAMPLOT_N_V_GRID_LINES);
    renderGridLines(gridLinesVT, 3.0f, STREAMPLOT_N_VT_GRID_LINES);
}

static void renderPlayPauseButton()
{
    glUseProgram(gProgramTexture);
    checkGlError("glUseProgram");

    glActiveTexture(GL_TEXTURE0);
    checkGlError("glActiveTexture");

    if(freeze)
        glBindTexture(GL_TEXTURE_2D, gPlayButtonHandle);
    else
        glBindTexture(GL_TEXTURE_2D, gPauseButtonHandle);
    checkGlError("glBindTexture");

    glUniform1i(gTextureUniformSamplerHandle, 0);
    checkGlError("glUniform1i");

    glVertexAttribPointer(gTexturePositionHandle, 2, GL_FLOAT, GL_FALSE, 0, playPauseVertices);
    checkGlError("glVertexAttribPointer");

    glEnableVertexAttribArray(gTexturePositionHandle);
    checkGlError("glEnableVertexAttribArray");

    glVertexAttribPointer(gTextureCoordinateHandle, 2, GL_FLOAT, GL_FALSE, 0, playPauseTextureVertices);
    checkGlError("glVertexAttribPointer");

    glEnableVertexAttribArray(gTextureCoordinateHandle);
    checkGlError("glEnableVertexAttribArray");

    glDrawArrays(GL_TRIANGLE_STRIP, 0, 4);
    checkGlError("glDrawArrays");
}

void StreamplotMainLoop(int nDataPoints, float* data, StreamplotEvent evt, char* strLeftTop)
{
    if(doubleTapCountDown > 0)
        doubleTapCountDown--;

    processEvents(evt);

    addData(nDataPoints, data);

    setYScale();

    clearScreen();

    if(gridEnabled)
        renderGrid();

    renderPlots();

    if(showPlayPause)
        renderPlayPauseButton();

    StreamplotPrint(strLeftTop, -0.96f, 0.76f);
}
