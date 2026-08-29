"""
 * SPDX-License-Identifier: FLIP-v3.0
 * Copyright (c) 2026 snolde
 * Contact: snolde@gmail.com
 * License: https://github.com/snolde/flip/blob/v3.0/LICENSE
 * @FLIPCOP0: https://github.com/snolde/fifth
"""
from fpga import FPGA, CH552
import os as osys


class FPGACompiler:
    def __init__(self, cpu=None):
        if cpu is None:
            self.cpu = FPGA(CH552())
        else:
        	self.cpu = cpu
        self.labels = {}  # label_name -> address
        self.references = []  # (address, label_name, mode)
        self.cursor = 0
        self.mode = ':'
        self.opcode_map = self.cpu.executeThread(-1)
        self.file = "compiler.mem"
        
        # Control mode mapping
        self.cmap= ['n', '??', ':?', '?:','f','??f',':?f','?:f']
        self.sop = ['ww','fw','wf','ff']

    def interactive(self, cursor):
        """interactive opcode compiler"""
        self.cursor = cursor
        self.opcDict(0x0300)
        while True:
        	try:
        		line = input(f"{self.cursor:#06X}{self.mode}").strip()
        		while line:
        			if self.mode=="=":
        				line = self.compile_line(line)
        			elif self.mode==":":        			
        				if line.startswith("]"):
        					self.mode="="
        					line = line[1:].strip()
        				elif line.startswith('0x'):
        					line +=" ";a=line.split(" ",1)[0]
        					self.cursor=self.parse_value(a.strip())
        					
        					line = line[len(a):].strip()
        					print(f"line={line}")
        				elif line.startswith("d"):
        					line=self.disasm(line)
        				elif line.startswith("<"):
        					line = self.load_block(line)
        				elif line.startswith(">"):
        					line = self.save_block(line)
        				elif line.startswith("b"):
        					self.cpu.burn()
        					line = line[1:].strip()
        				elif line.startswith("m"):
        					line = self.moveBlock(line)
        				elif line.startswith("o"):
        					self.opcodes(0)
        					line = line[1:].strip()
        				elif line.startswith("?"):
        					self.opcodes(1)
        					line = line[1:].strip()
        				elif line.startswith("x"):
        					self.cpu.executeThread(self.cursor)
        					line = line[1:].strip()
        				elif line.startswith("✓"):
        					print("\nd•∆•b ,(compile exit)")
        					break
        				elif line.startswith("h"):
        					line = line[1:].strip()
        					tok = line.strip().split(" ",2)
        					count = self.parse_value(tok[0]) if tok[0] else 4
        					self.memDump(self.cursor & 0xFFF0,(count<<4)-1)
        					line = tok[1] if len(tok)>1 else ''
        					continue
        				else:
        					print("???")
        					line = ""
        					continue
        	except EOFError:
        		break
        	except KeyboardInterrupt:
        			print("\nd•∆•b °°°")
        			break
        			
    def opcDict(self, a):
    	for w in self.opcode_map:
    		self.cpu._w8(a,len(w))
    		a+=1
    		self.cpu.memory[a:a+len(w)]=w.encode('ascii')
    		a+=len(w)
    		self.cpu._w8(a,self.opcode_map[w])
    		a+=1

    def disasm(self, line):
    	line = line.strip().split(" ",2)
    	count = 8 if len(line)<2 else self.parse_value(line[1])
    	line = "" if len(line)<3 else line[2]
    	for i in range(0,count,2):
    		xr=self.cpu._r16(self.cursor+i)
    		opc= xr & 0x3f
    		opc2= xr>>8 & 0x1f if opc < 32 else -1
    		sop = self.sop[xr>>6 & 0x03]
    		val = xr>>8 & 0xFF
    		cf = xr >>13 & 0x07
    		if opc < 32:
    			print(f"{self.cursor+i:#06x} {xr:04X}   {self.findword(opc):4} {self.findword(opc2):3} {sop} {self.cmap[cf]}")
    		else:
    			print(f"{self.cursor+i:#06x} {xr:04X}   {self.findword(opc):8} {sop} {val:02X}")
    			
    	return line.strip()
    				
    def load_block(self, line):
    	line = line.strip().split(" ",2)
    	if len(line) > 1:
    		self.load(line[1].strip())
    	else:
    		self.load(self.file)
    	return "" if len(line)<3 else line[2]

    def save_block(self, line):
    	line = line.strip().split(" ",2)
    	if len(line) > 1:
    		self.save(line[1].strip())
    	else:
        	self.save(self.file)
    	return "" if len(line)<3 else line[2]
    	        	
    def delete_block(self, line):
    	pass

    def moveBlock(self, line):
    	line = line.strip().split(" ",4)
    	if len(line) > 2:
    		try:
    			target = self.parse_value(line[1])
    			length = self.parse_value(line[2])
    			self.cpu.memory[target:target+length] = self.cpu.memory[self.cursor:self.cursor+length]
    			print(f"{length} bytes copied to {target:04x}")
    		except ValueError:
    			print("m target length")
    	return "" if len(line)<4 else line[3]
    		
    def save(self, file, s=0, e =0xffff):
        packed = self.cpu.pack(s, e)
        with open(file, 'w') as f:
            f.write(packed)
            print(f"Saved {e-s} bytes to {file}")
    
    def load(self, file):
        if not osys.path.exists(file):
            print(f"File {file} not found")
        else:
            with open(file, 'r') as f:
                packed = f.read().strip()
                self.cpu.unpack(packed)
                print(f"Loaded memory from {file}")
				
    def opcodes(self, flag=0):
        if flag:
            print(f"{len(self.opcode_map)} opcodes")
            for word in self.opcode_map:
                print(f"{self.opcode_map[word]:#4x} : {word:8}")
        else:
            print(len(self.cpu.opc_doc))
            for opc in self.cpu.opc_doc:
                print(f"{self.cpu.opc_doc[opc]}")
	
    def findword(self, opc):
    	for word in self.opcode_map:
    		if self.opcode_map[word] == opc:
    			return word
    	return f"?{opc:02X}"		
							
    def compile_line(self, line):
        """Compile a single line of source code"""
        line = line.strip()
        if not line:
            return
                     
        if line.startswith("—"): # string
        	line = line[1:]
        	length = len(line)
        	#print("length")
        	self.cpu._w8(self.cursor, length)
        	if not length%2:
        		line += ' ' # pad
        	self.cpu.memory[self.cursor+1:self.cursor + length]=line.encode('ascii')
        	self.cursor += 1 + length
        		
        # process by token
        while self.mode=="=" and line:
        	line = line.split(" ",1)
        	token = line[0]
        	line = "" if len(line)<2 else line[1]
        	if token.startswith("["):
        		self.mode=":"
        	elif token.startswith('—'): # string
        		line = line[1:]
        		length = len(line)
        		self.cpu._w8(self.cursor, length)
        		if not length%2:
        			line += ' ' # pad
        		self.cpu.memory[self.cursor+1:self.cursor + length]=line.encode('ascii')
        		self.cursor += 1 + length
        		return ""
        	else:
        	   self.compile_token(token)
        
        return line
        	   
            
    def compile_token(self, token):
        """Compile a single token with enhanced format: OPCODE_mode_stack_range"""

        # Parse opcode_mode_stack_range
        parts = token.split(',')
        opcode_name = parts[0].upper()
    
        # Default values
        cond = 'n'  # normal
        stack_opt = 'ww'  # both stacks = data stack
        val = 0
        opcode2 = 0
        cond =""
    
        # Parse remaining parts
        for part in parts[1:]:
            if not part:
                continue
            
            # Check for control modes
            if part in self.cmap:
                cond = part
            # Check for stack options (ww, fw, wf, ff)
            elif part in self.sop:
                stack_opt = part
            # Check for range/label (starts with 0x, 0b, or [)
            elif part.startswith('0x') or part.startswith('0b'):
                val = self.parse_value(part)
            elif part.upper() in self.opcode_map:
            	opcode2=self.opcode_map[part.upper()]
            	if opcode2 >=32:
            		print("2nd opcode out of range")
            		return
            # Check for numeric range (digits only)
            else:
                val = self.parse_value(part)
     
        # Get base opcode
        if opcode_name not in self.opcode_map:
            # Handle numeric literals
            try:
                value = self.parse_value(opcode_name)
                self.cpu._w16(self.cursor, value)
                self.cursor += 2
            except ValueError:
            	print(f"Invalid opcode or value: {opcode_name}.\nTo byte encode a string, use — (em-dash).")

            return
        
        opcode = self.opcode_map[opcode_name]
        print(f"found: {opcode:#04x} {opcode_name}")
    
        # Convert stack options to so value
        stack_map = {'w': 0, 'f': 1}
        if len(stack_opt) == 2:
            so = (stack_map.get(stack_opt[1], 0) << 1) | stack_map.get(stack_opt[0], 0)
        else:
            so = 0
        c_map = {'n':0, '??':1, ':?':2, '?:':3,'f':4,'??f':5,':?f':6,'?:f':7}
        cf= c_map[cond] if len(cond)>0 else 0
          
        # Build instruction word
        # Format: [6b opc][2b so] [5b opcode2][2b cond][1b flow] | [8b value]
        if opcode < 32:
        	print(f"word: {opcode:02X} so {so:02b} 2nd {opcode2:02X} {cf:06b}")
        else:
        	print(f"word:{opcode:02X} so {so:02b} val {val:04X}")
        instruction = (opcode & 0x3F) | ((so & 0x03) << 6)
        instruction +=  ((val & 0xFF) << 8) if opcode >31 else  ((opcode2 & 0x1F) << 8) | ((cf & 7) <<13)
    
        # Write instruction
        self.cpu._w16(self.cursor, instruction)
        self.cursor += 2
            
    def parse_value(self, value_str):
        """Parse numeric values in different bases"""
        value_str = value_str.strip().upper()
        if value_str.startswith('0X'):
            try:
            	return int(value_str[2:], 16)
            except ValueError:
            	print("Hex Value Error -> 0")
            	return 0
        elif value_str.startswith('0B'):
            try:
            	return int(value_str[2:], 2)
            except ValueError:
            	print("Binary Value Error -> 0")
            	return 0
        else:
            return int(value_str) 

    def memDump(self, start, length):
        """dump memory region"""
        ctr_str = ' '.join(f"{(start + j)&0xFF:02X}" for j in range(16))
        print(f"memdump   {ctr_str}")
        for i in range(0, min(length, 256), 16):
            hex_str = ' '.join(f"{self.cpu.memory[start + i + j]:02X}" for j in range(16))
            ascii_str = ''.join(chr(self.cpu.memory[start + i + j]) + '  ' if 32 <= self.cpu.memory[start + i + j] < 127 else '.  ' for j in range(16))
            print(f"  {start + i:#06x}: {hex_str}\n      HR:  {ascii_str}")
            
    def compile_program(self, source_lines, start_addr=0x2000):
        """Compile a complete program"""
        self.cursor = start_addr
        
        for line in source_lines.split('\n'):
            self.compile_line(line)

        return self.cursor  # Return end address

    def compile_and_run(self, source, start_addr=0x2000):
        """Compile and execute FORTH source"""
        end_addr = self.compiler.compile_program(source, start_addr)
        print(f"Compiled to {start_addr:#06x}-{end_addr:#06x}")
        self.cpu.executeThread(start_addr)

              
if __name__ == "__main__":
	compiler = FPGACompiler()
	compiler.interactive(0x0100)
    