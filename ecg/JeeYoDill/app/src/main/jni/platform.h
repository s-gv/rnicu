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

#include <jni.h>
#include <GLES2/gl2.h>
#include <GLES2/gl2ext.h>
#include <android/log.h>

#ifndef _Included_com_jeeyo_sagar_jeeyodill_StreamplotJNIWrapper
#define _Included_com_jeeyo_sagar_jeeyodill_StreamplotJNIWrapper
#ifdef __cplusplus
extern "C" {
#endif


#define  LOG_TAG    "libgl2jni"
#define  LOGI(...)  __android_log_print(ANDROID_LOG_INFO,LOG_TAG,__VA_ARGS__)
#define  LOGE(...)  __android_log_print(ANDROID_LOG_ERROR,LOG_TAG,__VA_ARGS__)

void printGLString(const char *name, GLenum s);
void checkGlError(const char* op);

JNIEXPORT void JNICALL
Java_com_jeeyo_sagar_jeeyodill_PlatformJNIWrapper_init(JNIEnv* env, jclass this,
                                                       jobject jAssetManager,
                                                       int width, int height,
                                                       jobjectArray jPlotTypes,
                                                       jint showPlayPauseButton,
                                                       jintArray resHandles);

JNIEXPORT void JNICALL
Java_com_jeeyo_sagar_jeeyodill_PlatformJNIWrapper_mainLoop(JNIEnv* env, jclass this,
                                                           jfloatArray jdata,
                                                           jint event, jfloat evtX0, jfloat evtY0,
                                                           jfloat evtX1, jfloat evtY1,
                                                           jstring leftTop);


#ifdef __cplusplus
}
#endif
#endif
