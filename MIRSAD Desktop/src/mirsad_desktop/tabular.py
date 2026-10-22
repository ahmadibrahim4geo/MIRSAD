"""Reiterable row spool: bounded RAM while preparing daily Excel tables."""
import itertools
import json
import tempfile
import threading


class RowBuffer:
    def __init__(self,memory_bytes=1024*1024):
        self._file=tempfile.SpooledTemporaryFile(max_size=memory_bytes,mode="w+t",encoding="utf-8",newline="\n")
        self._count=0;self._lock=threading.RLock()

    def append(self,row):
        text=json.dumps(list(row),ensure_ascii=False,allow_nan=False,separators=(",",":"))+"\n"
        with self._lock:
            self._file.seek(0,2);self._file.write(text);self._count+=1

    def __len__(self):return self._count

    def __iter__(self):
        position=0
        while True:
            with self._lock:
                self._file.seek(position);line=self._file.readline();position=self._file.tell()
            if not line:break
            yield json.loads(line)

    def __getitem__(self,key):
        if isinstance(key,slice):
            start,stop,step=key.indices(len(self))
            if step<=0:raise ValueError("Row slices require a positive step")
            return list(itertools.islice(self,start,stop,step))
        if key<0:key+=len(self)
        if not 0<=key<len(self):raise IndexError(key)
        return next(itertools.islice(self,key,key+1))

    def __eq__(self,other):
        if hasattr(other,"__len__") and len(other)!=len(self):return False
        return list(self)==list(other)

    def close(self):self._file.close()

    def __del__(self):
        handle=getattr(self,"_file",None)
        if handle is not None:handle.close()
