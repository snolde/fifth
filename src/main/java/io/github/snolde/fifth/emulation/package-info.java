/**
 * SPDX-License-Identifier: FLIP-v3.1
 * Copyright (c) 2026 snolde
 * Contact: snolde@gmail.com
 * <br>License: <a href="https://github.com/snolde/flip/blob/v3.1/LICENSE">FLIP v3.1</a>
 * <br>@FLIPCOP0: https://github.com/snolde/fifth
 *
 * <p>Package: emulation
 * <p>Purpose: High Performance Production Emulation
 * <p>This package contains JVM optimized implementations of the FIFTH MACHINE.
 * It is designed for maximum throughput and deterministic low latency. Consider it
 * a software hypervisor.
 * As a result, human readability and OOP "best practices" take a backseat.
 * <p>Target Audience: The JIT Compiler, the CPU, and production workloads.
 * <p>Design Principle: Performance invariants override Java conventions.
 * <ul>
 *     <li>No allocations in hot path. Primitive arrays only.</li>
 *     <li>No host exceptions for guest control flow.</li>
 *     <li>No wrapper methods or virtual dispatch inhibiting JIT
 *     inlining or causing megamorphic call sites.</li>
 *     <li>static state is used deliberately to reduce bytecode size and pointer chasing</li>
 * </ul>
 *
 * @see io.github.snolde.fifth.api
 */
package io.github.snolde.fifth.emulation;