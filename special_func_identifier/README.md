# Special Function Idetifier 

An IDA script that identifies the special functions in a binary and renamed it.


## usage

File->scirpt file->select identify_special_functions.py

## How it works

1. Identify functions by pattern matching of decompiled code.
2. propagated results by call graph recursively



## Supported Function Type


### nullsub

```
void sub_152D6()
{
  ;
}
```

### identity

```
__int64 __fastcall sub_13516(__int64 a1)
{
  return a1;
}
```

### getvalue

```
__int64 __fastcall getvalue_15f66(__int64 a1)
{
  return *(_QWORD *)a1;

```


