# Fifth 16 FPGA Emulator

The present Python code is a Demo emulatione of a reduced 16bit implementation of FIFTH16
on a FPGA. The OS and Fifth-native compiler is a work in progress, the accompanying
compiler.py is a minimal tool to program the FPGA.

It is a currently suspended work in progress included here as showcase and reference.

The implemented opcodes are aiming at high code density to allow implementation of a fully
functional universal stackmachine on FPGAs as small as a Tang Nano 1k, with OS and built-in
assembler and FORTH in the lower 1k cells.

The emulator implemets stackmuxing and conditional multi-opcode execution with flow which
define the core idea of the FIFTH philosophy of hardware/sofware synergy.
