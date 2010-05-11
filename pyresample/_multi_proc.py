#pyresample, Resampling of remote sensing image data in python
# 
#Copyright (C) 2010  Esben S. Nielsen
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import ctypes

import multiprocessing as mp
import numpy

class Scheduler(object):
    
    def __init__(self, ndata, nprocs, chunk=None, schedule='guided'):
        if not schedule in ['guided','dynamic', 'static']:
            raise ValueError, 'unknown scheduling strategy'
        self._ndata = mp.RawValue(ctypes.c_int, ndata)
        self._start = mp.RawValue(ctypes.c_int, 0)
        self._lock = mp.Lock()
        self._schedule = schedule
        self._nprocs = nprocs
        if schedule == 'guided' or schedule == 'dynamic':
            min_chunk = ndata // (10*nprocs)
            if chunk:
                min_chunk = chunk
            min_chunk = max(min_chunk, 1)
            self._chunk = min_chunk
        elif schedule == 'static':
            min_chunk = ndata // nprocs
            if chunk:
                min_chunk = max(chunk, min_chunk)
            min_chunk = max(min_chunk, 1)
            self._chunk = min_chunk
            
    def __iter__(self):
        return self

    def next(self):
        self._lock.acquire()
        ndata = self._ndata.value
        nprocs = self._nprocs
        start = self._start.value
        if self._schedule == 'guided':
            _chunk = ndata // nprocs
            chunk = max(self._chunk, _chunk)
        else:
            chunk = self._chunk
        if ndata:
            if chunk > ndata:
                s0 = start
                s1 = start + ndata
                self._ndata.value = 0
            else:
                s0 = start
                s1 = start + chunk
                self._ndata.value = ndata - chunk
                self._start.value = start + chunk
            self._lock.release()
            return slice(s0, s1)
        else:
            self._lock.release()
            raise StopIteration


def shmem_as_ndarray(raw_array):
    _ctypes_to_numpy = {
                        ctypes.c_char : numpy.int8,
                        ctypes.c_wchar : numpy.int16,
                        ctypes.c_byte : numpy.int8,
                        ctypes.c_ubyte : numpy.uint8,
                        ctypes.c_short : numpy.int16,
                        ctypes.c_ushort : numpy.uint16,
                        ctypes.c_int : numpy.int32,
                        ctypes.c_uint : numpy.int32,
                        ctypes.c_long : numpy.int32,
                        ctypes.c_ulong : numpy.int32,
                        ctypes.c_float : numpy.float32,
                        ctypes.c_double : numpy.float64
                        }
    address = raw_array._wrapper.get_address()
    size = raw_array._wrapper.get_size()
    dtype = _ctypes_to_numpy[raw_array._type_]
    class Dummy(object): pass
    d = Dummy()
    d.__array_interface__ = {
                             'data' : (address, False),
                             'typestr' : numpy.dtype(numpy.uint8).str,
                             'descr' : numpy.dtype(numpy.uint8).descr,
                             'shape' : (size,),
                             'strides' : None,
                             'version' : 3
                             }                            
    return numpy.asarray(d).view(dtype=dtype)