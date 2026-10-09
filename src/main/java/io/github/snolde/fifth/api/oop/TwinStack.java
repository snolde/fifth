/*
 * SPDX-License-Identifier: FLIP-v3.1
 * Copyright (c) 2026 snolde
 * Contact: snolde@gmail.com
 * License: https://github.com/snolde/flip/blob/v3.1/LICENSE
 * @FLIPCOP0: https://github.com/snolde/fifth
 */

package io.github.snolde.fifth.api.oop;

public interface TwinStack {

    /**
     *
     * @param value int
     * @param fs boolean
     */
    void push(int value, boolean fs);

    /**
     *
     * @param fs boolean
     * @return topValue int
     */
    int pop(boolean fs);

    /**
     *
     * @param value int
     * @param fs boolean
     */
    void put(int value, boolean fs);

    /**
     *
     * @param fs boolean
     * @return lastValue int
     */
    int take(boolean fs);

    /**
     *
     * @param depth int
     * @param fs boolean
     * @return valueAtDepth int
      */
    int pick( int depth, boolean fs );

    /**
     * Get current stack or fstack depth (0 empty)
     * @param fs boolean
     * @return depth int
     */
    int depth(boolean fs);


}

