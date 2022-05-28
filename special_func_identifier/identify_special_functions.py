import ida_funcs
import ida_name
import ida_xref
import idautils
import idaapi
import ida_allins
from enum import Enum

from typing import Dict


class FUNCTION_TYPE(str, Enum):
    NULLSUB = ("nullsub",)
    IDENTITY = ("identity",)
    GETVALUE = ("getvalue",)
    OTHER = ("unknown",)


# dummy
visited: Dict[int, bool] = {}


'''
infer function by heuristics rules
ea: function address
func_type: type of the function that ea called to
'''
def infer_function_type(ea: int, callee_type:FUNCTION_TYPE) -> FUNCTION_TYPE:

    func = ida_funcs.get_func(ea)
    if func == None:
        return FUNCTION_TYPE.OTHER
    func_size = func.end_ea - func.start_ea
    # function larger than 0x30 bytes is type other
    if func_size > 0x30:
        return FUNCTION_TYPE.OTHER
    try:
        code = str(idaapi.decompile(ea))
    except:
        print(f"decompile failed for func {hex(ea)}")
        return FUNCTION_TYPE.OTHER
    code_lines = code.split("\n")
    # function more than five lines is type other
    if len(code_lines) > 5:
        return FUNCTION_TYPE.OTHER
    # nullsub function only have a single ';' 
    if code_lines[2] == "  ;":
        return FUNCTION_TYPE.NULLSUB
    # if there is only a return subXXX() statement, then it's type depends on its callee
    if code_lines[2].find("return") > 0 and callee_type != FUNCTION_TYPE.OTHER:
        return callee_type
    # if there is only a return a1 statement, then it's type is identity 
    if code_lines[2].find("return a1;") > 0:
        return FUNCTION_TYPE.IDENTITY
    # if there is only a return *a1 statement, then it's type is getvalue
    # todo: dealing with more getvalue type rather than QWORD 
    if code_lines[2].find("return *(_QWORD *)a1;") > 0:
        return FUNCTION_TYPE.GETVALUE

    return FUNCTION_TYPE.OTHER

'''
propagating function type bottom up by call graph
ea: function address
func_type: type of the function
'''
def propagate_function_type(ea: int, func_type: FUNCTION_TYPE):
    print(f"propagate func {hex(ea)}, type {func_type}")

    if visited.get(ea) is not None:
        return
    if func_type == FUNCTION_TYPE.NULLSUB:
        ida_name.set_name(ea, f"nullsub_{hex(ea)[2:]}")
    elif func_type == FUNCTION_TYPE.IDENTITY:
        ida_name.set_name(ea, f"identity_{hex(ea)[2:]}")
    elif func_type == FUNCTION_TYPE.GETVALUE:
        ida_name.set_name(ea, f"getvalue_{hex(ea)[2:]}")
    
    visited[ea] = True
    cref = ida_xref.get_first_cref_to(ea)
    while cref != idaapi.BADADDR:
        cref_func = ida_funcs.get_func(cref)
        #function is not defined or function has been visited
        if cref_func is None or visited.get(cref_func.start_ea) is not None:
            cref = ida_xref.get_next_cref_to(ea, cref)
            continue
        cref_func_type = infer_function_type(cref_func.start_ea, func_type)
        if cref_func_type == FUNCTION_TYPE.OTHER:
            cref = ida_xref.get_next_cref_to(ea, cref)
            visited[cref_func.start_ea] = True
            continue
        propagate_function_type(cref_func.start_ea, cref_func_type)
        cref = ida_xref.get_next_cref_to(ea, cref)



def main():
    for ea in Functions():
        func_type = infer_function_type(ea, FUNCTION_TYPE.OTHER)
        if func_type == FUNCTION_TYPE.OTHER:
            continue

        propagate_function_type(ea, func_type)


if __name__ == "__main__":
    main()
