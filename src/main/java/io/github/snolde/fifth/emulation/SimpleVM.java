/*
 * SPDX-License-Identifier: FLIP-v3.1
 * Copyright (c) 2026 snolde
 * Contact: snolde@gmail.com
 * License: https://github.com/snolde/flip/blob/v3.1/LICENSE
 * @FLIPCOP0: https://github.com/snolde/fifth
 */

package io.github.snolde.fifth.emulation;

import io.github.snolde.fifth.api.CellTransport;
import io.github.snolde.fifth.api.VM;
import io.github.snolde.fifth.api.oop.*;

public class SimpleVM implements VM {


    public SimpleVM() {
    }


    ///
    @Override
    public void run() {

    }

    /// @param cell
    /// @param channel
    @Override
    public void send(int cell, int channel) {

    }

    /// @param channel
    /// @param consumer
    @Override
    public void subscribe(int channel, CellTransport consumer) {

    }
}
