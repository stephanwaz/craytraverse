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

int PyRtraceSimulManager::LoadOctree(const char *octn) {
    renderer->LoadOctree(octn);
    check_for_errors();
    renderer->SetCookedCall(printvals); //now Ready should return True
    return nobjects;
}

bool PyRtraceSimulManager::Ready() {
    return renderer->Ready() && rvc > 0;
}

void PyRtraceSimulManager::reset_settings() {
    ray_restore(nullptr);
    sens_curve = nullptr;
    out_scalefactor = 1;
    out_prims = stdprims;
    renderer->rtFlags = 0;
}

int PyRtraceSimulManager::Cleanup(bool everything) {
    reset_settings();
    return renderer->Cleanup(everything);
}

int PyRtraceSimulManager::SetThreadCount(int nproc) {
    proc = renderer->SetThreadCount(nproc);
    return proc;
}

int PyRtraceSimulManager::NThreads() {
    return renderer->NThreads();
}

u_long PyRtraceSimulManager::set_output(const char *outvals) {
    rvc = setrtoutput(outvals);
    check_for_errors();
    SetThreadCount(proc);
    return rvc;
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
    auto *outdata = new RREAL[rows * rvc];

    // Delete 'outdata' when the 'owner' capsule expires
    nb::capsule owner(outdata, [](void *p) noexcept {
        delete[] (float *) p;
    });
    output_values = outdata; //point to our output data
    rtrace_buffer(vptr, nproc, rows);
    output_values = nullptr;
    return OUTTYPE(outdata,{ rows, rvc }, owner);
}

void PyRtraceSimulManager::set_args(const nb::list& arglist, bool reset) {
    int argc = (int)arglist.size();
    char **argv = (char**)malloc(argc * sizeof(char*));

    for (int i = 0; i < argc; ++i)
        argv[i] = (char*)PyUnicode_AsUTF8(arglist[i].ptr());
    if (reset) {
        reset_settings();
    }
    rvc = setrtargs(argc, argv);
    if (nobjects > 0)
        renderer->SetCookedCall(printvals); //now Ready will return True in case octree is set this way
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
        set_args(arglist);
    }
}


using namespace nb::literals;

NB_MODULE(pyrtrace, m){
nb::class_<PyRtraceSimulManager>(m, "pyRtrace")
    .def_ro("rvc", &PyRtraceSimulManager::rvc, "the expected return value count per ray")
        .def_ro("proc", &PyRtraceSimulManager::proc, "the number of processors for rendering")
    .def(nb::init<const nb::list>(), "arglist"_a=nb::list(), "arglist should be a list of strings "
                                         "matching command line arguments. use shlex.split()")
    .def("LoadOctree", &PyRtraceSimulManager::LoadOctree, "octn"_a)
    .def("Ready", &PyRtraceSimulManager::Ready)
    .def("Cleanup", &PyRtraceSimulManager::Cleanup, "everything"_a = false)
    .def("SetThreadCount", &PyRtraceSimulManager::SetThreadCount, "nproc"_a = 0, R"nbdoc(Set process count for radiance.
Notes
-----
 - By default will use sysconf(_SC_NPROCESSORS_ONLN)).
 - has no effect until after LoadOctree.)nbdoc")
    .def("set_output", &PyRtraceSimulManager::set_output, "outvals"_a = "ov")
    .def("set_args", &PyRtraceSimulManager::set_args, "arglist"_a, "reset"_a = false)
    .def("__call__", &PyRtraceSimulManager::trace, "vecs"_a, "nproc"_a = -1);
}


