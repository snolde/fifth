/**
 * SPDX-License-Identifier: FLIP-v3.1
 * Copyright (c) 2026 snolde
 * Contact: snolde@gmail.com
 * License: <a href="https://github.com/snolde/flip/blob/v3.1/LICENSE">FLIP v3.1</a>
 * @FLIPCOP0: https://github.com/snolde/fifth
 *
 * <p>This package contains the interface and handler contracts for standardized FIFTH
 * implementations. The api root holds the interfaces that MUST be implemented to guarantee
 * interoperability and clean integration by all implementation packages, model, emulation
 * and simulation.</p>
 *
 * <p>Those interfaces and handlers are only a few external contracts, especially for production
 * classes optimization, and should be prioritized over abstraction and refactorability.
 * Code philosophy is: write few, run many, refactor need only. </p>
 *
 * <p>The oop subpackage in turn contains interfaces along traditional Java OOP style,
 * abstract and educational separation of concern which does not necessarily reflect hardware
 * reality. These interfaces are to be implemented in the model subpackage. Goal here is to
 * demonstrate how FIFTH works from an OOP mindset.</p>
 *
 * <p>ATTENTION: Stack centric languages in general and in particular FIFTH have a distinct
 * object-oriented approach of their own, which causes friction with Java OOP best practices.
 * Purists be warned.</p>
 *
 * @see io.github.snolde.fifth.api.oop
 * @see io.github.snolde.fifth.emulation
 * @see io.github.snolde.fifth.simulation
 * @see io.github.snolde.fifth.model
 */

package io.github.snolde.fifth.api;