test1:

# this is a comment
noop
add a3, v2, r30
addi r0, 255
or r0, v0, r1
ori r0, 255
# this is another comment
xor r0, v0, r1
and r0, v0, r1
not r0, v0
inv r0, v0
sll r0, v0
sla r0, v0
srl r0, v0
sra r0, v0

# this is a comment again
test2:
jmp test1
jr r0
jal test2