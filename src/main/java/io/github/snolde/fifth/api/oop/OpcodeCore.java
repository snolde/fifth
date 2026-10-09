/*
 * SPDX-License-Identifier: FLIP-v3.1
 * Copyright (c) 2026 snolde
 * Contact: snolde@gmail.com
 * License: https://github.com/snolde/flip/blob/v3.1/LICENSE
 * @FLIPCOP0: https://github.com/snolde/fifth
 */

package io.github.snolde.fifth.api.oop;

public interface OpcodeCore {

    /// NOP ( w:a -- o:a ) NOP/F>/F</WAIT
    void opcode00();

    /// DROP ( w@o:c --  ) o=0 TOS, o=1 BOS
    void opcode01();

    /// DUP ( w:c -- w:c o:c )
    void opcode02();

    /// SWAP (  --  )
    void opcode03();

    /// OVER ( w:c1 w:c2 -- w:c1 w:c2 o:c1 )
    void opcode04();

    /// ROT ( w:c1 w:c2 w:c3 -- w:c2 w:c3, o:c1 )
    void opcode05();

    /// ROT- ( w:c1 w:c2 w:c3, o:c4 o:c5 -- o:c3 w:c1 w:c2, o:c4 o:c5)
    void opcode06();

    /// UNDR (  w:c1 w:c2, o:c3 -- w:c1 o:c1 w:c2, o:c3 )
    void opcode07();

    /// UPOP (  -- w@o:? ) unpop, o=0 TOS, o=1 BOS
    void opcode08();

    /// NIP (  --  )
    void opcode09();

    /// IFR (  --  ) BOS -> TOS
    void opcode0A();

    /// IFR- (  --  ) TOS -> BOS
    void opcode0B();

    /// STAB ( o:b ... w:t -- o:t ... w:b ) switch tos and bos
    void opcode0C();

    /// PICK ( w:depth -- o:v )
    void opcode0D();

    /// ! ( w:cell o:a -- ) store
    void opcode0E();

    /// @ ( w:a -- o:val ) at
    void opcode0F();

    /// 0= ( w:n -- o:flag )
    void opcode10();

    /// 0< ( w:n -- o:flag )
    void opcode11();

    /// !0 ( w:n -- o:flag )
    void opcode12();

    /// NEG ( w:n -- o:-n )
    void opcode13();

    /// ~ ( w:n -- o:~n ) logic invert
    void opcode14();

    /// + ( w:a b -- o:a+b ) add
    void opcode15();

    /// - ( w:a b -- o:a-b ) sub
    void opcode16();

    /// * ( w:a b -- o:a*b ) mul
    void opcode17();

    /// / ( w:a b -- o:a/b ) div
    void opcode18();

    /// /% ( w:a b -- w:q o:r ) div-mod
    void opcode19();

    /// % ( w:a b -- o:a%b ) mod
    void opcode1A();

    /// = ( w:a b -- o:flag ) equals
    void opcode1B();

    /// < ( w: a b -- o:flag ) less than
    void opcode1C();

    /// > ( w: a b -- o:flag ) greater than
    void opcode1D();

    /// IPS ( -- f:ip a ) or skip
    void opcode1E();

    /// DOS ( -- o:ws-depth ) // depth of stack
    void opcode1F();

    /// & ( w: a b -- o:a&b ) logic and
    void opcode20();

    /// | ( w: a b -- o:a|b ) logic or
    void opcode21();

    /// ^ ( w: a b -- o:a^b ) logic xor
    void opcode22();

    /// << ( w: n cnt -- o: n<<cnt ) shift left count
    void opcode23();

    /// >> ( w: n cnt -- o:n>>cnt ) shift right count
    void opcode24();

    /// . ( w:v -- ) contextual typed output
    void opcode25();

    /// (  --  )
    void opcode26();

    /// (  --  )
    void opcode27();

    /// (  --  )
    void opcode28();

    /// (  --  )
    void opcode29();

    /// (  --  )
    void opcode2A();

    /// (  --  )
    void opcode2B();

    /// (  --  )
    void opcode2C();

    /// (  --  )
    void opcode2D();

    /// (  --  )
    void opcode2E();

    /// (  --  )
    void opcode2F();

    /// (  --  )
    void opcode30();

    /// (  --  )
    void opcode31();

    /// (  --  )
    void opcode32();

    /// (  --  )
    void opcode33();

    /// (  --  )
    void opcode34();

    /// (  --  )
    void opcode35();

    /// (  --  )
    void opcode36();

    /// (  --  )
    void opcode37();

    /// (  --  )
    void opcode38();

    /// (  --  )
    void opcode39();

    /// (  --  )
    void opcode3A();

    /// (  --  )
    void opcode3B();

    /// (  --  )
    void opcode3C();

    /// (  --  )
    void opcode3D();

    /// (  --  )
    void opcode3E();

    /// (  --  )
    void opcode3F();

}
