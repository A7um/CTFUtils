import ida_idaapi
import ida_hexrays
import idc
objcrt_list = []
objcrt_list.append(idc.get_name_ea_simple("_objc_retainAutoreleasedReturnValue"))
objcrt_list.append(idc.get_name_ea_simple("_objc_retainAutoreleaseReturnValue"))
objcrt_list.append(idc.get_name_ea_simple("_objc_retain"))
objcrt_list.append(idc.get_name_ea_simple("_objc_release"))


class objcrt_cleaner_optinsn_t(ida_hexrays.optinsn_t):

    def __init__(self):
        ida_hexrays.optinsn_t.__init__(self)
    
    def visit_subcall(self,ins):
        callins=ins.l.d
        if(callins.l.t==0x6 and callins.l.g in objcrt_list):
            if(callins.d.f==None):
                return 0
            else: 
                ins.l=ida_hexrays.mop_t(callins.d.f.args[0])
                return 1

        return 0
    def visit_call(self,callins):
        if(callins.l.t==0x6 and callins.l.g in objcrt_list):
            if(callins.d.f==None):
                return 0
            elif(callins.d.f.return_regs.reg.dstr()==''):                  
                callins._make_nop()
                return 1
        return 0
    def func(self,blk,ins,optflag):
        cnt=0
        if(optflag&ida_hexrays.OPTI_NO_LDXOPT==ida_hexrays.OPTI_NO_LDXOPT):
            return 0
        if(ins.opcode==ida_hexrays.m_call):
            cnt = self.visit_call(ins)
        elif(ins.contains_opcode(ida_hexrays.m_call)):
            cnt = self.visit_subcall(ins)
        if cnt != 0:                
            blk.mba.verify(True)        
        return cnt

oc = objcrt_cleaner_optinsn_t()
oc.install()
