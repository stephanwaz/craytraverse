//
// Created by Stephen Wasilewski on 13.11.2024.
//

#include "PyRtraceSimulManager.h"
#include <iostream>

char const * errcodes[4] = {"warning","fatal","system", "internal"};

extern int global_error_code;

//references to needed objects is rxtrace_py.cpp
extern int setrtoutput(const char *outvals);	/* set output values */
extern void rtrace_buffer(const double *vptr, int nproc, int raycount);

//for tracking result buffer
extern long putcount;
extern RREAL *output_values;


// this might have stability problems, so far if it works for "fatal" (setrtoutput with bad value)
// but not "system" (try to load an octree that does not exist) errors,
// but it probably just depends how much is left in the function and whether anything downstream
// gets into nasty trouble
void check_for_errors() {
    if (global_error_code != 0){
        std::string message = std::string(errcodes[global_error_code]) + " - " + errmsg;
        global_error_code = 0; //in case we decide to try and recover
        throw pybind11::value_error(message);
    }
}

bool PyRtraceSimulManager::LoadOctree(const char *octn) {
    bool loaded = renderer->LoadOctree(octn);
    check_for_errors();
    return loaded;
}

bool PyRtraceSimulManager::Ready() {
    return renderer->Ready();
}

int PyRtraceSimulManager::Cleanup(bool everything) {
    return renderer->Cleanup(everything);
}

int PyRtraceSimulManager::set_output(const char *outvals) {
    rvc = setrtoutput(outvals);
    check_for_errors();
    return rvc;
}

int PyRtraceSimulManager::obj_count() {
    return nobjects;
}

py::array_t<double> PyRtraceSimulManager::trace(py::array_t<double, py::array::c_style> &vecs, int nproc) {

    int rows = vecs.shape(0);
    py::buffer_info vbuff = vecs.request();
    auto *vptr = (double *) vbuff.ptr;

    output_values = (RREAL *)malloc(sizeof(RREAL) * rows * rvc);
    rtrace_buffer(vptr, nproc, rows);
    return py::array_t<double>({rows, rvc}, output_values);
}


using namespace pybind11::literals;

PYBIND11_MODULE(pyrtrace, m){
py::class_<PyRtraceSimulManager>(m, "pyRtrace", py::module_local())
    .def(py::init<>())
    .def("LoadOctree", &PyRtraceSimulManager::LoadOctree, "octn"_a)
    .def("Ready", &PyRtraceSimulManager::Ready)
    .def("Cleanup", &PyRtraceSimulManager::Cleanup, "everything"_a = false)
    .def("obj_count", &PyRtraceSimulManager::obj_count)
    .def("set_output", &PyRtraceSimulManager::set_output)
    .def("__call__", &PyRtraceSimulManager::trace, "vecs"_a, "nproc"_a = 0);
}


