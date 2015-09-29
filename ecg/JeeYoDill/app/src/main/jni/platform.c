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

#include "platform.h"
#include "streamplot.h"

JNIEXPORT void JNICALL
Java_com_jeeyo_sagar_jeeyodill_PlatformJNIWrapper_init(JNIEnv* env, jclass this,
                                                       jobject jAssetManager,
                                                       int width, int height,
                                                       jobjectArray jPlotTypes,
                                                       jint showPlayPauseButton,
                                                       jintArray jResHandles)
{
    int i;
    int nPlots = (*env)->GetArrayLength(env, jPlotTypes);

    StreamplotType plotTypes[nPlots];

    for(i = 0; i < nPlots; i++) {
        jobject jPlotTypeObj = (jobject) (*env)->GetObjectArrayElement(env, jPlotTypes, i);
        jclass jPlotType = (*env)->GetObjectClass(env, jPlotTypeObj);

        plotTypes[i].color[0] = (*env)->GetFloatField(env, jPlotTypeObj, (*env)->GetFieldID(env, jPlotType, "mColorR", "F"));
        plotTypes[i].color[1] = (*env)->GetFloatField(env, jPlotTypeObj, (*env)->GetFieldID(env, jPlotType, "mColorG", "F"));
        plotTypes[i].color[2] = (*env)->GetFloatField(env, jPlotTypeObj, (*env)->GetFieldID(env, jPlotType, "mColorB", "F"));
        plotTypes[i].color[3] = (*env)->GetFloatField(env, jPlotTypeObj, (*env)->GetFieldID(env, jPlotType, "mColorA", "F"));

        plotTypes[i].thickness = (*env)->GetFloatField(env, jPlotTypeObj, (*env)->GetFieldID(env, jPlotType, "mThickness", "F"));
        plotTypes[i].style = (*env)->GetIntField(env, jPlotTypeObj, (*env)->GetFieldID(env, jPlotType, "mStyle", "I"));

    }

    jint* resHandles = (*env)->GetIntArrayElements(env, jResHandles, 0);

    StreamplotInit(nPlots, plotTypes, width, height, showPlayPauseButton, resHandles);

    (*env)->ReleaseIntArrayElements(env, jResHandles, resHandles, 0);

}

JNIEXPORT void JNICALL
Java_com_jeeyo_sagar_jeeyodill_PlatformJNIWrapper_mainLoop(JNIEnv* env, jclass this,
                                                           jfloatArray jdata,
                                                           jint event, jfloat evtX0, jfloat evtY0,
                                                           jfloat evtX1, jfloat evtY1,
                                                           jstring leftTop)
{
    int nDataPoints = (*env)->GetArrayLength(env, jdata);
    jfloat* data = (*env)->GetFloatArrayElements(env, jdata, 0);

    const char *strLeftTop = (*env)->GetStringUTFChars(env, leftTop, 0);

    StreamplotEvent evt = {
        event, evtX0, evtY0, evtX1, evtY1
    };
    StreamplotMainLoop(nDataPoints, data, evt, strLeftTop);

    (*env)->ReleaseFloatArrayElements(env, jdata, data, 0);
    (*env)->ReleaseStringUTFChars(env, leftTop, strLeftTop);
}

void printGLString(const char *name, GLenum s) {
    const char *v = (const char *) glGetString(s);
    LOGI("GL %s = %s\n", name, v);
}

void checkGlError(const char* op) {
    GLint error;
    for (error = glGetError(); error; error
            = glGetError()) {
        LOGI("after %s() glError (0x%x)\n", op, error);
    }
}