"""Small JVM classfile reader for member/invocation discovery (not a decompiler)."""
import struct

def modified_utf8(data):
    # JVM strings encode NUL as C0 80 and supplementary characters as surrogate pairs.
    value=data.replace(b'\xc0\x80',b'\x00').decode('utf-8','surrogatepass')
    return value.encode('utf-16','surrogatepass').decode('utf-16','surrogatepass')

class Reader:
    def __init__(self,data): self.data=data; self.pos=0
    def take(self,n):
        value=self.data[self.pos:self.pos+n]
        if len(value)!=n: raise ValueError('Truncated classfile')
        self.pos+=n; return value
    def u1(self): return self.take(1)[0]
    def u2(self): return int.from_bytes(self.take(2),'big')
    def u4(self): return int.from_bytes(self.take(4),'big')

class ClassFile:
    def __init__(self,data):
        r=Reader(data)
        assert r.u4()==0xcafebabe
        self.minor=r.u2(); self.major=r.u2(); count=r.u2(); self.cp=[None]*count
        i=1
        while i<count:
            tag=r.u1()
            if tag==1: value=modified_utf8(r.take(r.u2()))
            elif tag in (3,4): value=struct.unpack('>i' if tag==3 else '>f',r.take(4))[0]
            elif tag in (5,6): value=struct.unpack('>q' if tag==5 else '>d',r.take(8))[0]
            elif tag in (7,8,16,19,20): value=r.u2()
            elif tag in (9,10,11,12,17,18): value=(r.u2(),r.u2())
            elif tag==15: value=(r.u1(),r.u2())
            else: raise ValueError(f'Unknown constant pool tag {tag}')
            self.cp[i]=(tag,value); i+=2 if tag in (5,6) else 1
        self.access=r.u2(); self.name=self.resolve(r.u2()); self.super=self.resolve(r.u2())
        self.interfaces=[self.resolve(r.u2()) for _ in range(r.u2())]
        self.fields=self.members(r); self.methods=self.members(r); self.attributes=self.attrs(r)
        assert r.pos==len(data)
    def resolve(self,index):
        if index==0: return None
        tag,val=self.cp[index]
        if tag in (7,8,16,19,20): return self.resolve(val)
        if tag in (9,10,11): return self.resolve(val[0])+'.'+self.resolve(val[1])
        if tag==12: return self.resolve(val[0])+self.resolve(val[1])
        if tag==15: return self.resolve(val[1])
        if tag in (17,18): return 'bootstrap#'+str(val[0])+':'+self.resolve(val[1])
        return val
    def attrs(self,r):
        return [(self.resolve(r.u2()),r.take(r.u4())) for _ in range(r.u2())]
    def members(self,r):
        values=[]
        for _ in range(r.u2()):
            access=r.u2();name=self.resolve(r.u2());descriptor=self.resolve(r.u2()); attrs=self.attrs(r)
            item=dict(name=name,descriptor=descriptor,access=access)
            for attr,data in attrs:
                if attr=='Code':
                    cr=Reader(data); item['max_stack']=cr.u2();item['max_locals']=cr.u2();item['code']=cr.take(cr.u4())
                elif attr=='ConstantValue': item['constant']=self.resolve(int.from_bytes(data,'big'))
            values.append(item)
        return values
    def references(self):
        return sorted({self.resolve(i) for i,x in enumerate(self.cp) if x and x[0] in (9,10,11)})
    def strings(self):
        return sorted({self.resolve(i) for i,x in enumerate(self.cp) if x and x[0]==8})
    def instructions(self,code):
        p=0
        while p<len(code):
            offset=p; op=code[p];p+=1;operand=None
            if op>0xc9: raise ValueError(f'Reserved/invalid opcode {op:#x} at {offset}')
            if op in (0xaa,0xab):
                p += (-p)%4
                default=struct.unpack('>i',code[p:p+4])[0]; p+=4
                if op==0xaa:
                    lo,hi=struct.unpack('>ii',code[p:p+8]);p+=8
                    assert 0<=hi-lo+1<=len(code)//4
                    p+=4*(hi-lo+1)
                else:
                    pairs=struct.unpack('>i',code[p:p+4])[0];p+=4
                    assert 0<=pairs<=len(code)//8
                    p+=8*pairs
                operand={'default_relative':default}
            elif op==0xc4:
                wide=code[p]; p+=5 if wide==0x84 else 3
            else:
                count=0
                if op in (0x10,0x12,0xa9,0xbc) or 0x15<=op<=0x19 or 0x36<=op<=0x3a: count=1
                elif op in (0x11,0x13,0x14,0x84,0xbb,0xbd,0xc0,0xc1,0xc6,0xc7) or 0x99<=op<=0xa8 or 0xb2<=op<=0xb8: count=2
                elif op==0xc5: count=3
                elif op in (0xb9,0xba,0xc8,0xc9): count=4
                raw=code[p:p+count]; assert len(raw)==count;p+=count
                if op==0x12: operand=self.resolve(raw[0])
                elif op in (0x13,0x14,0xbb,0xbd,0xc0,0xc1,0xc5) or 0xb2<=op<=0xba: operand=self.resolve(int.from_bytes(raw[:2],'big'))
                elif op in (0x10,0x11): operand=int.from_bytes(raw,'big',signed=True)
                elif 0x02<=op<=0x08: operand=op-3
                elif 0x0b<=op<=0x0d: operand=float(op-0x0b)
                elif op in (0x09,0x0a):operand=op-0x09
                elif op in (0x0e,0x0f):operand=float(op-0x0e)
            assert p<=len(code),f'Invalid opcode length at {offset}'
            yield dict(offset=offset,opcode=hex(op),operand=operand)
