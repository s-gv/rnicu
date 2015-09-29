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
package com.jeeyo.sagar.jeeyodill;

import android.app.Activity;
import android.content.res.AssetManager;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.opengl.GLES20;
import android.opengl.GLSurfaceView;
import android.opengl.GLUtils;
import android.util.Log;

import java.util.Queue;
import java.util.concurrent.ConcurrentLinkedQueue;

import javax.microedition.khronos.egl.EGLConfig;
import javax.microedition.khronos.opengles.GL10;

/**
 * Created by sagar on 28/1/15.
 */
public class RendererWrapper implements GLSurfaceView.Renderer {

    public static final int EVENT_DOWN = 1;
    public static final int EVENT_UP = 2;
    public static final int EVENT_PINCH = 3;

    private Activity mActivity;

    public float mEventX1;
    public float mEventX0;
    public float mEventY1;
    public float mEventY0;
    public int mEvent;

    ConcurrentLinkedQueue<Float> mQueue = new ConcurrentLinkedQueue<>();

    public RendererWrapper(Activity activity) {
        mActivity = activity;
    }

    @Override
    public void onSurfaceCreated(GL10 gl, EGLConfig config) {

    }

    @Override
    public void onSurfaceChanged(GL10 gl, int width, int height) {
        StreamplotType[] plotTypes = new StreamplotType[1];

        plotTypes[0] = new StreamplotType(StreamplotType.COLOR_BLACK);
        //plotTypes[1] = new StreamplotType(StreamplotType.STYLE_POINT_1, StreamplotType.COLOR_GREEN, 2.0f);

        PlatformJNIWrapper.StreamplotInit(mActivity, width, height, plotTypes, false);
    }
    private static int ECG_SAMPLE_RATE = 400;
    private float mECGLastData;
    private float mECGThresh = 100;
    private Boolean mECGmode = false;
    private float mECGmaxHiPass = 0;

    private int mECGLastMaxidx = 0;
    private int mECGMaxidx = 0;
    private int mECGidx = 0;
    private int mECGHr = 0;

    public void processData(float data) {
        float hiPass = Math.abs(data - mECGLastData);
        if (hiPass > mECGThresh) {
            mECGmode = true;
            if(hiPass > mECGmaxHiPass) {
                mECGmaxHiPass = hiPass;
                mECGMaxidx = mECGidx;
            }
        } else if(hiPass < mECGThresh/2) {
            if(mECGmode) {
                mECGThresh = mECGmaxHiPass;
                int hr = ECG_SAMPLE_RATE * 60 /(mECGMaxidx - mECGLastMaxidx + 1);
                if(hr > 30 && hr < 250) {
                    mECGHr = hr;
                }
                mECGLastMaxidx = mECGMaxidx;
                mECGmaxHiPass = 0;
            }
            mECGThresh = mECGThresh * 0.998f;
            mECGmode = false;
        }

        mECGidx = mECGidx + 1;
        mECGLastData = data;
    }
    @Override
    public void onDrawFrame(GL10 gl) {
        int size = mQueue.size();
        float[] data = new float[size];
        for(int i = 0; i < size; i++) {
            data[i] = -mQueue.poll();
            //Log.d("BLE", String.valueOf(data[i]));
            processData(data[i]);
        }
        PlatformJNIWrapper.mainLoop(data, mEvent, mEventX0, mEventY0, mEventX1, mEventY1, String.valueOf(mECGHr));
        //PlatformJNIWrapper.mainLoop(testData(), mEvent, mEventX0, mEventY0, mEventX1, mEventY1, "97");
        //PlatformJNIWrapper.mainLoop(testData2(), mEvent, mEventX0, mEventY0, mEventX1, mEventY1, "87");
        mEvent = 0; // clear the event
    }

    int mN = 0;
    float mScale = 3.0f;
    private float[] testData() {
        int nPoints = 6;
        float[] data = new float[2*nPoints];
        int max = 253;
        for(int i = 0; i < nPoints; i++) {
            data[2*i] = mScale * mN;
            data[2*i+1] = (-500.0f + (mN + max/2) % max);
            mN++;
            if(mN == max) {
                mN = 0;
                if(mScale == 3.0f)
                    mScale = 6.0f;
                else
                    mScale = 3.0f;
            }
        }
        return data;
    }

    int testIdx = 0;
    private float[] testData2() {
        int nPoints = 6;
        float[] data = new float[nPoints];
        for(int i = 0; i < nPoints; i++) {
            data[i] = -8191 + 50.0f * (testIdx++);
            if (testIdx == 253)
                testIdx = 0;
        }
        return data;
    }

    public void addDataPoint(int val) {
        float v;
        if(val < 8192 || val >= 65530) {
            v = (float) val;
        } else {
            v = (float) -val;
        }
        if(v < 65530) {
            mQueue.add(v);
        }
    }
}
