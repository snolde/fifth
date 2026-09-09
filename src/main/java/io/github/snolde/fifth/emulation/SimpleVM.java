/*
 * SPDX-License-Identifier: FLIP-v3.0
 * Copyright (c) 2026 snolde
 * Contact: snolde@gmail.com
 * License: https://github.com/snolde/flip/blob/v3.0/LICENSE
 * @FLIPCOP0: https://github.com/snolde/fifth
 */

package io.github.snolde.fifth.emulation;

import io.github.snolde.fifth.api.VM;
import io.github.snolde.fifth.api.oop.*;

public class SimpleVM implements VM, TwinStack, Threader, ALU, Memory {
    private final TwinStack stack;
    private final Threader threader;
    private final ALU alu;
    private final Memory mem;


    public SimpleVM() {
        this.stack = this;
        this.threader = this;
        this.alu = this;
        this.mem = this;
    }

    /// @param value int
    /// @param fs    boolean
    @Override
    public void push(int value, boolean fs) {

    }

    /// @param fs boolean
    /// @return top value
    @Override
    public int pop(boolean fs) {
        return 0;
    }

    /// @param value int
    /// @param fs    boolean
    @Override
    public void put(int value, boolean fs) {

    }

    /// @param fs boolean
    /// @return tail value
    @Override
    public int take(boolean fs) {
        return 0;
    }

    /// @param depth int
    /// @param fs    boolean
    /// @return cell at depth
    @Override
    public int pick(int depth, boolean fs) {
        return 0;
    }

    /// @param fs boolean
    /// @return depth of stack
    @Override
    public int depth(boolean fs) {
        return 0;
    }

    ///
    @Override
    public void run() {

    }
}
