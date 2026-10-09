/*
 * SPDX-License-Identifier: FLIP-v3.1
 * Copyright (c) 2026 snolde
 * Contact: snolde@gmail.com
 * License: https://github.com/snolde/flip/blob/v3.1/LICENSE
 * @FLIPCOP0: https://github.com/snolde/fifth
 */

package io.github.snolde.fifth.util;

public final class Util {

    /**
     * Next power of two for stack/queue size, min 8
     *
     * @param n int
     * @return int
     */
    public static int nextPOT(int n){
        return n < 8 ? 8 : Integer.highestOneBit(n - 1 ) << 1;
    }

    /**
     * Returns a new integer array to back data or flow stack
     *
     * @param minsize int
     * @return int[nextPOT(minsize)]
     */
    public static int[] getStack(int minsize){
        return new int[nextPOT(minsize)];
    }

    /**
     *
     * @param cell int
     * @return int
     */
    public static int payload(int cell) {
        return cell & 0xFFFFFFF;
    }

    /**
     *
     * @param cell int
     * @return int
     */
    public static int tagBits(int cell){
        return cell >> 28;
    }

    /**
     *
     * @param payload iny
     * @param tag int
     * @return int
     */
    public static int cell(int payload, int tag ){
        return payload & 0xFFFFFFF | ( tag << 28 );
    }

    /**
     *
     * @param pattern int
     * @param payload int
     * @return int
     */
    public static int fitPayload(int pattern, int payload){
        return pattern & 0xF0000000 | payload;
    }

}
