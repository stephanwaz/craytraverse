//
// Created by Stephen Wasilewski on 13.11.2024.
//

#ifndef CRAYTRAVERSE_PYRTRACESIMULMANAGER_H
#define CRAYTRAVERSE_PYRTRACESIMULMANAGER_H

#include "Radiance/src/rt/RtraceSimulManager.h"
#include <nanobind/nanobind.h>
#include <nanobind/ndarray.h>

namespace nb = nanobind;

//declarations needed by rxtrace that are defined in rxtmain (which is not part of this target)
double  (*sens_curve)(const SCOLOR scol) = nullptr;	/* spectral conversion for 1-channel */
double  out_scalefactor = 1;		/* output calibration scale factor */
RGBPRIMP  out_prims = stdprims;		/* output color primitives (NULL if spectral) */
RtraceSimulManager	myRTmanager;	// global simulation manager
int  inform = 'd';			/* input format */
int  outform = 'd';			/* output format */

//defined in rxtrace.cpp
extern RayReportCall printvals;
extern void putn(RREAL *v, int n);

//for tracking result buffer
RREAL *output_values = nullptr;

//defined in rxtrace_py.cpp
extern int setrtoutput(const char *outvals);	/* set output values */
void rtrace_buffer(const double *vptr, int nproc, u_long raycount);
int setrtargs(int  argc, char  *argv[]);

typedef nb::ndarray<double, nb::c_contig, nb::shape<-1, 6>, nb::ro> INRAYTYPE;
typedef nb::ndarray<nb::numpy, double, nb::ndim<2>> OUTTYPE;

static void check_for_errors();

class PyRtraceSimulManager {
private:
    RtraceSimulManager* renderer;
    void reset_settings();

public:
    u_long rvc;
    int proc;
    //either completely setup manager by calling with an argument list that includes
    //octree and -n X for multiprocessing or declare empty and then call LoadOctree
    // and set_args/SetThreadCount/set_output
    explicit PyRtraceSimulManager(const nb::list& arglist = nb::list());
    ~PyRtraceSimulManager() = default;

    //these all analogues of RtraceSimulManager methods (with some additional side effects)
    int LoadOctree(const char *octn);
    bool Ready();
    int Cleanup(bool everything = false);
    int SetThreadCount(int nproc = 0);
    int NThreads();

    //ADDITIONAL METHODS
    void set_args(const nb::list& arglist, bool reset = false);
    u_long set_output(const char *outvals);
    //the main simulation call
    OUTTYPE trace(INRAYTYPE &vecs, int nproc = -1);
};




#endif //CRAYTRAVERSE_PYRTRACESIMULMANAGER_H
