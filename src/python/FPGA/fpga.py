#!/usr/bin/env python3
"""
 * FPGA emulator with FIFTH instruction set
 *
 * SPDX-License-Identifier: FLIP-v3.0
 * Copyright (c) 2026 snolde
 * Contact: snolde@gmail.com
 * License: https://github.com/snolde/flip/blob/v3.0/LICENSE
 * @FLIPCOP0: https://github.com/snolde/fifth
"""
import os as osys
from time import monotonic as time

class FPGA:
	def __init__(self, bus=None):
		self.PROTECTED = 0x1000
		self.OSSPACE = 0x07FF
		self.isMaster = True
		self.bus = bus
		self.irqQ = []
		self.devIndex = 2
		self.opc_def = {}
		self.opc_doc = {}
		self.ops = []
		self.mmioW = [self._w8, self._w16]*32
		self.mmioR =[self._r8, self._r16]*32
		self.mmioW[63] = self.burn
		self.ip=0
		self.dstack = self.Stack()
		self.rstack = self.Stack()
		self.start = 0
		self.stop = 0
		self.icount = 0
		self.memory = bytearray(64 * 1024)
		self.ROM = "\xAE\xBAM"
		self.romSetup()
		""" Setup device bus """
		if bus is not None:
			self.devIndex = bus.mmioReg(self, self.devIndex)

	class Stack:
		def __init__(self, max_depth=256):
			import array
			self.stack = array.array('H', [0] * max_depth)
			self.sp = 0

		def push(self, value):
			if self.sp >= len(self.stack):
				raise Exception("Stack overflow")
			self.stack[self.sp] = value & 0xFFFF
			self.sp += 1

		def pop(self):
			if self.sp == 0:
				raise Exception("Stack underflow")
			self.sp -= 1
			return self.stack[self.sp]

		def peek(self):
			if self.sp == 0: return 0
			return self.stack[self.sp - 1]
			
		def peek2(self):
			if self.sp <= 1: return 0
			return self.stack[self.sp -2]
			
		def poke(self, val):
			if self.sp > 0:
				self.stack[self.sp -1] = val & 0xFFFF
			
		def poke2(self, val):
			if self.sp>1:
				self.stack[self.sp -2] = val & 0xFFFF

		def depth(self):
			return self.sp

	def mpcRead16(self, addr):
		if addr>=64:
			return self.memory[addr] | (self.memory[addr + 1] << 8)
		else:
			return self.mmioR[(addr & 0xFE) +1](addr)

	def mpcRead8(self, addr):
		return self.memory[addr] if addr >=64 else self.mmioR[addr & 0xFE](addr)

	def mpcWrite16(self, addr, value):
		if addr > self.OSSPACE:
			self.memory[addr] = value & 0xFF
			self.memory[addr+1]=(value>>8) & 0xFF
		elif addr < 64: # mmio
			self.mmioW[addr & 0xFE + 1](addr & 0xFE, value)
		elif self.ip <= self.OSSPACE+2: #priv acc
			if self.memory[230] & 2 != 0: # no prot
				self.memory[addr]=value & 0xFF
				self.memory[addr+1]=(value>>8) & 0xFF
			elif addr < 0x10: #sysvars modifiable
				self.memory[addr] = value & 0xFF
				self.memory[addr+1]=(value>>8) & 0xFF
		return

	def mpcWrite8(self, addr, value):
		if addr > self.OSSPACE:
			self.memory[addr] = value & 0xFF
		elif addr < 64:
			self.mmioW[addr & 0xFE](addr, value)
		elif self.ip <= self.OSSPACE+2: #priv acc
			if self.memory[230] & 2 != 0: # no prot
				self.memory[addr] = value & 0xFF
			elif addr < 0x10: #sysvars modifiable
				self.memory[addr] = value & 0xFF
		return

	def _r16(self, a): #unchecked read 16bit
		return self.memory[a] | (self.memory[a + 1] << 8)
	
	def _w16(self, a, v): #unchecked write 16bit
		self.memory[a] = v & 0xFF
		self.memory[a+1]=(v>>8) & 0xFF
    	
	def _r8(self,a): #unchecked read byte
		return self.memory[a]
    	
	def _w8(self, a, v): #unchecked writenbyte
		self.memory[a] = v & 0xFF

	def handleIrq(self):
		while len(self.irqQ):
			vec = self.nextIrq()
			# Simple for now
			self._w8(226, vec) # vec-> ord('q')*2
			self.executeThread(0x0100) # IrqHdl
					  		  	
	def raiseIrq(self, vec, prio=0):
		self.irqQ.append((prio, vec))
		#print(f"irqs: {self.irqQ}")
		self.handleIrq()
    
	def nextIrq(self):
		if not self.irqQ:
			return None			
		for i in range(len(self.irqQ)):
			prio, vec = self.irqQ[i]
			self.irqQ[i] = (prio + 1, vec)#age        
		self.irqQ.sort(reverse=True)
		return self.irqQ.pop(0)[1]	
			
	def pack(self, s, e, i=''): #pack cells
		while ( s <= e and self._r16(s) == 0 ): s += 2
		if s>e: return ""
		p = i+f"{s:04x}:"
		while (s<=e and self._r16(s)!=0 ):
			p+=f"{self._r16(s):04x}"; s+= 2
		return "" if s>e else p+self.pack(s,e,',')
		
	def unpack(self, str): #unpack string
		if ',' in str:
			for b in str.split(','): self.unpack(b.strip())
		elif ':' in str:
			head, data = str.strip().split(':',1)
			addr = int(head,16)
			for i in range(0, len(data), 4):
				if i + 4 <= len(data):
					word = int(data[i:i+4], 16)
					self._w16(addr, word)
					addr += 2

	def burn(self, s=0, e=0x0fff):
		with open(__file__, 'r' ) as fi:
			body = fi.read().split("'"*3+self.ROM)[0]
			if body:
				body+=f"'''{self.ROM}\n"
				body+=self.pack(s,e)
				body+=f"\n{self.ROM}'''"
				with open(__file__, 'w' ) as fo:
					fo.write(body)
					print(f"{s:04x}-{e:04x} burned")
					
	def romSetup(self):
		with open(__file__, 'r' ) as f:
			rom = f.read().split(self.ROM)[1].strip()
			if rom: 
				self.unpack(rom); print("SysROM ok")
        		
	def executeThread(self, addr):
		"""Thread with xreg and mode or <- dict"""
		o2 = [1,-1,2,-2]
		memory = self.memory
		ip= addr
		rangemask= (self.PROTECTED -1) >>6
		xreg = 0
		state = self._r16(230)
		value = 0    # watch out for closures
		so = 0         # when adding opcodes!
		control =0  # performance over comfort
		ds = self.dstack # in the threader, 
		rs = self.rstack  # but learn to ride dragons
		ws = ds       # or get eaten!
		os = rs
		self.icount=0 # metrics
		self.start = time()
		# OPCODE IMPLEMENTATIONS
		# Stack Operations
		def opcNOP():
			"""[00] NOP ( -- )"""
			pass

		def opcDROP():
			"""[01] DRP ( w:n -- )"""
			ws.pop()
			
		def opcOVER():
			"""[02] OVR ( w:a w:b -- w:a w:b o:a )"""
			b = ws.pop(); a = ws.pop()
			ws.push(a); ws.push(b); os.push(a)
			
		def opcROT():
			"""[03] ROT ( w:a w:b w:c -- w:b w:c o:a )"""
			c = ws.peek(); ws.sp -=1; a = ws.peek2()
			ws.poke2(ws.peek());ws.poke(c)
			os.push(a)
			
		def opcDUP():
			"""[04] DUP ( w:n -- w:n o:n )"""
			a = ws.peek()
			os.push(a)

		def opcSWAP():
			"""[05] SWP ( w:a w:b -- w:b o:a )"""
			b = ws.pop(); a = ws.pop()
			ws.push(b); os.push(a)
		
		def opcNIP():
			"""[06] NIP ( w:a b -- o:b )"""
			b = ws.pop(); ws.sp-=1
			os.push(b)
		
		def opcUDR():
			"""[07] UDR ( w:a b -- w:a a b )"""
			b = ws.peek(); ws.poke(ws.peek2())
			ws.push(b)
										
		def opcUPP():
			"""[08] UPP ( -- w:a ) unpop"""
			ws.sp+=1					

		def opcLIT():
			"""[09] LIT ( -- w:@ip [w:val] ) b7:val"""
			nonlocal ip
			val = self.mpcRead16(ip)
			ws.push(val)
			if so & 2: ws.push(value)
			ip += 2
			
		def opcIPS():#with flow call else skip
			"""[0A] IPS ( -- [f:ip] a ) or skip"""
			nonlocal ip
			if xreg & 0x8000:
				rs.push(rs.peek()); rs.poke2(ip)
			else:
				ip += 2

		def opcAT():
			"""[0B] @ ( w:a -- o:val )"""
			os.push(self.mpcRead16(ws.pop()))

		def opcSTORE():
			"""[0C] ! ( w:cell o:a -- )"""
			val = ws.pop()
			self.mpcWrite16(val, os.pop())

		def opcCAT():
			"""[0D] C@ ( w:a -- o:byte )"""
			os.push(self.mpcRead8(ws.pop()))

		def opcCSTORE():
			"""[0E] C! ( w:a o:byte -- )"""
			byte = os.pop()
			self.mpcWrite8(ws.pop(), byte)
		
		def opcZEQ():
			"""[0F] 0= ( w:n -- o:flag )"""
			n = ws.pop()
			os.push ( 1 if n == 0 else 0 )

		def opcZLT():
			"""[10] 0< ( w:n -- o:flag )"""
			n = ws.pop()
			n_sig = n if n < 32768 else n - 65536
			os.push( 1 if n_sig < 0 else 0 )

		def opcNN():
			"""[11] !0 ( w:n -- o:n)"""
			n = ws.pop()
			os.push ( 0 if n == 0 else 1 )			
		
		def opcNEGATE():
			"""[12] NG ( w:n -- o:-n )"""
			n = ws.pop()
			os.push( (-n) & 0xFFFF )

		def opcINVERT():
			"""[13] ~ ( w:n -- o:~n )"""
			n = ws.pop()
			os.push( (~n) & 0xFFFF )

		def opcADD():
			"""[14] + ( w:a b -- o:a+b )"""
			os.push((ws.pop()+ws.pop())&0xFFFF)
			
		def opcSUB():
			"""[15] - ( w:a b -- o:a-b )"""
			os.push((-ws.pop()+ws.pop())&0xFFFF)

		def opcMUL():
			"""[16] * ( w:a b -- o:a*b )"""
			os.push((ws.pop()*ws.pop())&0xFFFF)

		def opcDIV():
			"""[17] / ( w:a b -- o:a/b )"""
			os.push((ws.pop()//ws.pop())&0xFFFF)

		def opcDIVMOD():
			"""[18] /% ( w:a b -- w:q o:r )"""
			b=ws.pop(); a=ws.pop()
			ws.push(( a // b )&0xFFFF)
			os.push(( a % b )&0xFFFF)

		def opcMOD():
			"""[19] % ( w:a b -- o:a%b )"""
			b=ws.pop(); a=ws.pop()
			os.push((a%b)&0xFFFF)

		def opcEQ():
			"""[1A] = ( w:a (b) -- (w:a) o:flag )"""
			b = ws.pop()
			a = ws.peek() if value else ws.pop()
			os.push( 1 if a == b else 0 )

		def opcLT():
			"""[1B] < ( w: a (b) -- (w:a) o:flag )"""
			b = ws.pop()
			a = ws.peek() if value else ws.pop()
			a_sig = a if a < 32768 else a - 65536
			b_sig = b if b < 32768 else b - 65536
			result = 1 if a_sig < b_sig else 0
			os.push(result)

		def opcGT():
			"""[1C] > ( w: a (b) -- (w:a) o:flag )"""
			b = ws.pop()
			a = ws.peek() if value else ws.pop()
			a_sig = a if a < 32768 else a - 65536
			b_sig = b if b < 32768 else b - 65536
			result = 1 if a_sig > b_sig else 0
			os.push(result)
									
		# Arithmetic (full value msb)
		def opcADDI():
			"""[20] #+ ( w: a (b) -- o: a+b ) F"""
			val = value & 0x7F; f = value >>7 & 1
			b = val if val else ws.pop()
			a = ws.pop()
			os.push ( (a + b) & 0xFFFF )
			if f:
				nonlocal flow; flow = f

		def opcSUBI():
			"""[21] #- ( w: a (b) -- o: a-b ) F"""
			val = value & 0x7F; f = value >>7 & 1
			b = val if val else ws.pop()
			a = ws.pop()
			os.push ( (a - b) & 0xFFFF )
			if f:
				nonlocal flow; flow = f

		def opcMULI():
			"""[22] #* ( w: a (b) -- o: a*b )"""
			b = value if value else ws.pop()
			a = ws.pop()
			os.push( (a * b) & 0xFFFF )

		def opcDIVI():
			"""[23] #/ ( w: a (b) -- o: a/b )"""
			b = value if value else ws.pop()
			a = ws.pop()
			if b == 0:
				raise Exception("Division by zero")
			os.push( (a // b) & 0xFFFF )

		def opcDIVMODI():
			"""[24] #/% ( w:a (b) -- w:q o:r )"""
			b = value if value else ws.pop()
			a = ws.pop()
			if b == 0:
				raise Exception("Division by zero")
			ws.push( (a // b) & 0xFFFF )
			os.push( (a % b) & 0xFFFF )

		def opcMODI():
			"""[25] #% ( w: a (b) -- o:a%b )"""
			b = value if value else ws.pop()
			a = ws.pop()
			if b == 0:
				raise Exception("Division by zero")
			os.push( (a % b) & 0xFFFF )

		# Logic & Bitwise (0x18-0x1D)
		def opcAND():
			"""[26] & ( w: a (b) -- o:a&b )"""
			b = value if value else ws.pop()
			a = ws.pop()
			os.push( a & b )

		def opcOR():
			"""[27] | ( w: a (b) -- o:a|b )"""
			b = value if value else ws.pop()
			a = ws.pop()
			os.push( a | b )

		def opcXOR():
			"""[28] ^ ( w:a (b) -- o:a^b )"""
			b = value if value else ws.pop()
			a = ws.pop()
			os.push( a ^ b )

		def opcLSHIFT():
			"""[29] << ( w: n (cnt) -- o: n<<cnt ) F"""
			n = value & 0x0F; f = value >>7 & 1
			count = n if n else ws.pop() & 0x0F
			os.push( (ws.pop() << count) & 0xFFFF )
			if f:
				nonlocal flow; flow = f
				
		def opcRSHIFT():
			"""[2A] >> ( w: n (cnt) -- o:n>>cnt ) F"""
			n = value & 0x0F; f = value >>7 & 1
			count = n if n else ws.pop() & 0x0F
			os.push( (ws.pop() >> count) & 0xFFFF )
			if f:
				nonlocal flow; flow = f
				
		def opcEQI():
			"""[2B] #= ( w:a (b) -- (w:a) o:flag ) F"""
			val = value & 0x7F; f = value >>7 & 1
			b = val if val else ws.pop()
			a = ws.peek() if val else ws.pop()
			if f:
				if a!=b:
					nonlocal flow; flow = f
			else:
				os.push( a==b )

		def opcLTI():
			"""[2C] #< ( w: a (b) -- (w:a) o:flag ) F"""
			val = value & 0x7F; f = value >>7 & 1
			b = val if val else ws.pop()
			a = ws.peek() if val else ws.pop()
			a_sig = a if a < 32768 else a - 65536
			b_sig = b if b < 32768 else b - 65536
			result = 1 if a_sig < b_sig else 0
			if f:
				if result==0:
					nonlocal flow; flow = f
			else:
				os.push(result)

		def opcGTI():
			"""[2D] #> ( w: a (b) -- (w:a) o:flag ) F"""
			val = value & 0x7F; f = value >>7 & 1
			b = val if val else ws.pop()
			a = ws.peek() if val else ws.pop()
			a_sig = a if a < 32768 else a - 65536
			b_sig = b if b < 32768 else b - 65536
			result = 1 if a_sig > b_sig else 0
			if f:
				if result==0:
					nonlocal flow; flow = f
			else:
				os.push(result)

		def opcCI():
			"""[2E] CI ( -- w:c ) """
			ws.push(self.mpcRead8(value))

		def opcCO():
			"""[2F] CO (w:c -- ) """
			self.mpcWrite8(value, ws.pop())
						
		# Control Flow
		def opcIPAT():
			"""[30] IP@ ( [w:a] -- w:ip [w:a]) """
			val = ip if value==0 else ip + ((value>127)*-256 + value)*2
			if so & 2: # tuck under
				ws.push(ws.peek()); ws.poke2(val)
			else:
				ws.push(val)
			
		def opcIPSET():
			"""[31] IP! ( w:ip -- ) / (--)ip += sval"""
			f = value & 0x03
			if so & 2:
				# 0: ws.pop(); 0: execute
				# 1: ws.pop(); !0: execute
				# 2: ws.dec; 0: drop return
				# 3: ws.inc: t>n: 2drop return
				if f==0:# IF 
					if ws.pop()!=0: return
				elif f==1:# IF!
					if ws.pop()==0: return
				elif f==2:#regressive loop
					ws.poke(ws.peek()-1)
					if ws.peek()==0: 
						ws.sp-=1; return
				elif f==3:#for range
					ws.poke(ws.peek()+1)
					if ws.peek()>ws.peek2():
						ws.sp-=2; return			
			nonlocal ip
			o = (value >> 2) & 0x3F
			if o == 0: ip = ws.pop()
			else: ip += ((o>31)*-64 + o)*2

		def opcTOSTACK():
			"""[32] >S ( (w:a) -- o:a )"""
			a = ws.pop() if 0<so<3 else value
			os.push(a)

		def opcSTSET():
			"""[33] S! ( (w:sp) -- ) val if os 1"""
			ws.sp = value if value else os.pop()

		def opcSTAT():
			"""[34] S@ (w:a -- o:w[v|a])"""
			i = ws.pop() if 0<so<3 else value
			os.push(ws.stack[i])
			
		def opcSTP():
			"""[35] SP ( -- o: w-sp ) """
			os.push(ws.sp)
								
		def opcCATL(): # False->FS us
			"""[36] C@< ( w:a --/ w:a f:? ) ^0 if false"""
			if self.mpcRead8(ws.peek())>=value:
				rs.push(0)

		def opcCATG(): # False->FS us
			"""[37] C@> ( w:a -- w:a f:? ) """
			if self.mpcRead8(ws.peek())<=value:
				rs.push(0)

		def opcCATADD():
			"""[38] C@+ ( w:a -- w:a ) +-c@a"""
			a = ws.peek(); c=self.mpcRead8(a)
			c +=  - value if so & 2 else value
			self.mpcWrite8(a, c)
					
		def opcXSM(): # cross stack math
			"""[39] XSM ( w:a o:b -- wo:a +- b )"""
			b=os.pop(); a=ws.pop()
			a=a-(b+(value >>2 & 0x1F)) if value & 1 else a + b + (value >> 2 & 0x1F)
			if value & 2:
				os.push(a)
			else:
				ws.push(a)
					
		# ToS/NoS cached
		def opcTNCSTORE():
			"""[3A] TNC! ( w:a b o:c -- w:a b )"""
			d = o2[value >> 2 & 3] if value & 2 else 0
			c=0; inc = value>>4 & 3; c = os.pop()
			if inc & 2: rs.poke(rs.peek-1)
			if value & 1:
				self.cpu.mcpWrite8(ws.peek2(),c+d)
				if inc: ws.poke2(ws.peek2()+2-inc)
			else:
				self.cpu.mpcWrite8(ws.peek(),c+d)
				if inc: ws.poke(ws.peek()+2-inc)			
			
		def opcTNM(): # dragons, understand!
			"""[3B] TN+ ( * -- * ) modifies tos/nos"""
			m = value >> 2 & 0x03
			if so & 2: ws.poke2(ws.peek2()+o2[m])
			else: ws.poke(ws.peek()+o2[m])
			if value & 0x01: #2nd value
				m = value >> 4 & 0x03
				st = ds if so & 2 else rs
				if so&1: st.poke2(st.peek2()+o2[m])
				else : st.poke(st.peek()+o2[m])
		
		def opcTNCAT():
			"""[3C] TNC@ ( w: a b -- w: a b o:c+?)"""
			d = o2[value >> 2 & 3] if value & 2 else 0
			c=0; inc = value>>4 & 3
			if inc & 2: rs.poke(rs.peek-1)	
			if value & 1:
				if inc: ws.poke2(ws.peek2()+2-inc)	
				c=self.mpcRead8(ws.peek2())+d
			else:
				if inc: ws.poke(ws.peek()+2-inc)
				c=self.mpcRead8(ws.peek())+d
			os.push(c)

		def opcWALK():
			"""[3D] WLK ( w:a1 w:a2 -- w:a1+1 w:a2+1 o:fl )"""
			a2 = ws.peek(); a1 = ws.peek2()
			b1 = a1 if value & 4 else self.mpcRead8(a1) # opt 0
			b2 = self.mpcRead8(a2)
			cmp = b1< b2 if value & 16 else b1 - b2 # b1< b2 or dif b1 b2
			loop = value >> 5
			if cmp==0: #calculate walk method
				ws.poke(a2 + 1 -(value & 2) )
				if not value&1: ws.poke2(a1 + 1)
				if value & 8:
					c=rs.peek(); rs.poke(c-1)				
				if loop and c: # autoloop
					nonlocal ip # dragons with flow opt
					ip -= loop *2 # loopback 1-7 cells
					return
			os.push(cmp)

		def opcMOV():
			"""[3E] MOV ( w:src w:dst o:len -- )"""
			len = os.pop(); a2 = ws.pop(); a1 = ws.pop()
			if (0xFFFF - a2) < len or ((state & 2) == 0 and a2 <= self.OSSPACE):
				raise Exception("Memory Access violation")
			self.memory[a2:a2+len] = self.memory[a1:a1+len]

		def opcSCL():
			"""[3F] ` ( -- ) syscall FS 10bit * 2"""
			nonlocal ip
			a = (value << 3) + (so << 1)
			rs.push(ip); ip = a

		def opcSTACKDUMP():
			""" .S ( -- ) #debug stackdump"""
			print(f"D({ds.sp}){list(ds.stack[0:ds.sp])}")
			print(f"F({rs.sp}){list(rs.stack[0:rs.sp])}")
	
		# build opcode dictionary and reference
		if addr<0: # return dict
			for name, obj in locals().items():
				if name.startswith("opc") and obj.__doc__ is not None:
					if obj.__doc__.startswith("["):
						doc = obj.__doc__.split("]",1)
						opcode = int(doc[0].removeprefix("["),16)
						word = doc[1].strip().split(' ',1)[0]
						self.opc_def[word] = opcode
						self.opc_doc[word] = obj.__doc__
			return self.opc_def
			
		#slot opcode map
		ops = [None] * 64 # build opcode map
		for name, obj in locals().items():
			if name.startswith("opc") and obj.__doc__ is not None:
				if obj.__doc__.startswith("["):
					doc = obj.__doc__.split("]",1)
					opcode = int(doc[0].removeprefix("["),16)
					ops[opcode]=obj

		while True:
			xreg = self._r16(ip)
			state = self._r16(230)
			ip += 2
			is_privileged = (state & 2) != 0
			# FORTH mode checks if thread addr
			if not is_privileged and ip >= self.PROTECTED and xreg >= self.PROTECTED:
				rs.push(ip)
				ip = xreg
				continue
			# Decode instruction fields
			opcode = xreg & 0x3F #6b
			so= (xreg >> 6) & 0x03 #2b s-opt
			opcode2 = (xreg >> 8) & 0x1F
			value = (xreg >> 8) #5b
			exec = 3 - (xreg>>4 & 2) # opcode split
			cond = 0 if exec==1 else (xreg >>13) & 3
			flow = 0 if exec==1 else(xreg >> 15) & 1
			ws = ds # stack reset
			os = ds # stack reset
			self.icount+=1 # metrics
			if so & 1: ws =rs #mux work stack
			if so & 2: os =rs # mux option stack
			if cond:
				if cond & 1: 
					if os.pop():
						exec = 1 if cond&2 else 3
					else:
						exec = 2 if cond&2 else 0
				if cond==1 and exec & 1:
					flow = 0				
			if ops[opcode] is None: 
				raise Exception(f"Unknown opcode: 0x{opcode:02x}")
			elif exec & 1 :
				self.ip = ip
				ops[opcode]() #execute op
			if ops[opcode2] is None: 
				raise Exception(f"Unknown opcode: 0x{opcode2:02x}")			
			if cond==2:
				if os.pop():
					flow =0
				else:
					exec = exec & 1
			if exec & 2:
				self.ip=ip
				ops[opcode2]() #execute op 2			
			if flow == 0:  # all normal, thread
				continue
			else:  # & flow (RET)
				if rs.depth() > 0:
					ip = rs.pop()
					continue # 0&1 done
				else:
					print(f"FS empty - HALT @ {ip:04x}")
					break
			
		self.stop = time()
		opcSTACKDUMP()
		elapsed=self.stop-self.start
		print(f"debug: {self.icount} instructions in {elapsed}s")
		print(f"∅time/instruction: {elapsed/self.icount*1000000} μs")
		print(f"op@0124: {elapsed/self.icount*1000000*6-20.5}μs")
		ips = self.icount/elapsed
		print(f"{ips} IPS")
		return ip
					
class CH552:
    '''includes connected virtual terminal'''
    def __init__(self, bus=None, id = 1):
        self.isMaster = False
        self.master = None
        self.esc_mod = False
        self.id = id
        self.esc_buf = ""
        self.sc = 0b01001000
        self.ibuf = ""
        if bus is not None:
        	if bus.isMaster:
        		self.mmioReg(bus, bus.devIndex)
        	elif bus.master is not None:
        		self.mmioReg(bus.master, bus.master.devIndex)
        		        
    def mmioReg(self, master, pos):
    	self.master = master
    	self.master.mmioW[pos]=self._write
    	self.master.mmioR[pos]=self._read
    	pos+=1
    	self.master.mmioW[pos]=self._writeSC
    	self.master.mmioR[pos]=self._readSC
    	pos+=1
    	return pos
    	
    def run(self):
    	while True:
    		try:
    			self.put(input().strip())
    		except EOFError:
    			break
    		except KeyboardInterrupt:
    			break
   
    def put(self, string):
    	self.ibuf = string
    	#cutting corners
    	self.master.memory[0x0701:0x0701+len(self.ibuf)]=self.ibuf.encode('ascii')
    	self.master._w8( 0x0700, len(self.ibuf))
    	#RX buffer in IB irq 1
    	print("raise irq")
    	self.master.raiseIrq( 0b00001001 )
   		
    def _readSC(self, byte):
    	return self.sc
    
    def _writeSC(self, byte):
    	self.sc = (self.sc & 0xF0)|( byte & 0x0F )
    	if byte & 1: # reset
    		 self.ibuf =""
    	elif byte & 2: # query TODO implement
    		pass
	
    def _read(self, byte):
    	if self.ibuf:
    		char = self.ibuf[0]; self.ibuf = self.ibuf[1:]
    		if not self.ibuf: self.sc =self.sc & 0x7F
    		return char
    	return 0
    	
    def _write(self, addr, byte):
        if self.esc_mod:
            self.esc_buf += chr(byte)
            if chr(byte).isalpha():  # esc end
                print(f'\x1b[{self.escape_buffer}', end='', flush=True)
                self.esc_mod = False
        elif byte == 27:  # ESC
            self.esc_mod = True
            self.esc_buf = ""
        else:
            print(chr(byte), end='', flush=True)
			
if __name__ == "__main__":
	fpga=FPGA(CH552())
	fpga.bus.run()
						
### NO CODE AFTER THIS - ROM ###
'''®ºM
00c4:000a1000,00d0:10000107,00e4:07ff0002010700070c00,00f0:a000,0100:039b0600,0110:0b0401a0c8c048bd05d000b90706e5c3e02dfb2ca021
®ºM'''