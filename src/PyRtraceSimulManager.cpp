//
// Created by Stephen Wasilewski on 13.11.2024.
//

#include "PyRtraceSimulManager.h"
#include <iostream>

extern int global_error_code;

// this might have stability problems, so far if it works for "fatal" (setrtoutput with bad value)
// but not "system" (try to load an octree that does not exist) errors,
// but it probably just depends how much is left in the function and whether anything downstream
// gets into nasty trouble
void check_for_errors() {
    if (global_error_code != 0){
        global_error_code = 0; //in case we decide to try and recover
        throw nb::value_error(errmsg);
    }
}

bool PyRtraceSimulManager::LoadOctree(const char *octn) {
    bool loaded = renderer->LoadOctree(octn);
    check_for_errors();
    renderer->SetCookedCall(printvals); //so Ready will return True
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

OUTTYPE PyRtraceSimulManager::trace(INRAYTYPE &vecs, int nproc) {
    if (!Ready())
        throw nb::value_error("Simulation Manager is not Ready!");
    if(nproc >= 0)
        proc = nproc;
    renderer->SetThreadCount(proc);
    u_long rows = vecs.shape(0);
    auto vptr = vecs.data();

    // Allocate a memory region an initialize it
    RREAL *outdata = new RREAL[rows * rvc];

    // Delete 'outdata' when the 'owner' capsule expires
    nb::capsule owner(outdata, [](void *p) noexcept {
        delete[] (float *) p;
    });
    output_values = outdata; //point to our output data
    rtrace_buffer(vptr, nproc, rows);
    output_values = nullptr;
    return OUTTYPE(outdata,{ rows, rvc }, owner);
}

void PyRtraceSimulManager::set_args(const nb::list& arglist) {
    int argc = (int)arglist.size();
    char **argv = (char**)malloc(argc * sizeof(char*));

    for (int i = 0; i < argc; ++i)
        argv[i] = (char*)PyUnicode_AsUTF8(arglist[i].ptr());

    rvc = setrtargs(argc, argv);
    if (obj_count() > 0)
        renderer->SetCookedCall(printvals);
    free(argv);
    proc = NThreads();
    check_for_errors();
}

PyRtraceSimulManager::PyRtraceSimulManager(const nb::list &arglist) {
    //every python instance points back to the same instance
    renderer = &myRTmanager;
    rvc = 0;
    proc = NThreads();
    if (len(arglist) > 0) {
        std::cerr << "setting arguments " << std::endl;
        set_args(arglist);
    }
}


using namespace nb::literals;

NB_MODULE(pyrtrace, m){
nb::class_<PyRtraceSimulManager>(m, "pyRtrace")
    .def_ro("rvc", &PyRtraceSimulManager::rvc, "the expected return value count per ray")
    .def(nb::init<const nb::list>(), "arglist"_a=nb::list())
    .def("LoadOctree", &PyRtraceSimulManager::LoadOctree, "octn"_a)
    .def("Ready", &PyRtraceSimulManager::Ready)
    .def("Cleanup", &PyRtraceSimulManager::Cleanup, "everything"_a = false)
    .def("SetThreadCount", &PyRtraceSimulManager::SetThreadCount, "nproc"_a = 0, R"nbdoc(Set process count for radiance.
Notes
-----
 - By default will use sysconf(_SC_NPROCESSORS_ONLN)).
 - has no effect until after LoadOctree.)nbdoc")
    .def("NThreads", &PyRtraceSimulManager::NThreads)
    .def("obj_count", &PyRtraceSimulManager::obj_count)
    .def("set_output", &PyRtraceSimulManager::set_output)
    .def("set_args", &PyRtraceSimulManager::set_args, "arglist"_a)
    .def("get_render_settings", &PyRtraceSimulManager::get_render_settings)
    .def("__call__", &PyRtraceSimulManager::trace, "vecs"_a, "nproc"_a = -1);
}


