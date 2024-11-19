//
// Created by Stephen Wasilewski on 13.11.2024.
//
#include  "Radiance/src/rt/RtraceSimulManager.h"
#include <pybind11/pybind11.h>
#include <iostream>


// global simulation manager
extern RtraceSimulManager	myRTmanager;

extern double  (*sens_curve)(SCOLOR scol);	/* spectral conversion for 1-channel */
extern double  out_scalefactor;		/* output calibration scale factor */
extern RGBPRIMP  out_prims;		/* output color primitives (NULL if spectral) */
extern int setrtoutput(const char *outvals);

typedef void putf_t(RREAL *v, int n);
extern putf_t *putreal;

//for tracking result buffer
long putcount;
extern RREAL *output_values;

static const char  *sigerr[NSIG];	/* signal error messages */
static void onsig(int  signo);
static void sigdie(int  signo, const char  *msg);

void putn(RREAL *v, int n){ /* output to buffer */
    for (int i = 0; i < n; i++){
        output_values[putcount + i] = v[i];
    }
    putcount += n;
}


//modified from rtrace() in rxtrace.cpp
void
rtrace_buffer(				/* trace rays from buffer */
        const double *vptr,
        int nproc,
        int raycount
)
{
    putcount = 0;
    auto * ivbuf = (FVECT *)malloc(2*sizeof(FVECT));
    /* set up output */
    if (castonly) {
        nproc = 1;		/* don't bother multiprocessing */
    } else if (nproc <= 0) {	// need to get default for system?
        nproc = RtraceSimulManager::GetNCores() + nproc;
        if (nproc <= 0) nproc = 1;
    }
    myRTmanager.SetThreadCount(nproc);
    putreal = putn;
    myRTmanager.rtFlags |= RTdoFIFO;

    int n = 1;			/* process input rays */
    int ti = 0;
    bool	pending = false;
    while (raycount > 0) {
        raycount--;
        ivbuf[0][0] = vptr[ti];
        ivbuf[0][1] = vptr[ti+1];
        ivbuf[0][2] = vptr[ti+2];
        ivbuf[1][0] = vptr[ti+3];
        ivbuf[1][1] = vptr[ti+4];
        ivbuf[1][2] = vptr[ti+5];
        ti += 6;
        if (myRTmanager.EnqueueBundle(ivbuf, n) < n)
            throw pybind11::value_error("ray queuing failure");
        bool	atZero = IsZeroVec(ivbuf[2*n-1]);
        if (pending & (atZero)) {
            if (myRTmanager.FlushQueue() <= 0)
                throw pybind11::value_error("ray flush error");
            pending = false;
        } else
            pending |= !atZero;
    }
    if (myRTmanager.FlushQueue() < 0)
        throw pybind11::value_error("final flush error");
    free(ivbuf);
}


//modified from main() in rxtmain.cpp for consistent option parsing
int
setrtargs(int  argc, char  *argv[])
{
#define	 check(ol,al)		if (argv[i][ol] || \
				badarg(argc-i-1,argv+i+1,al)) \
				throw pybind11::value_error("command line error at: " + std::string(argv[i]));
#define	 check_bool(olen,var)		switch (argv[i][olen]) { \
				case '\0': var = !var; break; \
				case 'y': case 'Y': case 't': case 'T': \
				case '+': case '1': var = 1; break; \
				case 'n': case 'N': case 'f': case 'F': \
				case '-': case '0': var = 0; break; \
				default: throw pybind11::value_error("command line error at: " + std::string(argv[i])); }
    int  rval;
    int  i;
    int nproc = 0;
    int rvc = 0;

    /* option city */
    for (i = 0; i < argc; i++) {
        /* expand arguments */
        while ((rval = expandarg(&argc, &argv, i)) > 0)
            ;
        if (rval < 0) {
            throw pybind11::value_error("cannot expand: " + std::string(argv[i]));
        }
        if (argv[i] == NULL || argv[i][0] != '-')
            break;			/* break from options */

        rval = getrenderopt(argc-i, argv+i);
        if (rval >= 0) {
            i += rval;
            continue;
        }
        switch (argv[i][1]) {
            case 'n':				/* number of cores */
                check(2,"i");
                nproc = atoi(argv[++i]);
                break;
            case 'x':				/* x resolution */
                check(2,"i");
                std::cerr << "Warning: -x argument ignored" << std::endl;
                break;
            case 'y':				/* y resolution */
                check(2,"i");
                std::cerr << "Warning: -y argument ignored" << std::endl;
                break;
            case 'w':				/* warnings */
                rval = erract[WARNING].pf != NULL;
                check_bool(2,rval);
                if (rval) erract[WARNING].pf = wputs;
                else erract[WARNING].pf = NULL;
                break;
            case 'e':				/* error file */
                check(2,"s");
                std::cerr << "Warning: -e argument ignored" << std::endl;
//                errfile = argv[++i];
                break;
            case 'l':				/* limit distance */
                if (argv[i][2] != 'd')
                    throw pybind11::value_error("command line error at: " + std::string(argv[i]));
                rval = myRTmanager.rtFlags & RTlimDist;
                check_bool(3,rval);
                if (rval) myRTmanager.rtFlags |= RTlimDist;
                else myRTmanager.rtFlags &= ~RTlimDist;
                break;
            case 'I':				/* immed. irradiance */
                rval = myRTmanager.rtFlags & RTimmIrrad;
                check_bool(3,rval);
                if (rval) myRTmanager.rtFlags |= RTimmIrrad;
                else myRTmanager.rtFlags &= ~RTimmIrrad;
                break;
            case 'f':				/* format i/o */
                std::cerr << "Warning: -f argument ignored" << std::endl;
            case 'o':				/* output */
                rvc = setrtoutput(argv[i]+2);
                break;
            case 'h':				/* header output */
                std::cerr << "Warning: -f argument ignored" << std::endl;
                break;
            case 't':				/* trace */
                std::cerr << "Warning: -t argument ignored" << std::endl;
#if MAXCSAMP>3
            case 'c':				/* output spectral results */
                if (argv[i][2] != 'o')
                    throw pybind11::value_error("command line error at: " + std::string(argv[i]));
                rval = (out_prims == NULL) & (sens_curve == NULL);
                check_bool(3,rval);
                if (rval) {
                    out_prims = NULL;
                    sens_curve = NULL;
                } else if (out_prims == NULL)
                    out_prims = stdprims;
                break;
#endif
            default:
                throw pybind11::value_error("command line error at: " + std::string(argv[i]));
        }
    }
    /* set/check spectral sampling */
    rval = setspectrsamp(CNDX, WLPART);
    if (rval < 0)
        throw pybind11::value_error("unsupported spectral sampling");
    if (out_prims != NULL) {
        if (!rval)
            throw pybind11::value_error("spectral range incompatible with color output");
    } else if (NCSAMP == 3)
        out_prims = stdprims;	/* 3 samples do not a spectrum make */
    /* set up signal handling */
    sigdie(SIGINT, "Interrupt");
#ifdef SIGHUP
    sigdie(SIGHUP, "Hangup");
#endif
    sigdie(SIGTERM, "Terminate");
#ifdef SIGPIPE
    sigdie(SIGPIPE, "Broken pipe");
#endif
#ifdef SIGALRM
    sigdie(SIGALRM, "Alarm clock");
#endif
#ifdef	SIGXCPU
    sigdie(SIGXCPU, "CPU limit exceeded");
    sigdie(SIGXFSZ, "File size exceeded");
#endif
    if (i == argc - 1)
        if (!myRTmanager.LoadOctree(argv[i]))
            throw pybind11::value_error("error loading octree: " + std::string(argv[i]));
    if (nproc != 0)
        myRTmanager.SetThreadCount(nproc);
#undef	check
#undef	check_bool
    return rvc;
}

static void
onsig(				/* fatal signal */
        int  signo
)
{
    static int  gotsig = 0;

    if (gotsig++)			/* two signals and we're gone! */
        _exit(signo);

#ifdef SIGALRM
    alarm(15);			/* allow 15 seconds to clean up */
    signal(SIGALRM, SIG_DFL);	/* make certain we do die */
#endif
    eputs("signal - ");
    eputs(sigerr[signo]);
    eputs("\n");
    quit(3);
}

static void
sigdie(			/* set fatal signal */
        int  signo,
        const char  *msg
)
{
    if (signal(signo, onsig) == SIG_IGN)
        signal(signo, SIG_IGN);
    sigerr[signo] = msg;
}