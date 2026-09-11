## 001 - FlowGuard proposal
### Status
accepted
### Context
Differentiation of executables and data allows 
special treatment of data cells on occurring flow.
### Decision
Data values on the flow-stack are considered "flow-guards",
on encountering a FlowGuard  (FG) on the flow-stack, the threader
applies the following logic:
1. FG>0 : decrement FG, IP ⇒ fs:NOS, FG==0 ? NIP
2. FG=0 : DROP FG, skip flow, IP++
3. FG<0 : DROP FG, execute flow

### Consequences
- opcode-free loops with count (FG)
- opcode-free branching (boolean FG)
- intuitive architecture (FG guards executable under it)
- simple performant hardware implementation
