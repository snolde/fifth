"""
FPGA emulator with FIFTH instruction set

SPDX-License-Identifier: FLIP-v3.1
Copyright (c) 2026 snolde
Contact: snolde@gmail.com
License: https://github.com/snolde/flip/blob/v3.1/LICENSE
@FLIPCOP0: https://github.com/snolde/fifth
  """
``` code
[00] NOP ( -- )
[01] DRP ( w:n -- )
[02] OVR ( w:a w:b -- w:a w:b o:a )
[03] ROT ( w:a w:b w:c -- w:b w:c o:a )
[04] DUP ( w:n -- w:n o:n )
[05] SWP ( w:a w:b -- w:b o:a )
[06] NIP ( w:a b -- o:b )
[07] UDR ( w:a b -- w:a a b )
[08] UPP ( -- w:a ) unpop
[09] LIT ( -- w:@ip [w:val] ) b7:val
[0A] IPS ( -- [f:ip] a ) or skip
[0B] @ ( w:a -- o:val )
[0C] ! ( w:cell o:a -- )
[0D] C@ ( w:a -- o:byte )
[0E] C! ( w:a o:byte -- )
[0F] 0= ( w:n -- o:flag )
[10] 0< ( w:n -- o:flag )
[11] !0 ( w:n -- o:n)
[12] NG ( w:n -- o:-n )
[13] ~ ( w:n -- o:~n )
[14] + ( w:a b -- o:a+b )
[15] - ( w:a b -- o:a-b )
[16] * ( w:a b -- o:a*b )
[17] / ( w:a b -- o:a/b )
[18] /% ( w:a b -- w:q o:r )
[19] % ( w:a b -- o:a%b )
[1A] = ( w:a (b) -- (w:a) o:flag )
[1B] < ( w: a (b) -- (w:a) o:flag )
[1C] > ( w: a (b) -- (w:a) o:flag )
[20] #+ ( w: a (b) -- o: a+b ) F
[21] #- ( w: a (b) -- o: a-b ) F
[22] #* ( w: a (b) -- o: a*b )
[23] #/ ( w: a (b) -- o: a/b )
[24] #/% ( w:a (b) -- w:q o:r )
[25] #% ( w: a (b) -- o:a%b )
[26] & ( w: a (b) -- o:a&b )
[27] | ( w: a (b) -- o:a|b )
[28] ^ ( w:a (b) -- o:a^b )
[29] << ( w: n (cnt) -- o: n<<cnt ) F
[2A] >> ( w: n (cnt) -- o:n>>cnt ) F
[2B] #= ( w:a (b) -- (w:a) o:flag ) F
[2C] #< ( w: a (b) -- (w:a) o:flag ) F
[2D] #> ( w: a (b) -- (w:a) o:flag ) F
[2E] CI ( -- w:c )
[2F] CO (w:c -- )
[30] IP@ ( [w:a] -- w:ip [w:a])
[31] IP! ( w:ip -- ) / (--)ip += sval
[32] >S ( (w:a) -- o:a )
[33] S! ( (w:sp) -- ) val if os 1
[34] S@ (w:a -- o:w[v|a])
[35] SP ( -- o: w-sp )
[36] C@< ( w:a --/ w:a f:? ) ^0 if false
[37] C@> ( w:a -- w:a f:? )
[38] C@+ ( w:a -- w:a ) +-c@a
[39] XSM ( w:a o:b -- wo:a +- b )
[3A] TNC! ( w:a b o:c -- w:a b )
[3B] TN+ ( * -- * ) modifies tos/nos
[3C] TNC@ ( w: a b -- w: a b o:c+?)
[3D] WLK ( w:a1 w:a2 -- w:a1+1 w:a2+1 o:fl )
[3E] MOV ( w:src w:dst o:len -- )
[3F] ` ( -- ) syscall FS 10bit * 2
```
0X0100: