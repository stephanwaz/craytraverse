//
// Created by Stephen Wasilewski on 13.11.2024.
//

#ifndef CRAYTRAVERSE_PYRTRACESIMULMANAGER_H
#define CRAYTRAVERSE_PYRTRACESIMULMANAGER_H

#include "Radiance/src/rt/RtraceSimulManager.h"
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

namespace py = pybind11;

//declarations needed by rxtrace that are defined in rxtmain (which is not part of this target)
double  (*sens_curve)(const SCOLOR scol) = nullptr;	/* spectral conversion for 1-channel */
double  out_scalefactor = 1;		/* output calibration scale factor */
RGBPRIMP  out_prims = stdprims;		/* output color primitives (NULL if spectral) */
RtraceSimulManager	myRTmanager;	// global simulation manager
int  inform = 'a';			/* input format */
int  outform = 'a';			/* output format */

//defined in rxtrace.cpp
extern RayReportCall printvals;
extern void putn(RREAL *v, int n);

//for tracking result buffer
RREAL *output_values;



//defined in rxtrace_py.cpp
extern int setrtoutput(const char *outvals);	/* set output values */
void rtrace_buffer(const double *vptr, int nproc, int raycount);
int setrtargs(int  argc, char  *argv[]);

typedef py::array_t<double, py::array::c_style> INRAYTYPE;

static void check_for_errors();

class PyRtraceSimulManager {
private:
    RtraceSimulManager* renderer;
    int proc;

public:
    int rvc;
    explicit PyRtraceSimulManager(const char *octn = nullptr, const py::list& arglist = py::none(), int nproc = 0);
    ~PyRtraceSimulManager() = default;

    //these all directly implement RtraceSimulManager methods
    bool LoadOctree(const char *octn);
    bool Ready();
    int Cleanup(bool everything = false);
    int SetThreadCount(int nproc = 0);
    int NThreads();

    //ADDITIONAL METHODS
    void set_args(const py::list& arglist);
    int set_output(const char *outvals);
    int obj_count(); // return number of objects loaded
    int get_render_settings();

    py::array_t<double> trace(INRAYTYPE &vecs, int nproc = -1);
};




#endif //CRAYTRAVERSE_PYRTRACESIMULMANAGER_H
