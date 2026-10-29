 9b82600: 55                           	pushl	%ebp
 9b82601: 8b ec                        	movl	%esp, %ebp
 9b82603: 51                           	pushl	%ecx
 9b82604: 53                           	pushl	%ebx
 9b82605: 85 f6                        	testl	%esi, %esi
 9b82607: 0f 84 9e 00 00 00            	je	0x9b826ab <.text+0x56b>
 9b8260d: 8d 45 fc                     	leal	-0x4(%ebp), %eax
 9b82610: 50                           	pushl	%eax
 9b82611: 6a 03                        	pushl	$0x3
 9b82613: 68 a0 d5 05 00               	pushl	$0x5d5a0                # imm = 0x5D5A0
 9b82618: b8 b8 00 00 00               	movl	$0xb8, %eax
 9b8261d: e8 83 17 00 00               	calll	0x9b83da5 <.text+0x1c65>
 9b82622: 8b 45 fc                     	movl	-0x4(%ebp), %eax
 9b82625: 8b c8                        	movl	%eax, %ecx
 9b82627: c1 e9 05                     	shrl	$0x5, %ecx
 9b8262a: b3 7f                        	movb	$0x7f, %bl
 9b8262c: 22 cb                        	andb	%bl, %cl
 9b8262e: 88 0e                        	movb	%cl, (%esi)
 9b82630: 8b c8                        	movl	%eax, %ecx
 9b82632: c1 e9 0c                     	shrl	$0xc, %ecx
 9b82635: 22 cb                        	andb	%bl, %cl
 9b82637: 88 4e 01                     	movb	%cl, 0x1(%esi)
 9b8263a: 8b c8                        	movl	%eax, %ecx
 9b8263c: c1 e8 1a                     	shrl	$0x1a, %eax
 9b8263f: 22 c3                        	andb	%bl, %al
 9b82641: 88 46 03                     	movb	%al, 0x3(%esi)
 9b82644: 83 c4 0c                     	addl	$0xc, %esp
 9b82647: 8d 45 fc                     	leal	-0x4(%ebp), %eax
 9b8264a: 50                           	pushl	%eax
 9b8264b: c1 e9 13                     	shrl	$0x13, %ecx
 9b8264e: 22 cb                        	andb	%bl, %cl
 9b82650: 6a 03                        	pushl	$0x3
 9b82652: 68 a4 d5 05 00               	pushl	$0x5d5a4                # imm = 0x5D5A4
 9b82657: b8 b8 00 00 00               	movl	$0xb8, %eax
 9b8265c: 88 4e 02                     	movb	%cl, 0x2(%esi)
 9b8265f: e8 41 17 00 00               	calll	0x9b83da5 <.text+0x1c65>
 9b82664: 8b 4d fc                     	movl	-0x4(%ebp), %ecx
 9b82667: 8b 45 fc                     	movl	-0x4(%ebp), %eax
 9b8266a: d1 e8                        	shrl	%eax
 9b8266c: 22 c3                        	andb	%bl, %al
 9b8266e: c1 e9 08                     	shrl	$0x8, %ecx
 9b82671: 83 c4 0c                     	addl	$0xc, %esp
 9b82674: 22 cb                        	andb	%bl, %cl
 9b82676: 88 46 04                     	movb	%al, 0x4(%esi)
 9b82679: 0f be c0                     	movsbl	%al, %eax
 9b8267c: 88 4e 05                     	movb	%cl, 0x5(%esi)
 9b8267f: 0f be c9                     	movsbl	%cl, %ecx
 9b82682: 51                           	pushl	%ecx
 9b82683: 50                           	pushl	%eax
 9b82684: 0f be 46 03                  	movsbl	0x3(%esi), %eax
 9b82688: 50                           	pushl	%eax
 9b82689: 0f be 46 02                  	movsbl	0x2(%esi), %eax
 9b8268d: 50                           	pushl	%eax
 9b8268e: 0f be 46 01                  	movsbl	0x1(%esi), %eax
 9b82692: 50                           	pushl	%eax
 9b82693: 0f be 06                     	movsbl	(%esi), %eax
 9b82696: 50                           	pushl	%eax
 9b82697: 68 e4 65 b8 09               	pushl	$0x9b865e4              # imm = 0x9B865E4
 9b8269c: 68 00 00 04 00               	pushl	$0x40000                # imm = 0x40000
 9b826a1: 6a 00                        	pushl	$0x0
 9b826a3: e8 29 0c 00 00               	calll	0x9b832d1 <.text+0x1191>
 9b826a8: 83 c4 24                     	addl	$0x24, %esp
 9b826ab: 5b                           	popl	%ebx
 9b826ac: c9                           	leave
 9b826ad: c3                           	retl
 9b826ae: 55                           	pushl	%ebp
 9b826af: 8b ec                        	movl	%esp, %ebp
 9b826b1: 83 ec 14                     	subl	$0x14, %esp
 9b826b4: 56                           	pushl	%esi
 9b826b5: 57                           	pushl	%edi
 9b826b6: 33 c0                        	xorl	%eax, %eax
 9b826b8: c6 45 f0 00                  	movb	$0x0, -0x10(%ebp)
 9b826bc: 8d 7d f1                     	leal	-0xf(%ebp), %edi
 9b826bf: ab                           	stosl	%eax, %es:(%edi)
 9b826c0: ab                           	stosl	%eax, %es:(%edi)
 9b826c1: aa                           	stosb	%al, %es:(%edi)
 9b826c2: 68 04 66 b8 09               	pushl	$0x9b86604              # imm = 0x9B86604
 9b826c7: bf 00 00 04 00               	movl	$0x40000, %edi          # imm = 0x40000
 9b826cc: 57                           	pushl	%edi
 9b826cd: 6a 00                        	pushl	$0x0
 9b826cf: e8 fd 0b 00 00               	calll	0x9b832d1 <.text+0x1191>
 9b826d4: 8b 45 08                     	movl	0x8(%ebp), %eax
 9b826d7: 83 c4 0c                     	addl	$0xc, %esp
 9b826da: e8 e9 0d 00 00               	calll	0x9b834c8 <.text+0x1388>
 9b826df: 85 c0                        	testl	%eax, %eax
 9b826e1: eb 4f                        	jmp	0x9b82732 <.text+0x5f2>
 9b826e3: 8d 75 f0                     	leal	-0x10(%ebp), %esi
 9b826e6: e8 15 ff ff ff               	calll	0x9b82600 <.text+0x4c0>
 9b826eb: 8a 4d f0                     	movb	-0x10(%ebp), %cl
 9b826ee: ba 20 66 b8 09               	movl	$0x9b86620, %edx        # imm = 0x9B86620
 9b826f3: 8b c6                        	movl	%esi, %eax
 9b826f5: eb 08                        	jmp	0x9b826ff <.text+0x5bf>
 9b826f7: 3a 0a                        	cmpb	(%edx), %cl
 9b826f9: 75 08                        	jne	0x9b82703 <.text+0x5c3>
 9b826fb: 40                           	incl	%eax
 9b826fc: 8a 08                        	movb	(%eax), %cl
 9b826fe: 42                           	incl	%edx
 9b826ff: 84 c9                        	testb	%cl, %cl
 9b82701: 75 f4                        	jne	0x9b826f7 <.text+0x5b7>
 9b82703: 0f be 0a                     	movsbl	(%edx), %ecx
 9b82706: 0f be 00                     	movsbl	(%eax), %eax
 9b82709: 2b c1                        	subl	%ecx, %eax
 9b8270b: 75 14                        	jne	0x9b82721 <.text+0x5e1>
 9b8270d: 6a 01                        	pushl	$0x1
 9b8270f: 68 0d 14 04 00               	pushl	$0x4140d                # imm = 0x4140D
 9b82714: 68 c0 5c b8 09               	pushl	$0x9b85cc0              # imm = 0x9B85CC0
 9b82719: e8 4b 09 00 00               	calll	0x9b83069 <.text+0xf29>
 9b8271e: 83 c4 0c                     	addl	$0xc, %esp
 9b82721: 8b 45 fc                     	movl	-0x4(%ebp), %eax
 9b82724: f7 00 00 00 00 20            	testl	$0x20000000, (%eax)     # imm = 0x20000000
 9b8272a: 75 0b                        	jne	0x9b82737 <.text+0x5f7>
 9b8272c: 0f b7 48 06                  	movzwl	0x6(%eax), %ecx
 9b82730: 03 c1                        	addl	%ecx, %eax
 9b82732: 89 45 fc                     	movl	%eax, -0x4(%ebp)
 9b82735: 75 ac                        	jne	0x9b826e3 <.text+0x5a3>
 9b82737: 68 28 66 b8 09               	pushl	$0x9b86628              # imm = 0x9B86628
 9b8273c: 57                           	pushl	%edi
 9b8273d: 6a 00                        	pushl	$0x0
 9b8273f: e8 8d 0b 00 00               	calll	0x9b832d1 <.text+0x1191>
 9b82744: 83 c4 0c                     	addl	$0xc, %esp
 9b82747: 5f                           	popl	%edi
 9b82748: 33 c0                        	xorl	%eax, %eax
 9b8274a: 5e                           	popl	%esi
 9b8274b: c9                           	leave
 9b8274c: c3                           	retl
 9b83069: e8 e2 ff ff ff               	calll	0x9b83050 <.text+0xf10>
 9b8306e: ff 74 24 0c                  	pushl	0xc(%esp)
 9b83072: ff 74 24 0c                  	pushl	0xc(%esp)
 9b83076: ff 74 24 0c                  	pushl	0xc(%esp)
 9b8307a: ff 50 20                     	calll	*0x20(%eax)
 9b8307d: 8a 44 24 18                  	movb	0x18(%esp), %al
 9b83081: 83 c4 0c                     	addl	$0xc, %esp
 9b83084: c3                           	retl
 9b83085: e8 c6 ff ff ff               	calll	0x9b83050 <.text+0xf10>
 9b8308a: ff 74 24 0c                  	pushl	0xc(%esp)
 9b8308e: ff 74 24 0c                  	pushl	0xc(%esp)
 9b83092: ff 74 24 0c                  	pushl	0xc(%esp)
 9b83096: ff 50 34                     	calll	*0x34(%eax)
 9b83099: 8a 44 24 18                  	movb	0x18(%esp), %al
 9b8309d: 83 c4 0c                     	addl	$0xc, %esp
