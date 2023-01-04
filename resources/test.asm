test1:

# this is a comment
noop
add a3, v2, r30
addi r3, r3, 255
or r12, v2, r7
ori r0, r1, 12
# this is another comment
xor r0, v0, r1
and r0, v0, r1
inv r0, v0
not r0, v0
sll r0, v0
sla r0, v0
srl r0, v0
sra r0, v0

# this is a comment again
test2:
jmp test1
jr r0
test3:
jal test2