package io.github.snolde.fifth.util;

/*
 * SPDX-License-Identifier: FLIP-v3.0
 * Copyright (c) 2026 snolde
 * Contact: snolde@gmail.com
 * License: https://github.com/snolde/flip/blob/v3.0/LICENSE
 * @FLIPCOP0: https://github.com/snolde/fifth
 */

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class UtilTest {

    @Test
    void nextPOT() {
        assertEquals (32,Util.nextPOT(20),"Next power of two for 20 should be 32.");
        assertEquals(8,Util.nextPOT(1));
        assertEquals(8,Util.nextPOT(3));
    }

    @Test
    void getStack() {
        assertEquals(8, Util.getStack(7).length);
        assertEquals(32, Util.getStack(24).length);
        assertEquals(128, Util.getStack(100).length);
    }

    @Test
    void payload() {
        assertEquals(0x01135533, Util.payload(0x31135533));
    }

    @Test
    void tagBits() {
        assertEquals(0x03, Util.tagBits(0x30550000));
    }

    @Test
    void cell() {
        assertEquals(0x31135533, Util.cell(0x01135533, 3));
    }

    @Test
    void fitPayload() {
        assertEquals(0xB06699DD,Util.fitPayload(0xB1135533,0x6699DD));
    }
}