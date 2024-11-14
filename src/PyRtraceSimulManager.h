//
// Created by Stephen Wasilewski on 13.11.2024.
//

#ifndef CRAYTRAVERSE_PYRTRACESIMULMANAGER_H
#define CRAYTRAVERSE_PYRTRACESIMULMANAGER_H

#include "Radiance/src/rt/RtraceSimulManager.h"
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

namespace py = pybind11;

//declarations needed from rxtmain in rxtrace_py
double  (*sens_curve)(const SCOLOR scol) = NULL;	/* spectral conversion for 1-channel */
double  out_scalefactor = 1;		/* output calibration scale factor */
RGBPRIMP  out_prims = stdprims;		/* output color primitives (NULL if spectral) */
RtraceSimulManager	myRTmanager;	// global simulation manager
int  inform = 'a';			/* input format */
int  outform = 'a';			/* output format */

//need to define

static void check_for_errors();

class PyRtraceSimulManager {
private:
    //make sure another RtraceSimulManager is never created from python side
    RtraceSimulManager* renderer;
    int rvc;

public:
    PyRtraceSimulManager() {
        //every python instance points back to this
        renderer = &myRTmanager;
    }
    ~PyRtraceSimulManager() = default;

    //these all directly implement RtraceSimulManager methods
    bool LoadOctree(const char *octn);
    bool Ready();
    int Cleanup(bool everything = false);

    //ADDITIONAL METHODS
    int set_output(const char *outvals);
    int obj_count(); // return number of objects loaded
    py::array_t<double> trace(py::array_t<double, py::array::c_style> &vecs, int nproc = 0);

};


#endif //CRAYTRAVERSE_PYRTRACESIMULMANAGER_H
