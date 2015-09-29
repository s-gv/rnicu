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

public class StreamplotType {

    public static final int COLOR_BLUE = 0;
    public static final int COLOR_PURPLE = 1;
    public static final int COLOR_GREEN = 2;
    public static final int COLOR_YELLOW = 3;
    public static final int COLOR_RED = 4;
    public static final int COLOR_BLACK = 5;

    public static final int STYLE_LINE_1 = 1;
    public static final int STYLE_POINT_1 = 2;

    public float mColorR;
    public float mColorG;
    public float mColorB;
    public float mColorA;

    public float mThickness;
    public int mStyle;

    public StreamplotType() {
        mStyle = STYLE_LINE_1;
        mThickness = 5.0f;
    }

    public StreamplotType(int color) {
        setColor(color);
        mStyle = STYLE_LINE_1;
        mThickness = 5.0f;
    }
    public StreamplotType(int style, int color) {
        setColor(color);
        mStyle = style;
        mThickness = 5.0f;
    }
    public StreamplotType(int style, int color, float thickness) {
        setColor(color);
        mStyle = style;
        mThickness = thickness;
    }

    public void setColor(int color) {
        switch(color) {
            case COLOR_RED:
                mColorR = 1.0f;
                mColorG = 0.267f;
                mColorB = 0.267f;
                break;

            case COLOR_BLUE:
                mColorR = 0.2f;
                mColorG = 0.71f;
                mColorB = 0.898f;
                break;

            case COLOR_PURPLE:
                mColorR = 0.667f;
                mColorG = 0.4f;
                mColorB = 0.8f;
                break;

            case COLOR_GREEN:
                mColorR = 0.6f;
                mColorG = 0.8f;
                mColorB = 0.0f;
                break;

            case COLOR_YELLOW:
                mColorR = 1.0f;
                mColorG = 0.733f;
                mColorB = 0.2f;
                break;

            case COLOR_BLACK:
                mColorR = 0.0f;
                mColorG = 0.0f;
                mColorB = 0.0f;
                break;

            default:
                mColorR = 1.0f;
                mColorG = 1.0f;
                mColorB = 1.0f;
                break;
        }
        mColorA = 1.0f;
    }
}
