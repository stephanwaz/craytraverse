//
// Created by Stephen Wasilewski on 13.11.2024.
//

#include "PyRtraceSimulManager.h"
#include <iostream>

char const * errcodes[4] = {"warning","fatal","system", "internal"};

extern int global_error_code;




// this might have stability problems, so far if it works for "fatal" (setrtoutput with bad value)
// but not "system" (try to load an octree that does not exist) errors,
// but it probably just depends how much is left in the function and whether anything downstream
// gets into nasty trouble
void check_for_errors() {
    if (global_error_code != 0){
        std::string message = std::string(errcodes[global_error_code]) + " - " + errmsg;
        global_error_code = 0; //in case we decide to try and recover
        throw py::value_error(message);
    }
}



bool PyRtraceSimulManager::LoadOctree(const char *octn) {
    bool loaded = renderer->LoadOctree(octn);
    check_for_errors();
    myRTmanager.SetCookedCall(printvals);
    return loaded;
}

bool PyRtraceSimulManager::Ready() {
    return renderer->Ready() && rvc > 0;
}

int PyRtraceSimulManager::Cleanup(bool everything) {
    return renderer->Cleanup(everything);
}

int PyRtraceSimulManager::SetThreadCount(int nproc) {
    proc = renderer->SetThreadCount(nproc);
    return proc;
}

int PyRtraceSimulManager::NThreads() {
    return renderer->NThreads();
}

int PyRtraceSimulManager::set_output(const char *outvals) {
    rvc = setrtoutput(outvals);
    check_for_errors();
    SetThreadCount(proc);
    return rvc;
}

int PyRtraceSimulManager::obj_count() {
    return nobjects;
}

int PyRtraceSimulManager::get_render_settings() {
    return castonly;
}

py::array_t<double> PyRtraceSimulManager::trace(INRAYTYPE &vecs, int nproc) {
    if (!Ready())
        throw py::value_error("Simulation Manager is not Ready!");
    if(nproc >= 0)
        proc = nproc;
    myRTmanager.SetThreadCount(proc);
    int rows = vecs.shape(0);
    py::buffer_info vbuff = vecs.request();
    auto *vptr = (double *) vbuff.ptr;

    output_values = (RREAL *)malloc(sizeof(RREAL) * rows * rvc);
    rtrace_buffer(vptr, nproc, rows);
    return py::array_t<double>({rows, rvc}, output_values);
}

void PyRtraceSimulManager::set_args(const py::list& arglist) {
    int argc = (int)arglist.size();
    char **argv = (char**)malloc(argc * sizeof(char*));

    for (int i = 0; i < argc; ++i)
        argv[i] = (char*)PyUnicode_AsUTF8(arglist[i].ptr());

    rvc = setrtargs(argc, argv);
    free(argv);
    check_for_errors();
    SetThreadCount(proc);
}

PyRtraceSimulManager::PyRtraceSimulManager(const char *octn, const py::list &arglist, int nproc) {
    //every python instance points back to the same instance
    renderer = &myRTmanager;
    rvc = 0;
    proc = nproc;
    if (octn != nullptr){
        std::cerr << "Attempting to load octree " << octn << std::endl;
        LoadOctree(octn);
    }
    if (!arglist.is(py::none())) {
        std::cerr << "setting arguments " << octn << std::endl;
        set_args(arglist);
    }
}


using namespace pybind11::literals;

PYBIND11_MODULE(pyrtrace, m){
py::class_<PyRtraceSimulManager>(m, "pyRtrace", py::module_local())
    .def_readonly("rvc", &PyRtraceSimulManager::rvc, R"pbdoc(the expected return value count per ray)pbdoc")
    .def(py::init<const char *, const py::list, int>(), "octn"_a= nullptr, "arglist"_a=py::none(), "nproc"_a=0)
    .def("LoadOctree", &PyRtraceSimulManager::LoadOctree, "octn"_a)
    .def("Ready", &PyRtraceSimulManager::Ready)
    .def("Cleanup", &PyRtraceSimulManager::Cleanup, "everything"_a = false)
    .def("SetThreadCount", &PyRtraceSimulManager::SetThreadCount, "nproc"_a = 0, R"pbdoc(Set process count for radiance.
Notes
-----
 - By default will use sysconf(_SC_NPROCESSORS_ONLN)).
 - has no effect until after LoadOctree.)pbdoc")
    .def("NThreads", &PyRtraceSimulManager::NThreads)
    .def("obj_count", &PyRtraceSimulManager::obj_count)
    .def("set_output", &PyRtraceSimulManager::set_output)
    .def("set_args", &PyRtraceSimulManager::set_args, "arglist"_a)
    .def("get_render_settings", &PyRtraceSimulManager::get_render_settings)
    .def("__call__", &PyRtraceSimulManager::trace, "vecs"_a, "nproc"_a = -1);
}


