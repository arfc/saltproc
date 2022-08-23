
% Increase counter:

if (exist('idx', 'var'));
  idx = idx + 1;
else;
  idx = 1;
end;

% Version, title and date:

VERSION                   (idx, [1: 14])  = 'Serpent 2.1.31' ;
COMPILE_DATE              (idx, [1: 20])  = 'May 16 2019 12:25:40' ;
DEBUG                     (idx, 1)        = 0 ;
TITLE                     (idx, [1:  8])  = 'Untitled' ;
CONFIDENTIAL_DATA         (idx, 1)        = 0 ;
INPUT_FILE_NAME           (idx, [1: 69])  = '/home/andrei2/Desktop/git/saltproc/develop/saltproc/data/saltproc_tap' ;
WORKING_DIRECTORY         (idx, [1: 51])  = '/home/andrei2/Desktop/git/saltproc/develop/saltproc' ;
HOSTNAME                  (idx, [1: 28])  = 'andrei2-Precision-Tower-3420' ;
CPU_TYPE                  (idx, [1: 41])  = 'Intel(R) Xeon(R) CPU E3-1225 v5 @ 3.30GHz' ;
CPU_MHZ                   (idx, 1)        = 186.0 ;
START_DATE                (idx, [1: 24])  = 'Tue May 28 19:35:49 2019' ;
COMPLETE_DATE             (idx, [1: 24])  = 'Tue May 28 20:05:39 2019' ;

% Run parameters:

POP                       (idx, 1)        = 50000 ;
CYCLES                    (idx, 1)        = 300 ;
SKIP                      (idx, 1)        = 120 ;
BATCH_INTERVAL            (idx, 1)        = 1 ;
SRC_NORM_MODE             (idx, 1)        = 2 ;
SEED                      (idx, 1)        = 1559090149611 ;
UFS_MODE                  (idx, 1)        = 0 ;
UFS_ORDER                 (idx, 1)        = 1.00000;
NEUTRON_TRANSPORT_MODE    (idx, 1)        = 1 ;
PHOTON_TRANSPORT_MODE     (idx, 1)        = 0 ;
GROUP_CONSTANT_GENERATION (idx, 1)        = 1 ;
B1_CALCULATION            (idx, [1:  3])  = [ 0 0 0 ];
B1_BURNUP_CORRECTION      (idx, 1)        = 0 ;

CRIT_SPEC_MODE            (idx, 1)        = 0 ;
IMPLICIT_REACTION_RATES   (idx, 1)        = 1 ;

% Optimization:

OPTIMIZATION_MODE         (idx, 1)        = 4 ;
RECONSTRUCT_MICROXS       (idx, 1)        = 1 ;
RECONSTRUCT_MACROXS       (idx, 1)        = 1 ;
DOUBLE_INDEXING           (idx, 1)        = 0 ;
MG_MAJORANT_MODE          (idx, 1)        = 0 ;
SPECTRUM_COLLAPSE         (idx, 1)        = 1 ;

% Parallelization:

MPI_TASKS                 (idx, 1)        = 1 ;
OMP_THREADS               (idx, 1)        = 4 ;
MPI_REPRODUCIBILITY       (idx, 1)        = 0 ;
OMP_REPRODUCIBILITY       (idx, 1)        = 1 ;
OMP_HISTORY_PROFILE       (idx, [1:   4]) = [  9.97211E-01  9.99787E-01  1.00305E+00  9.99947E-01  ];
SHARE_BUF_ARRAY           (idx, 1)        = 0 ;
SHARE_RES2_ARRAY          (idx, 1)        = 1 ;
OMP_SHARED_QUEUE_LIM      (idx, 1)        = 0 ;

% File paths:

XS_DATA_FILE_PATH         (idx, [1: 55])  = '/home/andrei2/serpent/xsdata/jeff312/sss_jeff312.xsdata' ;
DECAY_DATA_FILE_PATH      (idx, [1: 51])  = '/home/andrei2/serpent/xsdata/jeff312/sss_jeff33.dec' ;
SFY_DATA_FILE_PATH        (idx, [1: 51])  = '/home/andrei2/serpent/xsdata/jeff312/sss_jeff33.nfy' ;
NFY_DATA_FILE_PATH        (idx, [1: 51])  = '/home/andrei2/serpent/xsdata/jeff312/sss_jeff33.nfy' ;
BRA_DATA_FILE_PATH        (idx, [1:  3])  = 'N/A' ;

% Collision and reaction sampling (neutrons/photons):

MIN_MACROXS               (idx, [1:   4]) = [  5.00000E-02 0.0E+00  0.00000E+00 0.0E+00 ];
DT_THRESH                 (idx, [1:  2])  = [  9.00000E-01  9.00000E-01 ];
ST_FRAC                   (idx, [1:   4]) = [  5.08233E-02 0.00035  0.00000E+00 0.0E+00 ];
DT_FRAC                   (idx, [1:   4]) = [  9.49177E-01 1.9E-05  0.00000E+00 0.0E+00 ];
DT_EFF                    (idx, [1:   4]) = [  3.47017E-01 6.7E-05  0.00000E+00 0.0E+00 ];
REA_SAMPLING_EFF          (idx, [1:   4]) = [  1.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
REA_SAMPLING_FAIL         (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
TOT_COL_EFF               (idx, [1:   4]) = [  3.60878E-01 6.5E-05  0.00000E+00 0.0E+00 ];
AVG_TRACKING_LOOPS        (idx, [1:   8]) = [  4.36162E+00 0.00021  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
AVG_TRACKS                (idx, [1:   4]) = [  3.73831E+01 0.00014  0.00000E+00 0.0E+00 ];
AVG_REAL_COL              (idx, [1:   4]) = [  3.73656E+01 0.00014  0.00000E+00 0.0E+00 ];
AVG_VIRT_COL              (idx, [1:   4]) = [  6.61756E+01 0.00020  0.00000E+00 0.0E+00 ];
AVG_SURF_CROSS            (idx, [1:   4]) = [  3.22662E+00 0.00040  0.00000E+00 0.0E+00 ];
LOST_PARTICLES            (idx, 1)        = 0 ;

% Run statistics:

CYCLE_IDX                 (idx, 1)        = 300 ;
SIMULATED_HISTORIES       (idx, 1)        = 15000506 ;
MEAN_POP_SIZE             (idx, [1:  2])  = [  5.00017E+04 0.00045 ];
MEAN_POP_WGT              (idx, [1:  2])  = [  5.00017E+04 0.00045 ];
SIMULATION_COMPLETED      (idx, 1)        = 1 ;

% Running times:

TOT_CPU_TIME              (idx, 1)        =  1.05254E+02 ;
RUNNING_TIME              (idx, 1)        =  2.98276E+01 ;
INIT_TIME                 (idx, [1:  2])  = [  5.73833E-01  5.73833E-01 ];
PROCESS_TIME              (idx, [1:  2])  = [  5.53333E-03  5.53333E-03 ];
TRANSPORT_CYCLE_TIME      (idx, [1:  3])  = [  2.92482E+01  2.92482E+01  0.00000E+00 ];
BURNUP_CYCLE_TIME         (idx, [1:  2])  = [  0.00000E+00  0.00000E+00 ];
BATEMAN_SOLUTION_TIME     (idx, [1:  2])  = [  0.00000E+00  0.00000E+00 ];
MPI_OVERHEAD_TIME         (idx, [1:  2])  = [  0.00000E+00  0.00000E+00 ];
ESTIMATED_RUNNING_TIME    (idx, [1:  2])  = [  2.98274E+01  0.00000E+00 ];
CPU_USAGE                 (idx, 1)        = 3.52874 ;
TRANSPORT_CPU_USAGE       (idx, [1:   2]) = [  3.55996E+00 0.00709 ];
OMP_PARALLEL_FRAC         (idx, 1)        =  9.72463E-01 ;

% Memory usage:

AVAIL_MEM                 (idx, 1)        = 32069.45 ;
ALLOC_MEMSIZE             (idx, 1)        = 10634.95;
MEMSIZE                   (idx, 1)        = 10552.84;
XS_MEMSIZE                (idx, 1)        = 10120.43;
MAT_MEMSIZE               (idx, 1)        = 97.07;
RES_MEMSIZE               (idx, 1)        = 1.03;
IFC_MEMSIZE               (idx, 1)        = 0.00;
MISC_MEMSIZE              (idx, 1)        = 334.32;
UNKNOWN_MEMSIZE           (idx, 1)        = 0.00;
UNUSED_MEMSIZE            (idx, 1)        = 82.11;

% Geometry parameters:

TOT_CELLS                 (idx, 1)        = 87 ;
UNION_CELLS               (idx, 1)        = 0 ;

% Neutron energy grid:

NEUTRON_ERG_TOL           (idx, 1)        =  5.00000E-05 ;
NEUTRON_ERG_NE            (idx, 1)        = 391538 ;
NEUTRON_EMIN              (idx, 1)        =  1.00000E-11 ;
NEUTRON_EMAX              (idx, 1)        =  2.00000E+01 ;

% Unresolved resonance probability table sampling:

URES_DILU_CUT             (idx, 1)        =  1.00000E-09 ;
URES_EMIN                 (idx, 1)        =  1.00000E+37 ;
URES_EMAX                 (idx, 1)        = -1.00000E+37 ;
URES_AVAIL                (idx, 1)        = 147 ;
URES_USED                 (idx, 1)        = 0 ;

% Nuclides and reaction channels:

TOT_NUCLIDES              (idx, 1)        = 1657 ;
TOT_TRANSPORT_NUCLIDES    (idx, 1)        = 314 ;
TOT_DOSIMETRY_NUCLIDES    (idx, 1)        = 0 ;
TOT_DECAY_NUCLIDES        (idx, 1)        = 1343 ;
TOT_PHOTON_NUCLIDES       (idx, 1)        = 0 ;
TOT_REA_CHANNELS          (idx, 1)        = 7315 ;
TOT_TRANSMU_REA           (idx, 1)        = 2520 ;

% Neutron physics options:

USE_DELNU                 (idx, 1)        = 1 ;
USE_URES                  (idx, 1)        = 0 ;
USE_DBRC                  (idx, 1)        = 0 ;
IMPL_CAPT                 (idx, 1)        = 0 ;
IMPL_NXN                  (idx, 1)        = 1 ;
IMPL_FISS                 (idx, 1)        = 0 ;
DOPPLER_PREPROCESSOR      (idx, 1)        = 1 ;
TMS_MODE                  (idx, 1)        = 0 ;
SAMPLE_FISS               (idx, 1)        = 1 ;
SAMPLE_CAPT               (idx, 1)        = 1 ;
SAMPLE_SCATT              (idx, 1)        = 1 ;

% Radioactivity data:

TOT_ACTIVITY              (idx, 1)        =  2.72130E+20 ;
TOT_DECAY_HEAT            (idx, 1)        =  8.28620E+07 ;
TOT_SF_RATE               (idx, 1)        =  4.56837E+05 ;
ACTINIDE_ACTIVITY         (idx, 1)        =  6.99688E+19 ;
ACTINIDE_DECAY_HEAT       (idx, 1)        =  4.90802E+06 ;
FISSION_PRODUCT_ACTIVITY  (idx, 1)        =  2.01183E+20 ;
FISSION_PRODUCT_DECAY_HEAT(idx, 1)        =  7.69711E+07 ;
INHALATION_TOXICITY       (idx, 1)        =  6.86278E+10 ;
INGESTION_TOXICITY        (idx, 1)        =  8.01072E+10 ;
ACTINIDE_INH_TOX          (idx, 1)        =  3.37684E+10 ;
ACTINIDE_ING_TOX          (idx, 1)        =  2.63578E+10 ;
FISSION_PRODUCT_INH_TOX   (idx, 1)        =  3.48594E+10 ;
FISSION_PRODUCT_ING_TOX   (idx, 1)        =  5.37494E+10 ;
SR90_ACTIVITY             (idx, 1)        =  8.34075E+14 ;
TE132_ACTIVITY            (idx, 1)        =  1.20917E+18 ;
I131_ACTIVITY             (idx, 1)        =  4.40613E+17 ;
I132_ACTIVITY             (idx, 1)        =  1.20584E+18 ;
CS134_ACTIVITY            (idx, 1)        =  9.45947E+11 ;
CS137_ACTIVITY            (idx, 1)        =  8.85063E+14 ;
PHOTON_DECAY_SOURCE       (idx, 1)        =  3.06514E+20 ;
NEUTRON_DECAY_SOURCE      (idx, 1)        =  4.91728E+17 ;
ALPHA_DECAY_SOURCE        (idx, 1)        =  1.42646E+17 ;
ELECTRON_DECAY_SOURCE     (idx, 1)        =  4.20750E+20 ;

% Normalization coefficient:

NORM_COEF                 (idx, [1:   4]) = [  1.88557E+15 0.00034  0.00000E+00 0.0E+00 ];

% Parameters for burnup calculation:

BURN_MATERIALS            (idx, 1)        = 2 ;
BURN_MODE                 (idx, 1)        = 2 ;
BURN_STEP                 (idx, 1)        = 0 ;
BURN_RANDOMIZE_DATA       (idx, [1:  2])  = [ 0 0 ];
BURNUP                    (idx, [1:  2])  = [  0.00000E+00  0.00000E+00 ];
BURN_DAYS                 (idx, [1:  2])  = [  0.00000E+00  0.00000E+00 ];

% Analog reaction rate estimators:

CONVERSION_RATIO          (idx, [1:   2]) = [  8.06117E-01 0.00054 ];
U235_FISS                 (idx, [1:   4]) = [  3.56834E+19 0.00037  9.26600E-01 0.00011 ];
U238_FISS                 (idx, [1:   4]) = [  2.70733E+18 0.00158  7.02985E-02 0.00144 ];
PU239_FISS                (idx, [1:   4]) = [  1.18036E+17 0.00801  3.06495E-03 0.00798 ];
PU240_FISS                (idx, [1:   4]) = [  1.26133E+13 0.70593  3.26466E-07 0.70593 ];
U235_CAPT                 (idx, [1:   4]) = [  1.16033E+19 0.00072  2.14013E-01 0.00063 ];
U238_CAPT                 (idx, [1:   4]) = [  3.82726E+19 0.00055  7.05889E-01 0.00021 ];
PU239_CAPT                (idx, [1:   4]) = [  7.20178E+16 0.00951  1.32829E-03 0.00949 ];
PU240_CAPT                (idx, [1:   4]) = [  1.75940E+15 0.05645  3.24401E-05 0.05643 ];
XE135_CAPT                (idx, [1:   4]) = [  5.28100E+17 0.00331  9.74054E-03 0.00332 ];
SM149_CAPT                (idx, [1:   4]) = [  2.58377E+16 0.01501  4.76553E-04 0.01501 ];

% Neutron balance (particles/weight):

BALA_SRC_NEUTRON_SRC     (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_SRC_NEUTRON_FISS    (idx, [1:  2])  = [ 15000506 1.50000E+07 ];
BALA_SRC_NEUTRON_NXN     (idx, [1:  2])  = [ 0 1.63712E+04 ];
BALA_SRC_NEUTRON_VR      (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_SRC_NEUTRON_TOT     (idx, [1:  2])  = [ 15000506 1.50164E+07 ];

BALA_LOSS_NEUTRON_CAPT    (idx, [1:  2])  = [ 8616923 8.62630E+06 ];
BALA_LOSS_NEUTRON_FISS    (idx, [1:  2])  = [ 6120939 6.12715E+06 ];
BALA_LOSS_NEUTRON_LEAK    (idx, [1:  2])  = [ 262644 2.62926E+05 ];
BALA_LOSS_NEUTRON_CUT     (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_LOSS_NEUTRON_ERR     (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_LOSS_NEUTRON_TOT     (idx, [1:  2])  = [ 15000506 1.50164E+07 ];

BALA_NEUTRON_DIFF         (idx, [1:  2])  = [ 0 4.73112E-07 ];

% Normalized total reaction rates (neutrons):

TOT_POWER                 (idx, [1:   6]) = [  1.25000E+09 0.0E+00  1.25000E+09 0.0E+00  0.00000E+00 0.0E+00 ];
TOT_POWDENS               (idx, [1:   6]) = [  1.78365E-02 0.0E+00  1.78365E-02 0.0E+00  0.00000E+00 0.0E+00 ];
TOT_GENRATE               (idx, [1:   6]) = [  9.49040E+19 6.1E-06  9.49040E+19 6.1E-06  0.00000E+00 0.0E+00 ];
TOT_FISSRATE              (idx, [1:   6]) = [  3.85182E+19 6.2E-07  3.85182E+19 6.2E-07  0.00000E+00 0.0E+00 ];
TOT_CAPTRATE              (idx, [1:   6]) = [  5.42229E+19 0.00029  5.18890E+19 0.00030  2.33394E+18 0.00062 ];
TOT_ABSRATE               (idx, [1:   6]) = [  9.27411E+19 0.00017  9.04071E+19 0.00017  2.33394E+18 0.00062 ];
TOT_SRCRATE               (idx, [1:   6]) = [  9.42785E+19 0.00034  9.42785E+19 0.00034  0.00000E+00 0.0E+00 ];
TOT_FLUX                  (idx, [1:   6]) = [  8.44503E+21 0.00029  7.46846E+21 0.00030  9.76570E+20 0.00031 ];
TOT_PHOTON_PRODRATE       (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
TOT_LEAKRATE              (idx, [1:   2]) = [  1.65256E+18 0.00254 ];
ALBEDO_LEAKRATE           (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
TOT_LOSSRATE              (idx, [1:   2]) = [  9.43936E+19 0.00017 ];
TOT_CUTRATE               (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
TOT_RR                    (idx, [1:   2]) = [  3.52644E+21 0.00028 ];
INI_FMASS                 (idx, 1)        =  7.00810E+04 ;
TOT_FMASS                 (idx, 1)        =  7.00810E+04 ;
INI_BURN_FMASS            (idx, 1)        =  7.00810E+04 ;
TOT_BURN_FMASS            (idx, 1)        =  7.00810E+04 ;

% Six-factor formula:

SIX_FF_ETA                (idx, [1:   2]) = [  1.82203E+00 0.00032 ];
SIX_FF_F                  (idx, [1:   2]) = [  9.70128E-01 9.2E-05 ];
SIX_FF_P                  (idx, [1:   2]) = [  2.27851E-01 0.00049 ];
SIX_FF_EPSILON            (idx, [1:   2]) = [  2.54368E+00 0.00049 ];
SIX_FF_LF                 (idx, [1:   2]) = [  9.82497E-01 4.5E-05 ];
SIX_FF_LT                 (idx, [1:   2]) = [  9.99974E-01 1.3E-06 ];
SIX_FF_KINF               (idx, [1:   2]) = [  1.02439E+00 0.00031 ];
SIX_FF_KEFF               (idx, [1:   2]) = [  1.00643E+00 0.00031 ];

% Fission neutron and energy production:

NUBAR                     (idx, [1:   2]) = [  2.46388E+00 6.6E-06 ];
FISSE                     (idx, [1:   2]) = [  2.02551E+02 6.2E-07 ];

% Criticality eigenvalues:

ANA_KEFF                  (idx, [1:   6]) = [  1.00647E+00 0.00032  9.99289E-01 0.00031  7.14314E-03 0.00478 ];
IMP_KEFF                  (idx, [1:   2]) = [  1.00651E+00 0.00017 ];
COL_KEFF                  (idx, [1:   2]) = [  1.00667E+00 0.00034 ];
ABS_KEFF                  (idx, [1:   2]) = [  1.00651E+00 0.00017 ];
ABS_KINF                  (idx, [1:   2]) = [  1.02447E+00 0.00017 ];
GEOM_ALBEDO               (idx, [1:   6]) = [  1.00000E+00 0.0E+00  1.00000E+00 0.0E+00  1.00000E+00 0.0E+00 ];

% ALF (Average lethargy of neutrons causing fission):
% Based on E0 = 2.000000E+01 MeV

ANA_ALF                   (idx, [1:   2]) = [  1.39930E+01 0.00016 ];
IMP_ALF                   (idx, [1:   2]) = [  1.39936E+01 0.00010 ];

% EALF (Energy corresponding to average lethargy of neutrons causing fission):

ANA_EALF                  (idx, [1:   2]) = [  1.67586E-05 0.00217 ];
IMP_EALF                  (idx, [1:   2]) = [  1.67422E-05 0.00147 ];

% AFGE (Average energy of neutrons causing fission):

ANA_AFGE                  (idx, [1:   2]) = [  2.39692E-01 0.00149 ];
IMP_AFGE                  (idx, [1:   2]) = [  2.39829E-01 0.00056 ];

% Forward-weighted delayed neutron parameters:

PRECURSOR_GROUPS          (idx, 1)        = 8 ;
FWD_ANA_BETA_ZERO         (idx, [1:  18]) = [  7.39770E-03 0.00324  2.17048E-04 0.01744  1.05221E-03 0.00807  6.38056E-04 0.00979  1.39092E-03 0.00680  2.34135E-03 0.00544  8.13505E-04 0.00916  6.80349E-04 0.00967  2.64266E-04 0.01540 ];
FWD_ANA_LAMBDA            (idx, [1:  18]) = [  4.76145E-01 0.00439  1.24667E-02 0.0E+00  2.82917E-02 4.9E-09  4.25244E-02 7.1E-09  1.33042E-01 0.0E+00  2.92467E-01 0.0E+00  6.66488E-01 0.0E+00  1.63478E+00 5.2E-09  3.55460E+00 0.0E+00 ];

% Beta-eff using Meulekamp's method:

ADJ_MEULEKAMP_BETA_EFF    (idx, [1:  18]) = [  7.22624E-03 0.00507  2.21324E-04 0.02768  1.02751E-03 0.01307  6.37107E-04 0.01638  1.33488E-03 0.01188  2.28287E-03 0.00832  8.03912E-04 0.01445  6.59392E-04 0.01632  2.59242E-04 0.02778 ];
ADJ_MEULEKAMP_LAMBDA      (idx, [1:  18]) = [  4.75762E-01 0.00788  1.24667E-02 0.0E+00  2.82917E-02 4.7E-09  4.25244E-02 6.9E-09  1.33042E-01 0.0E+00  2.92467E-01 0.0E+00  6.66488E-01 0.0E+00  1.63478E+00 5.2E-09  3.55460E+00 0.0E+00 ];

% Adjoint weighted time constants using Nauchi's method:

IFP_CHAIN_LENGTH          (idx, 1)        = 15 ;
ADJ_NAUCHI_GEN_TIME       (idx, [1:   6]) = [  1.49421E-05 0.00074  1.49307E-05 0.00074  1.65627E-05 0.00750 ];
ADJ_NAUCHI_LIFETIME       (idx, [1:   6]) = [  1.50384E-05 0.00067  1.50269E-05 0.00067  1.66683E-05 0.00746 ];
ADJ_NAUCHI_BETA_EFF       (idx, [1:  18]) = [  7.08863E-03 0.00485  2.06406E-04 0.03056  1.00709E-03 0.01362  6.20521E-04 0.01624  1.31960E-03 0.01198  2.25507E-03 0.00837  7.79808E-04 0.01445  6.49739E-04 0.01625  2.50401E-04 0.02527 ];
ADJ_NAUCHI_LAMBDA         (idx, [1:  18]) = [  4.74626E-01 0.00768  1.24667E-02 0.0E+00  2.82917E-02 4.9E-09  4.25244E-02 7.2E-09  1.33042E-01 0.0E+00  2.92467E-01 0.0E+00  6.66488E-01 0.0E+00  1.63478E+00 5.2E-09  3.55460E+00 0.0E+00 ];

% Adjoint weighted time constants using IFP:

ADJ_IFP_GEN_TIME          (idx, [1:   6]) = [  1.50739E-05 0.00191  1.50629E-05 0.00193  1.66468E-05 0.01922 ];
ADJ_IFP_LIFETIME          (idx, [1:   6]) = [  1.51710E-05 0.00189  1.51599E-05 0.00191  1.67561E-05 0.01926 ];
ADJ_IFP_IMP_BETA_EFF      (idx, [1:  18]) = [  7.04498E-03 0.01723  1.93141E-04 0.09002  9.82128E-04 0.04340  6.07321E-04 0.05647  1.33665E-03 0.03534  2.23402E-03 0.02976  8.08278E-04 0.05073  6.21809E-04 0.05470  2.61634E-04 0.08377 ];
ADJ_IFP_IMP_LAMBDA        (idx, [1:  18]) = [  4.79302E-01 0.02550  1.24667E-02 0.0E+00  2.82917E-02 5.7E-09  4.25244E-02 7.6E-09  1.33042E-01 0.0E+00  2.92467E-01 0.0E+00  6.66488E-01 0.0E+00  1.63478E+00 5.4E-09  3.55460E+00 0.0E+00 ];
ADJ_IFP_ANA_BETA_EFF      (idx, [1:  18]) = [  7.08399E-03 0.01639  1.97067E-04 0.08816  9.82119E-04 0.04281  6.09951E-04 0.05508  1.34202E-03 0.03445  2.24592E-03 0.02870  8.18407E-04 0.04873  6.27689E-04 0.05203  2.60818E-04 0.07863 ];
ADJ_IFP_ANA_LAMBDA        (idx, [1:  18]) = [  4.81772E-01 0.02429  1.24667E-02 0.0E+00  2.82917E-02 5.6E-09  4.25244E-02 7.8E-09  1.33042E-01 0.0E+00  2.92467E-01 0.0E+00  6.66488E-01 0.0E+00  1.63478E+00 5.5E-09  3.55460E+00 0.0E+00 ];
ADJ_IFP_ROSSI_ALPHA       (idx, [1:   2]) = [ -4.68261E+02 0.01740 ];

% Adjoint weighted time constants using perturbation technique:

ADJ_PERT_GEN_TIME         (idx, [1:   2]) = [  1.50263E-05 0.00049 ];
ADJ_PERT_LIFETIME         (idx, [1:   2]) = [  1.51231E-05 0.00037 ];
ADJ_PERT_BETA_EFF         (idx, [1:   2]) = [  7.11488E-03 0.00306 ];
ADJ_PERT_ROSSI_ALPHA      (idx, [1:   2]) = [ -4.73542E+02 0.00313 ];

% Inverse neutron speed :

ANA_INV_SPD               (idx, [1:   2]) = [  1.02086E-07 0.00043 ];

% Analog slowing-down and thermal neutron lifetime (total/prompt/delayed):

ANA_SLOW_TIME             (idx, [1:   6]) = [  9.37009E-06 0.00062  9.37049E-06 0.00062  9.30590E-06 0.00665 ];
ANA_THERM_TIME            (idx, [1:   6]) = [  2.20442E-05 0.00047  2.20424E-05 0.00046  2.22878E-05 0.00546 ];
ANA_THERM_FRAC            (idx, [1:   6]) = [  2.27007E-01 0.00048  2.26904E-01 0.00048  2.41544E-01 0.00677 ];
ANA_DELAYED_EMTIME        (idx, [1:   2]) = [  1.21506E+01 0.00676 ];
ANA_MEAN_NCOL             (idx, [1:   4]) = [  3.73656E+01 0.00014  3.94767E+01 0.00022 ];

% Group constant generation:

GC_UNIVERSE_NAME          (idx, [1:  1])  = '0' ;

% Micro- and macro-group structures:

MICRO_NG                  (idx, 1)        = 70 ;
MICRO_E                   (idx, [1:  71]) = [  1.00000E-11  5.00000E-09  1.00000E-08  1.50000E-08  2.00000E-08  2.50000E-08  3.00000E-08  3.50000E-08  4.20000E-08  5.00000E-08  5.80000E-08  6.70000E-08  8.00000E-08  1.00000E-07  1.40000E-07  1.80000E-07  2.20000E-07  2.50000E-07  2.80000E-07  3.00000E-07  3.20000E-07  3.50000E-07  4.00000E-07  5.00000E-07  6.25000E-07  7.80000E-07  8.50000E-07  9.10000E-07  9.50000E-07  9.72000E-07  9.96000E-07  1.02000E-06  1.04500E-06  1.07100E-06  1.09700E-06  1.12300E-06  1.15000E-06  1.30000E-06  1.50000E-06  1.85500E-06  2.10000E-06  2.60000E-06  3.30000E-06  4.00000E-06  9.87700E-06  1.59680E-05  2.77000E-05  4.80520E-05  7.55014E-05  1.48728E-04  3.67262E-04  9.06898E-04  1.42510E-03  2.23945E-03  3.51910E-03  5.50000E-03  9.11800E-03  1.50300E-02  2.47800E-02  4.08500E-02  6.74300E-02  1.11000E-01  1.83000E-01  3.02500E-01  5.00000E-01  8.21000E-01  1.35300E+00  2.23100E+00  3.67900E+00  6.06550E+00  2.00000E+01 ];

MACRO_NG                  (idx, 1)        = 2 ;
MACRO_E                   (idx, [1:   3]) = [  1.00000E+37  6.25000E-07  0.00000E+00 ];

% Micro-group spectrum:

INF_MICRO_FLX             (idx, [1: 140]) = [  2.59676E+05 0.00181  1.19905E+06 0.00063  2.80004E+06 0.00055  4.20392E+06 0.00042  5.12288E+06 0.00032  6.32140E+06 0.00044  3.47059E+06 0.00030  3.00529E+06 0.00039  5.72324E+06 0.00045  5.17557E+06 0.00035  5.48209E+06 0.00021  4.67136E+06 0.00047  4.68603E+06 0.00044  3.76584E+06 0.00054  3.26959E+06 0.00053  2.59527E+06 0.00063  2.40345E+06 0.00034  2.25594E+06 0.00071  2.08312E+06 0.00063  3.66728E+06 0.00049  3.08642E+06 0.00049  1.91254E+06 0.00077  1.07694E+06 0.00071  1.05752E+06 0.00105  8.54965E+05 0.00079  8.06728E+05 0.00089  1.08561E+06 0.00072  3.34604E+05 0.00134  5.29035E+05 0.00099  5.52919E+05 0.00149  3.27724E+05 0.00132  5.98589E+05 0.00103  4.09067E+05 0.00139  3.19474E+05 0.00137  5.55838E+04 0.00211  5.42115E+04 0.00326  5.57336E+04 0.00128  5.75119E+04 0.00209  5.73154E+04 0.00257  5.65795E+04 0.00251  5.79806E+04 0.00267  5.44101E+04 0.00274  1.02185E+05 0.00170  1.62444E+05 0.00190  2.02132E+05 0.00146  5.11505E+05 0.00136  4.84789E+05 0.00098  4.37826E+05 0.00144  2.32672E+05 0.00174  1.40578E+05 0.00144  9.40508E+04 0.00158  9.87902E+04 0.00165  1.57163E+05 0.00113  1.73610E+05 0.00115  2.52415E+05 0.00091  2.70856E+05 0.00117  2.77427E+05 0.00153  1.30385E+05 0.00156  7.68477E+04 0.00140  4.77441E+04 0.00227  3.80042E+04 0.00208  3.45186E+04 0.00264  2.54104E+04 0.00268  1.64677E+04 0.00399  1.34137E+04 0.00289  1.11838E+04 0.00341  8.87857E+03 0.00251  6.57748E+03 0.00420  3.82458E+03 0.00482  1.30224E+03 0.00786 ];

% Integral parameters:

INF_KINF                  (idx, [1:   2]) = [  1.02463E+00 0.00026 ];

% Flux spectra in infinite geometry:

INF_FLX                   (idx, [1:   4]) = [  8.15899E+21 0.00032  2.86110E+20 0.00044 ];
INF_FISS_FLX              (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Reaction cross sections:

INF_TOT                   (idx, [1:   4]) = [  4.14135E-01 3.9E-05  5.15701E-01 0.00022 ];
INF_CAPT                  (idx, [1:   4]) = [  5.93341E-03 0.00019  2.03174E-02 0.00027 ];
INF_ABS                   (idx, [1:   4]) = [  8.77967E-03 0.00014  7.37827E-02 0.00026 ];
INF_FISS                  (idx, [1:   4]) = [  2.84626E-03 0.00015  5.34653E-02 0.00026 ];
INF_NSF                   (idx, [1:   4]) = [  7.05999E-03 0.00014  1.30386E-01 0.00026 ];
INF_NUBAR                 (idx, [1:   4]) = [  2.48045E+00 7.1E-06  2.43871E+00 5.1E-07 ];
INF_KAPPA                 (idx, [1:   4]) = [  2.02713E+02 7.9E-07  2.02304E+02 8.4E-08 ];
INF_INVV                  (idx, [1:   4]) = [  4.89184E-08 0.00048  1.61827E-06 0.00023 ];

% Total scattering cross sections:

INF_SCATT0                (idx, [1:   4]) = [  4.05356E-01 3.9E-05  4.41936E-01 0.00023 ];
INF_SCATT1                (idx, [1:   4]) = [  7.39931E-02 0.00027  6.97219E-02 0.00056 ];
INF_SCATT2                (idx, [1:   4]) = [  2.72715E-02 0.00045  1.87414E-02 0.00225 ];
INF_SCATT3                (idx, [1:   4]) = [  3.18591E-03 0.00203  5.74468E-03 0.00722 ];
INF_SCATT4                (idx, [1:   4]) = [ -1.41599E-03 0.00624  1.54236E-04 0.20017 ];
INF_SCATT5                (idx, [1:   4]) = [  3.63332E-04 0.01289  7.69336E-04 0.03978 ];
INF_SCATT6                (idx, [1:   4]) = [  1.30353E-03 0.00281 -1.11327E-03 0.02043 ];
INF_SCATT7                (idx, [1:   4]) = [  2.19332E-04 0.02504  2.00406E-04 0.14537 ];

% Total scattering production cross sections:

INF_SCATTP0               (idx, [1:   4]) = [  4.05369E-01 3.9E-05  4.41936E-01 0.00023 ];
INF_SCATTP1               (idx, [1:   4]) = [  7.39933E-02 0.00027  6.97219E-02 0.00056 ];
INF_SCATTP2               (idx, [1:   4]) = [  2.72716E-02 0.00045  1.87414E-02 0.00225 ];
INF_SCATTP3               (idx, [1:   4]) = [  3.18591E-03 0.00203  5.74468E-03 0.00722 ];
INF_SCATTP4               (idx, [1:   4]) = [ -1.41598E-03 0.00624  1.54236E-04 0.20017 ];
INF_SCATTP5               (idx, [1:   4]) = [  3.63348E-04 0.01293  7.69336E-04 0.03978 ];
INF_SCATTP6               (idx, [1:   4]) = [  1.30353E-03 0.00281 -1.11327E-03 0.02043 ];
INF_SCATTP7               (idx, [1:   4]) = [  2.19338E-04 0.02503  2.00406E-04 0.14537 ];

% Diffusion parameters:

INF_TRANSPXS              (idx, [1:   4]) = [  3.16292E-01 6.9E-05  4.20597E-01 0.00021 ];
INF_DIFFCOEF              (idx, [1:   4]) = [  1.05388E+00 6.9E-05  7.92524E-01 0.00021 ];

% Reduced absoption and removal:

INF_RABSXS                (idx, [1:   4]) = [  8.76705E-03 0.00014  7.37827E-02 0.00026 ];
INF_REMXS                 (idx, [1:   4]) = [  1.15828E-02 0.00021  7.99607E-02 0.00036 ];

% Poison cross sections:

INF_I135_YIELD            (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_XE135_YIELD           (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_PM147_YIELD           (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_PM148_YIELD           (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_PM148M_YIELD          (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_PM149_YIELD           (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_SM149_YIELD           (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_I135_MICRO_ABS        (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_XE135_MICRO_ABS       (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_PM147_MICRO_ABS       (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_PM148_MICRO_ABS       (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_PM148M_MICRO_ABS      (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_PM149_MICRO_ABS       (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_SM149_MICRO_ABS       (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_XE135_MACRO_ABS       (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_SM149_MACRO_ABS       (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Fission spectra:

INF_CHIT                  (idx, [1:   4]) = [  1.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_CHIP                  (idx, [1:   4]) = [  1.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_CHID                  (idx, [1:   4]) = [  1.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Scattering matrixes:

INF_S0                    (idx, [1:   8]) = [  4.02552E-01 3.8E-05  2.80427E-03 0.00055  6.19598E-03 0.00194  4.35740E-01 0.00023 ];
INF_S1                    (idx, [1:   8]) = [  7.34827E-02 0.00027  5.10343E-04 0.00158  3.32156E-04 0.01726  6.93897E-02 0.00056 ];
INF_S2                    (idx, [1:   8]) = [  2.74754E-02 0.00044 -2.03908E-04 0.00239 -9.64576E-06 0.60975  1.87511E-02 0.00220 ];
INF_S3                    (idx, [1:   8]) = [  3.42172E-03 0.00195 -2.35817E-04 0.00245 -1.30365E-04 0.03562  5.87505E-03 0.00724 ];
INF_S4                    (idx, [1:   8]) = [ -1.32350E-03 0.00657 -9.24972E-05 0.00449 -1.53815E-04 0.02304  3.08051E-04 0.09880 ];
INF_S5                    (idx, [1:   8]) = [  3.76525E-04 0.01244 -1.31931E-05 0.02096 -1.34934E-04 0.02148  9.04269E-04 0.03263 ];
INF_S6                    (idx, [1:   8]) = [  1.31975E-03 0.00272 -1.62250E-05 0.02045 -8.66080E-05 0.02897 -1.02667E-03 0.02192 ];
INF_S7                    (idx, [1:   8]) = [  2.32573E-04 0.02408 -1.32405E-05 0.02693 -4.86307E-05 0.05706  2.49037E-04 0.11109 ];

% Scattering production matrixes:

INF_SP0                   (idx, [1:   8]) = [  4.02564E-01 3.8E-05  2.80427E-03 0.00055  6.19598E-03 0.00194  4.35740E-01 0.00023 ];
INF_SP1                   (idx, [1:   8]) = [  7.34829E-02 0.00027  5.10343E-04 0.00158  3.32156E-04 0.01726  6.93897E-02 0.00056 ];
INF_SP2                   (idx, [1:   8]) = [  2.74756E-02 0.00044 -2.03908E-04 0.00239 -9.64576E-06 0.60975  1.87511E-02 0.00220 ];
INF_SP3                   (idx, [1:   8]) = [  3.42173E-03 0.00194 -2.35817E-04 0.00245 -1.30365E-04 0.03562  5.87505E-03 0.00724 ];
INF_SP4                   (idx, [1:   8]) = [ -1.32348E-03 0.00658 -9.24972E-05 0.00449 -1.53815E-04 0.02304  3.08051E-04 0.09880 ];
INF_SP5                   (idx, [1:   8]) = [  3.76541E-04 0.01247 -1.31931E-05 0.02096 -1.34934E-04 0.02148  9.04269E-04 0.03263 ];
INF_SP6                   (idx, [1:   8]) = [  1.31975E-03 0.00271 -1.62250E-05 0.02045 -8.66080E-05 0.02897 -1.02667E-03 0.02192 ];
INF_SP7                   (idx, [1:   8]) = [  2.32578E-04 0.02408 -1.32405E-05 0.02693 -4.86307E-05 0.05706  2.49037E-04 0.11109 ];

% Micro-group spectrum:

B1_MICRO_FLX              (idx, [1: 140]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Integral parameters:

B1_KINF                   (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
B1_KEFF                   (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
B1_B2                     (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
B1_ERR                    (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];

% Critical spectra in infinite geometry:

B1_FLX                    (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_FISS_FLX               (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Reaction cross sections:

B1_TOT                    (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_CAPT                   (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_ABS                    (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_FISS                   (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_NSF                    (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_NUBAR                  (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_KAPPA                  (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_INVV                   (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Total scattering cross sections:

B1_SCATT0                 (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATT1                 (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATT2                 (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATT3                 (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATT4                 (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATT5                 (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATT6                 (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATT7                 (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Total scattering production cross sections:

B1_SCATTP0                (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATTP1                (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATTP2                (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATTP3                (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATTP4                (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATTP5                (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATTP6                (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATTP7                (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Diffusion parameters:

B1_TRANSPXS               (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_DIFFCOEF               (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Reduced absoption and removal:

B1_RABSXS                 (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_REMXS                  (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Poison cross sections:

B1_I135_YIELD             (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_XE135_YIELD            (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_PM147_YIELD            (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_PM148_YIELD            (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_PM148M_YIELD           (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_PM149_YIELD            (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SM149_YIELD            (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_I135_MICRO_ABS         (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_XE135_MICRO_ABS        (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_PM147_MICRO_ABS        (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_PM148_MICRO_ABS        (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_PM148M_MICRO_ABS       (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_PM149_MICRO_ABS        (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SM149_MICRO_ABS        (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_XE135_MACRO_ABS        (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SM149_MACRO_ABS        (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Fission spectra:

B1_CHIT                   (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_CHIP                   (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_CHID                   (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Scattering matrixes:

B1_S0                     (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_S1                     (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_S2                     (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_S3                     (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_S4                     (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_S5                     (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_S6                     (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_S7                     (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Scattering production matrixes:

B1_SP0                    (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SP1                    (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SP2                    (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SP3                    (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SP4                    (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SP5                    (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SP6                    (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SP7                    (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Additional diffusion parameters:

CMM_TRANSPXS              (idx, [1:   4]) = [  3.05573E-01 0.00024  3.85000E-01 0.00175 ];
CMM_TRANSPXS_X            (idx, [1:   4]) = [  3.07373E-01 0.00033  3.79378E-01 0.00395 ];
CMM_TRANSPXS_Y            (idx, [1:   4]) = [  3.07400E-01 0.00053  3.79457E-01 0.00449 ];
CMM_TRANSPXS_Z            (idx, [1:   4]) = [  3.02012E-01 0.00044  3.96889E-01 0.00336 ];
CMM_DIFFCOEF              (idx, [1:   4]) = [  1.09085E+00 0.00024  8.65838E-01 0.00174 ];
CMM_DIFFCOEF_X            (idx, [1:   4]) = [  1.08446E+00 0.00033  8.78821E-01 0.00393 ];
CMM_DIFFCOEF_Y            (idx, [1:   4]) = [  1.08437E+00 0.00053  8.78694E-01 0.00443 ];
CMM_DIFFCOEF_Z            (idx, [1:   4]) = [  1.10371E+00 0.00044  8.40000E-01 0.00338 ];

% Delayed neutron parameters (Meulekamp method):

BETA_EFF                  (idx, [1:  18]) = [  7.22624E-03 0.00507  2.21324E-04 0.02768  1.02751E-03 0.01307  6.37107E-04 0.01638  1.33488E-03 0.01188  2.28287E-03 0.00832  8.03912E-04 0.01445  6.59392E-04 0.01632  2.59242E-04 0.02778 ];
LAMBDA                    (idx, [1:  18]) = [  4.75762E-01 0.00788  1.24667E-02 0.0E+00  2.82917E-02 4.7E-09  4.25244E-02 6.9E-09  1.33042E-01 0.0E+00  2.92467E-01 0.0E+00  6.66488E-01 0.0E+00  1.63478E+00 5.2E-09  3.55460E+00 0.0E+00 ];


% Increase counter:

if (exist('idx', 'var'));
  idx = idx + 1;
else;
  idx = 1;
end;

% Version, title and date:

VERSION                   (idx, [1: 14])  = 'Serpent 2.1.31' ;
COMPILE_DATE              (idx, [1: 20])  = 'May 16 2019 12:25:40' ;
DEBUG                     (idx, 1)        = 0 ;
TITLE                     (idx, [1:  8])  = 'Untitled' ;
CONFIDENTIAL_DATA         (idx, 1)        = 0 ;
INPUT_FILE_NAME           (idx, [1: 69])  = '/home/andrei2/Desktop/git/saltproc/develop/saltproc/data/saltproc_tap' ;
WORKING_DIRECTORY         (idx, [1: 51])  = '/home/andrei2/Desktop/git/saltproc/develop/saltproc' ;
HOSTNAME                  (idx, [1: 28])  = 'andrei2-Precision-Tower-3420' ;
CPU_TYPE                  (idx, [1: 41])  = 'Intel(R) Xeon(R) CPU E3-1225 v5 @ 3.30GHz' ;
CPU_MHZ                   (idx, 1)        = 186.0 ;
START_DATE                (idx, [1: 24])  = 'Tue May 28 19:35:49 2019' ;
COMPLETE_DATE             (idx, [1: 24])  = 'Tue May 28 20:57:45 2019' ;

% Run parameters:

POP                       (idx, 1)        = 50000 ;
CYCLES                    (idx, 1)        = 300 ;
SKIP                      (idx, 1)        = 120 ;
BATCH_INTERVAL            (idx, 1)        = 1 ;
SRC_NORM_MODE             (idx, 1)        = 2 ;
SEED                      (idx, 1)        = 1559090149611 ;
UFS_MODE                  (idx, 1)        = 0 ;
UFS_ORDER                 (idx, 1)        = 1.00000;
NEUTRON_TRANSPORT_MODE    (idx, 1)        = 1 ;
PHOTON_TRANSPORT_MODE     (idx, 1)        = 0 ;
GROUP_CONSTANT_GENERATION (idx, 1)        = 1 ;
B1_CALCULATION            (idx, [1:  3])  = [ 0 0 0 ];
B1_BURNUP_CORRECTION      (idx, 1)        = 0 ;

CRIT_SPEC_MODE            (idx, 1)        = 0 ;
IMPLICIT_REACTION_RATES   (idx, 1)        = 1 ;

% Optimization:

OPTIMIZATION_MODE         (idx, 1)        = 4 ;
RECONSTRUCT_MICROXS       (idx, 1)        = 1 ;
RECONSTRUCT_MACROXS       (idx, 1)        = 1 ;
DOUBLE_INDEXING           (idx, 1)        = 0 ;
MG_MAJORANT_MODE          (idx, 1)        = 0 ;
SPECTRUM_COLLAPSE         (idx, 1)        = 1 ;

% Parallelization:

MPI_TASKS                 (idx, 1)        = 1 ;
OMP_THREADS               (idx, 1)        = 4 ;
MPI_REPRODUCIBILITY       (idx, 1)        = 0 ;
OMP_REPRODUCIBILITY       (idx, 1)        = 1 ;
OMP_HISTORY_PROFILE       (idx, [1:   4]) = [  9.97434E-01  1.00021E+00  1.00222E+00  1.00014E+00  ];
SHARE_BUF_ARRAY           (idx, 1)        = 0 ;
SHARE_RES2_ARRAY          (idx, 1)        = 1 ;
OMP_SHARED_QUEUE_LIM      (idx, 1)        = 0 ;

% File paths:

XS_DATA_FILE_PATH         (idx, [1: 55])  = '/home/andrei2/serpent/xsdata/jeff312/sss_jeff312.xsdata' ;
DECAY_DATA_FILE_PATH      (idx, [1: 51])  = '/home/andrei2/serpent/xsdata/jeff312/sss_jeff33.dec' ;
SFY_DATA_FILE_PATH        (idx, [1: 51])  = '/home/andrei2/serpent/xsdata/jeff312/sss_jeff33.nfy' ;
NFY_DATA_FILE_PATH        (idx, [1: 51])  = '/home/andrei2/serpent/xsdata/jeff312/sss_jeff33.nfy' ;
BRA_DATA_FILE_PATH        (idx, [1:  3])  = 'N/A' ;

% Collision and reaction sampling (neutrons/photons):

MIN_MACROXS               (idx, [1:   4]) = [  5.00000E-02 0.0E+00  0.00000E+00 0.0E+00 ];
DT_THRESH                 (idx, [1:  2])  = [  9.00000E-01  9.00000E-01 ];
ST_FRAC                   (idx, [1:   4]) = [  5.07269E-02 0.00035  0.00000E+00 0.0E+00 ];
DT_FRAC                   (idx, [1:   4]) = [  9.49273E-01 1.9E-05  0.00000E+00 0.0E+00 ];
DT_EFF                    (idx, [1:   4]) = [  3.46988E-01 6.8E-05  0.00000E+00 0.0E+00 ];
REA_SAMPLING_EFF          (idx, [1:   4]) = [  1.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
REA_SAMPLING_FAIL         (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
TOT_COL_EFF               (idx, [1:   4]) = [  3.60821E-01 6.7E-05  0.00000E+00 0.0E+00 ];
AVG_TRACKING_LOOPS        (idx, [1:   8]) = [  4.36593E+00 0.00020  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
AVG_TRACKS                (idx, [1:   4]) = [  3.73801E+01 0.00013  0.00000E+00 0.0E+00 ];
AVG_REAL_COL              (idx, [1:   4]) = [  3.73626E+01 0.00013  0.00000E+00 0.0E+00 ];
AVG_VIRT_COL              (idx, [1:   4]) = [  6.61863E+01 0.00019  0.00000E+00 0.0E+00 ];
AVG_SURF_CROSS            (idx, [1:   4]) = [  3.22082E+00 0.00040  0.00000E+00 0.0E+00 ];
LOST_PARTICLES            (idx, 1)        = 0 ;

% Run statistics:

CYCLE_IDX                 (idx, 1)        = 300 ;
SIMULATED_HISTORIES       (idx, 1)        = 15000439 ;
MEAN_POP_SIZE             (idx, [1:  2])  = [  5.00015E+04 0.00045 ];
MEAN_POP_WGT              (idx, [1:  2])  = [  5.00015E+04 0.00045 ];
SIMULATION_COMPLETED      (idx, 1)        = 1 ;

% Running times:

TOT_CPU_TIME              (idx, 1)        =  3.08023E+02 ;
RUNNING_TIME              (idx, 1)        =  8.19330E+01 ;
INIT_TIME                 (idx, [1:  2])  = [  5.73833E-01  5.73833E-01 ];
PROCESS_TIME              (idx, [1:  2])  = [  1.63833E-02  5.38333E-03 ];
TRANSPORT_CYCLE_TIME      (idx, [1:  3])  = [  8.13089E+01  2.67942E+01  2.52664E+01 ];
BURNUP_CYCLE_TIME         (idx, [1:  2])  = [  3.39167E-02  1.63167E-02 ];
BATEMAN_SOLUTION_TIME     (idx, [1:  2])  = [  1.66666E-03  7.99998E-04 ];
MPI_OVERHEAD_TIME         (idx, [1:  2])  = [  0.00000E+00  0.00000E+00 ];
ESTIMATED_RUNNING_TIME    (idx, [1:  2])  = [  8.19329E+01  8.19329E+01 ];
CPU_USAGE                 (idx, 1)        = 3.75945 ;
TRANSPORT_CPU_USAGE       (idx, [1:   2]) = [  3.89332E+00 0.00040 ];
OMP_PARALLEL_FRAC         (idx, 1)        =  9.85433E-01 ;

% Memory usage:

AVAIL_MEM                 (idx, 1)        = 32069.45 ;
ALLOC_MEMSIZE             (idx, 1)        = 10634.95;
MEMSIZE                   (idx, 1)        = 10552.84;
XS_MEMSIZE                (idx, 1)        = 10120.43;
MAT_MEMSIZE               (idx, 1)        = 97.07;
RES_MEMSIZE               (idx, 1)        = 1.03;
IFC_MEMSIZE               (idx, 1)        = 0.00;
MISC_MEMSIZE              (idx, 1)        = 334.32;
UNKNOWN_MEMSIZE           (idx, 1)        = 0.00;
UNUSED_MEMSIZE            (idx, 1)        = 82.11;

% Geometry parameters:

TOT_CELLS                 (idx, 1)        = 87 ;
UNION_CELLS               (idx, 1)        = 0 ;

% Neutron energy grid:

NEUTRON_ERG_TOL           (idx, 1)        =  5.00000E-05 ;
NEUTRON_ERG_NE            (idx, 1)        = 391538 ;
NEUTRON_EMIN              (idx, 1)        =  1.00000E-11 ;
NEUTRON_EMAX              (idx, 1)        =  2.00000E+01 ;

% Unresolved resonance probability table sampling:

URES_DILU_CUT             (idx, 1)        =  1.00000E-09 ;
URES_EMIN                 (idx, 1)        =  1.00000E+37 ;
URES_EMAX                 (idx, 1)        = -1.00000E+37 ;
URES_AVAIL                (idx, 1)        = 147 ;
URES_USED                 (idx, 1)        = 0 ;

% Nuclides and reaction channels:

TOT_NUCLIDES              (idx, 1)        = 1657 ;
TOT_TRANSPORT_NUCLIDES    (idx, 1)        = 314 ;
TOT_DOSIMETRY_NUCLIDES    (idx, 1)        = 0 ;
TOT_DECAY_NUCLIDES        (idx, 1)        = 1343 ;
TOT_PHOTON_NUCLIDES       (idx, 1)        = 0 ;
TOT_REA_CHANNELS          (idx, 1)        = 7315 ;
TOT_TRANSMU_REA           (idx, 1)        = 2520 ;

% Neutron physics options:

USE_DELNU                 (idx, 1)        = 1 ;
USE_URES                  (idx, 1)        = 0 ;
USE_DBRC                  (idx, 1)        = 0 ;
IMPL_CAPT                 (idx, 1)        = 0 ;
IMPL_NXN                  (idx, 1)        = 1 ;
IMPL_FISS                 (idx, 1)        = 0 ;
DOPPLER_PREPROCESSOR      (idx, 1)        = 1 ;
TMS_MODE                  (idx, 1)        = 0 ;
SAMPLE_FISS               (idx, 1)        = 1 ;
SAMPLE_CAPT               (idx, 1)        = 1 ;
SAMPLE_SCATT              (idx, 1)        = 1 ;

% Radioactivity data:

TOT_ACTIVITY              (idx, 1)        =  2.79507E+20 ;
TOT_DECAY_HEAT            (idx, 1)        =  8.36258E+07 ;
TOT_SF_RATE               (idx, 1)        =  4.63486E+05 ;
ACTINIDE_ACTIVITY         (idx, 1)        =  7.38850E+19 ;
ACTINIDE_DECAY_HEAT       (idx, 1)        =  5.16692E+06 ;
FISSION_PRODUCT_ACTIVITY  (idx, 1)        =  2.04642E+20 ;
FISSION_PRODUCT_DECAY_HEAT(idx, 1)        =  7.74748E+07 ;
INHALATION_TOXICITY       (idx, 1)        =  8.15759E+10 ;
INGESTION_TOXICITY        (idx, 1)        =  9.04440E+10 ;
ACTINIDE_INH_TOX          (idx, 1)        =  3.86607E+10 ;
ACTINIDE_ING_TOX          (idx, 1)        =  2.94867E+10 ;
FISSION_PRODUCT_INH_TOX   (idx, 1)        =  4.29151E+10 ;
FISSION_PRODUCT_ING_TOX   (idx, 1)        =  6.09573E+10 ;
SR90_ACTIVITY             (idx, 1)        =  1.25030E+15 ;
TE132_ACTIVITY            (idx, 1)        =  1.42847E+18 ;
I131_ACTIVITY             (idx, 1)        =  6.00727E+17 ;
I132_ACTIVITY             (idx, 1)        =  1.43207E+18 ;
CS134_ACTIVITY            (idx, 1)        =  3.43470E+12 ;
CS137_ACTIVITY            (idx, 1)        =  1.32786E+15 ;
PHOTON_DECAY_SOURCE       (idx, 1)        =  3.17393E+20 ;
NEUTRON_DECAY_SOURCE      (idx, 1)        =  4.91163E+17 ;
ALPHA_DECAY_SOURCE        (idx, 1)        =  1.42431E+17 ;
ELECTRON_DECAY_SOURCE     (idx, 1)        =  4.39910E+20 ;

% Normalization coefficient:

NORM_COEF                 (idx, [1:   4]) = [  1.88798E+15 0.00030  0.00000E+00 0.0E+00 ];

% Parameters for burnup calculation:

BURN_MATERIALS            (idx, 1)        = 2 ;
BURN_MODE                 (idx, 1)        = 2 ;
BURN_STEP                 (idx, 1)        = 1 ;
BURN_RANDOMIZE_DATA       (idx, [1:  2])  = [ 0 0 ];
BURNUP                    (idx, [1:  2])  = [  5.35095E-02  5.35110E-02 ];
BURN_DAYS                 (idx, [1:  2])  = [  3.00000E+00  3.00000E+00 ];

% Analog reaction rate estimators:

CONVERSION_RATIO          (idx, [1:   2]) = [  8.06564E-01 0.00052 ];
U235_FISS                 (idx, [1:   4]) = [  3.55772E+19 0.00036  9.23952E-01 0.00012 ];
U238_FISS                 (idx, [1:   4]) = [  2.71255E+18 0.00170  7.04432E-02 0.00160 ];
PU239_FISS                (idx, [1:   4]) = [  2.14037E+17 0.00531  5.55864E-03 0.00530 ];
PU240_FISS                (idx, [1:   4]) = [  1.89793E+13 0.57542  4.91525E-07 0.57543 ];
PU241_FISS                (idx, [1:   4]) = [  6.32329E+12 1.00000  1.64878E-07 1.00000 ];
U235_CAPT                 (idx, [1:   4]) = [  1.15816E+19 0.00072  2.13140E-01 0.00063 ];
U238_CAPT                 (idx, [1:   4]) = [  3.83133E+19 0.00048  7.05091E-01 0.00022 ];
PU239_CAPT                (idx, [1:   4]) = [  1.31179E+17 0.00695  2.41429E-03 0.00697 ];
PU240_CAPT                (idx, [1:   4]) = [  4.23146E+15 0.03871  7.78617E-05 0.03869 ];
PU241_CAPT                (idx, [1:   4]) = [  1.26564E+13 0.70592  2.33276E-07 0.70592 ];
XE135_CAPT                (idx, [1:   4]) = [  5.25865E+17 0.00353  9.67780E-03 0.00352 ];
SM149_CAPT                (idx, [1:   4]) = [  4.58939E+16 0.01144  8.44680E-04 0.01145 ];

% Neutron balance (particles/weight):

BALA_SRC_NEUTRON_SRC     (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_SRC_NEUTRON_FISS    (idx, [1:  2])  = [ 15000439 1.50000E+07 ];
BALA_SRC_NEUTRON_NXN     (idx, [1:  2])  = [ 0 1.63473E+04 ];
BALA_SRC_NEUTRON_VR      (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_SRC_NEUTRON_TOT     (idx, [1:  2])  = [ 15000439 1.50163E+07 ];

BALA_LOSS_NEUTRON_CAPT    (idx, [1:  2])  = [ 8624897 8.63426E+06 ];
BALA_LOSS_NEUTRON_FISS    (idx, [1:  2])  = [ 6112289 6.11858E+06 ];
BALA_LOSS_NEUTRON_LEAK    (idx, [1:  2])  = [ 263253 2.63511E+05 ];
BALA_LOSS_NEUTRON_CUT     (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_LOSS_NEUTRON_ERR     (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_LOSS_NEUTRON_TOT     (idx, [1:  2])  = [ 15000439 1.50163E+07 ];

BALA_NEUTRON_DIFF         (idx, [1:  2])  = [ 0 -5.02914E-08 ];

% Normalized total reaction rates (neutrons):

TOT_POWER                 (idx, [1:   6]) = [  1.25000E+09 0.0E+00  1.25000E+09 0.0E+00  0.00000E+00 0.0E+00 ];
TOT_POWDENS               (idx, [1:   6]) = [  1.78365E-02 0.0E+00  1.78365E-02 0.0E+00  0.00000E+00 0.0E+00 ];
TOT_GENRATE               (idx, [1:   6]) = [  9.49397E+19 5.3E-06  9.49397E+19 5.3E-06  0.00000E+00 0.0E+00 ];
TOT_FISSRATE              (idx, [1:   6]) = [  3.85155E+19 5.5E-07  3.85155E+19 5.5E-07  0.00000E+00 0.0E+00 ];
TOT_CAPTRATE              (idx, [1:   6]) = [  5.43328E+19 0.00027  5.19999E+19 0.00028  2.33283E+18 0.00061 ];
TOT_ABSRATE               (idx, [1:   6]) = [  9.28482E+19 0.00016  9.05154E+19 0.00016  2.33283E+18 0.00061 ];
TOT_SRCRATE               (idx, [1:   6]) = [  9.43992E+19 0.00030  9.43992E+19 0.00030  0.00000E+00 0.0E+00 ];
TOT_FLUX                  (idx, [1:   6]) = [  8.45491E+21 0.00027  7.47707E+21 0.00028  9.77841E+20 0.00028 ];
TOT_PHOTON_PRODRATE       (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
TOT_LEAKRATE              (idx, [1:   2]) = [  1.65836E+18 0.00233 ];
ALBEDO_LEAKRATE           (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
TOT_LOSSRATE              (idx, [1:   2]) = [  9.45066E+19 0.00017 ];
TOT_CUTRATE               (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
TOT_RR                    (idx, [1:   2]) = [  3.53065E+21 0.00026 ];
INI_FMASS                 (idx, 1)        =  7.00810E+04 ;
TOT_FMASS                 (idx, 1)        =  7.00771E+04 ;
INI_BURN_FMASS            (idx, 1)        =  7.00810E+04 ;
TOT_BURN_FMASS            (idx, 1)        =  7.00771E+04 ;

% Six-factor formula:

SIX_FF_ETA                (idx, [1:   2]) = [  1.81868E+00 0.00032 ];
SIX_FF_F                  (idx, [1:   2]) = [  9.70416E-01 9.3E-05 ];
SIX_FF_P                  (idx, [1:   2]) = [  2.27808E-01 0.00046 ];
SIX_FF_EPSILON            (idx, [1:   2]) = [  2.54579E+00 0.00048 ];
SIX_FF_LF                 (idx, [1:   2]) = [  9.82455E-01 4.1E-05 ];
SIX_FF_LT                 (idx, [1:   2]) = [  9.99978E-01 1.2E-06 ];
SIX_FF_KINF               (idx, [1:   2]) = [  1.02346E+00 0.00030 ];
SIX_FF_KEFF               (idx, [1:   2]) = [  1.00549E+00 0.00030 ];

% Fission neutron and energy production:

NUBAR                     (idx, [1:   2]) = [  2.46498E+00 5.8E-06 ];
FISSE                     (idx, [1:   2]) = [  2.02565E+02 5.5E-07 ];

% Criticality eigenvalues:

ANA_KEFF                  (idx, [1:   6]) = [  1.00542E+00 0.00032  9.98339E-01 0.00030  7.14561E-03 0.00471 ];
IMP_KEFF                  (idx, [1:   2]) = [  1.00569E+00 0.00017 ];
COL_KEFF                  (idx, [1:   2]) = [  1.00575E+00 0.00030 ];
ABS_KEFF                  (idx, [1:   2]) = [  1.00569E+00 0.00017 ];
ABS_KINF                  (idx, [1:   2]) = [  1.02368E+00 0.00016 ];
GEOM_ALBEDO               (idx, [1:   6]) = [  1.00000E+00 0.0E+00  1.00000E+00 0.0E+00  1.00000E+00 0.0E+00 ];

% ALF (Average lethargy of neutrons causing fission):
% Based on E0 = 2.000000E+01 MeV

ANA_ALF                   (idx, [1:   2]) = [  1.39866E+01 0.00015 ];
IMP_ALF                   (idx, [1:   2]) = [  1.39887E+01 9.1E-05 ];

% EALF (Energy corresponding to average lethargy of neutrons causing fission):

ANA_EALF                  (idx, [1:   2]) = [  1.68667E-05 0.00211 ];
IMP_EALF                  (idx, [1:   2]) = [  1.68244E-05 0.00127 ];

% AFGE (Average energy of neutrons causing fission):

ANA_AFGE                  (idx, [1:   2]) = [  2.40339E-01 0.00154 ];
IMP_AFGE                  (idx, [1:   2]) = [  2.40125E-01 0.00048 ];

% Forward-weighted delayed neutron parameters:

PRECURSOR_GROUPS          (idx, 1)        = 8 ;
FWD_ANA_BETA_ZERO         (idx, [1:  18]) = [  7.39026E-03 0.00312  2.19973E-04 0.01763  1.06376E-03 0.00788  6.32466E-04 0.01052  1.39341E-03 0.00701  2.30227E-03 0.00542  8.22292E-04 0.00841  6.85158E-04 0.01013  2.70932E-04 0.01507 ];
FWD_ANA_LAMBDA            (idx, [1:  18]) = [  4.80259E-01 0.00451  1.24667E-02 0.0E+00  2.82917E-02 4.9E-09  4.25244E-02 7.1E-09  1.33042E-01 0.0E+00  2.92467E-01 0.0E+00  6.66488E-01 0.0E+00  1.63478E+00 5.2E-09  3.55460E+00 0.0E+00 ];

% Beta-eff using Meulekamp's method:

ADJ_MEULEKAMP_BETA_EFF    (idx, [1:  18]) = [  7.21987E-03 0.00520  2.09985E-04 0.02545  1.02291E-03 0.01341  6.31829E-04 0.01674  1.37666E-03 0.01105  2.24969E-03 0.00879  7.73211E-04 0.01389  6.95250E-04 0.01632  2.60327E-04 0.02508 ];
ADJ_MEULEKAMP_LAMBDA      (idx, [1:  18]) = [  4.81508E-01 0.00740  1.24667E-02 0.0E+00  2.82917E-02 4.8E-09  4.25244E-02 6.8E-09  1.33042E-01 0.0E+00  2.92467E-01 0.0E+00  6.66488E-01 0.0E+00  1.63478E+00 5.3E-09  3.55460E+00 0.0E+00 ];

% Adjoint weighted time constants using Nauchi's method:

IFP_CHAIN_LENGTH          (idx, 1)        = 15 ;
ADJ_NAUCHI_GEN_TIME       (idx, [1:   6]) = [  1.49164E-05 0.00073  1.49059E-05 0.00074  1.63825E-05 0.00782 ];
ADJ_NAUCHI_LIFETIME       (idx, [1:   6]) = [  1.49967E-05 0.00063  1.49861E-05 0.00064  1.64711E-05 0.00782 ];
ADJ_NAUCHI_BETA_EFF       (idx, [1:  18]) = [  7.10272E-03 0.00478  2.07442E-04 0.02764  1.00817E-03 0.01373  6.11975E-04 0.01749  1.35434E-03 0.00983  2.21755E-03 0.00881  7.75679E-04 0.01347  6.75225E-04 0.01689  2.52335E-04 0.02509 ];
ADJ_NAUCHI_LAMBDA         (idx, [1:  18]) = [  4.78799E-01 0.00741  1.24667E-02 0.0E+00  2.82917E-02 4.9E-09  4.25244E-02 7.1E-09  1.33042E-01 0.0E+00  2.92467E-01 0.0E+00  6.66488E-01 0.0E+00  1.63478E+00 5.2E-09  3.55460E+00 0.0E+00 ];

% Adjoint weighted time constants using IFP:

ADJ_IFP_GEN_TIME          (idx, [1:   6]) = [  1.50230E-05 0.00179  1.50135E-05 0.00182  1.62610E-05 0.02089 ];
ADJ_IFP_LIFETIME          (idx, [1:   6]) = [  1.51041E-05 0.00179  1.50946E-05 0.00182  1.63494E-05 0.02090 ];
ADJ_IFP_IMP_BETA_EFF      (idx, [1:  18]) = [  7.20047E-03 0.01616  2.15443E-04 0.09336  1.02874E-03 0.04272  6.63675E-04 0.05799  1.37329E-03 0.03724  2.18375E-03 0.02964  7.81047E-04 0.04638  7.13124E-04 0.05450  2.41410E-04 0.08283 ];
ADJ_IFP_IMP_LAMBDA        (idx, [1:  18]) = [  4.76580E-01 0.02423  1.24667E-02 0.0E+00  2.82917E-02 5.8E-09  4.25244E-02 7.5E-09  1.33042E-01 0.0E+00  2.92467E-01 0.0E+00  6.66488E-01 0.0E+00  1.63478E+00 5.4E-09  3.55460E+00 0.0E+00 ];
ADJ_IFP_ANA_BETA_EFF      (idx, [1:  18]) = [  7.15923E-03 0.01543  2.14497E-04 0.08924  1.01670E-03 0.04059  6.42274E-04 0.05483  1.35073E-03 0.03597  2.19760E-03 0.02842  7.85019E-04 0.04508  7.11258E-04 0.05121  2.41157E-04 0.08147 ];
ADJ_IFP_ANA_LAMBDA        (idx, [1:  18]) = [  4.78035E-01 0.02372  1.24667E-02 0.0E+00  2.82917E-02 5.9E-09  4.25244E-02 7.9E-09  1.33042E-01 0.0E+00  2.92467E-01 0.0E+00  6.66488E-01 0.0E+00  1.63478E+00 5.4E-09  3.55460E+00 0.0E+00 ];
ADJ_IFP_ROSSI_ALPHA       (idx, [1:   2]) = [ -4.80064E+02 0.01626 ];

% Adjoint weighted time constants using perturbation technique:

ADJ_PERT_GEN_TIME         (idx, [1:   2]) = [  1.49846E-05 0.00044 ];
ADJ_PERT_LIFETIME         (idx, [1:   2]) = [  1.50653E-05 0.00031 ];
ADJ_PERT_BETA_EFF         (idx, [1:   2]) = [  7.11784E-03 0.00289 ];
ADJ_PERT_ROSSI_ALPHA      (idx, [1:   2]) = [ -4.75026E+02 0.00290 ];

% Inverse neutron speed :

ANA_INV_SPD               (idx, [1:   2]) = [  1.01799E-07 0.00039 ];

% Analog slowing-down and thermal neutron lifetime (total/prompt/delayed):

ANA_SLOW_TIME             (idx, [1:   6]) = [  9.35960E-06 0.00067  9.35971E-06 0.00067  9.34116E-06 0.00700 ];
ANA_THERM_TIME            (idx, [1:   6]) = [  2.19511E-05 0.00047  2.19503E-05 0.00047  2.20359E-05 0.00541 ];
ANA_THERM_FRAC            (idx, [1:   6]) = [  2.26976E-01 0.00045  2.26867E-01 0.00046  2.42428E-01 0.00701 ];
ANA_DELAYED_EMTIME        (idx, [1:   2]) = [  1.22792E+01 0.00667 ];
ANA_MEAN_NCOL             (idx, [1:   4]) = [  3.73626E+01 0.00013  3.94456E+01 0.00020 ];

% Group constant generation:

GC_UNIVERSE_NAME          (idx, [1:  1])  = '0' ;

% Micro- and macro-group structures:

MICRO_NG                  (idx, 1)        = 70 ;
MICRO_E                   (idx, [1:  71]) = [  1.00000E-11  5.00000E-09  1.00000E-08  1.50000E-08  2.00000E-08  2.50000E-08  3.00000E-08  3.50000E-08  4.20000E-08  5.00000E-08  5.80000E-08  6.70000E-08  8.00000E-08  1.00000E-07  1.40000E-07  1.80000E-07  2.20000E-07  2.50000E-07  2.80000E-07  3.00000E-07  3.20000E-07  3.50000E-07  4.00000E-07  5.00000E-07  6.25000E-07  7.80000E-07  8.50000E-07  9.10000E-07  9.50000E-07  9.72000E-07  9.96000E-07  1.02000E-06  1.04500E-06  1.07100E-06  1.09700E-06  1.12300E-06  1.15000E-06  1.30000E-06  1.50000E-06  1.85500E-06  2.10000E-06  2.60000E-06  3.30000E-06  4.00000E-06  9.87700E-06  1.59680E-05  2.77000E-05  4.80520E-05  7.55014E-05  1.48728E-04  3.67262E-04  9.06898E-04  1.42510E-03  2.23945E-03  3.51910E-03  5.50000E-03  9.11800E-03  1.50300E-02  2.47800E-02  4.08500E-02  6.74300E-02  1.11000E-01  1.83000E-01  3.02500E-01  5.00000E-01  8.21000E-01  1.35300E+00  2.23100E+00  3.67900E+00  6.06550E+00  2.00000E+01 ];

MACRO_NG                  (idx, 1)        = 2 ;
MACRO_E                   (idx, [1:   3]) = [  1.00000E+37  6.25000E-07  0.00000E+00 ];

% Micro-group spectrum:

INF_MICRO_FLX             (idx, [1: 140]) = [  2.60548E+05 0.00257  1.19908E+06 0.00056  2.79722E+06 0.00052  4.20247E+06 0.00049  5.12165E+06 0.00029  6.32123E+06 0.00025  3.47114E+06 0.00029  3.00533E+06 0.00034  5.72271E+06 0.00039  5.17436E+06 0.00026  5.48158E+06 0.00042  4.67575E+06 0.00044  4.69182E+06 0.00045  3.76736E+06 0.00067  3.27021E+06 0.00049  2.59900E+06 0.00086  2.40424E+06 0.00084  2.25630E+06 0.00082  2.08408E+06 0.00055  3.66599E+06 0.00058  3.08490E+06 0.00049  1.91129E+06 0.00076  1.07829E+06 0.00057  1.05764E+06 0.00065  8.54071E+05 0.00083  8.04708E+05 0.00076  1.08288E+06 0.00049  3.34853E+05 0.00094  5.30040E+05 0.00107  5.54164E+05 0.00111  3.27007E+05 0.00131  5.99512E+05 0.00117  4.08523E+05 0.00140  3.18883E+05 0.00170  5.57217E+04 0.00231  5.41846E+04 0.00215  5.55997E+04 0.00234  5.74699E+04 0.00182  5.72585E+04 0.00232  5.66153E+04 0.00283  5.79436E+04 0.00279  5.43303E+04 0.00279  1.01762E+05 0.00210  1.62612E+05 0.00188  2.01800E+05 0.00140  5.10824E+05 0.00113  4.85446E+05 0.00097  4.36776E+05 0.00124  2.31805E+05 0.00117  1.39926E+05 0.00165  9.33114E+04 0.00146  9.76528E+04 0.00107  1.56273E+05 0.00138  1.72517E+05 0.00152  2.50182E+05 0.00182  2.69076E+05 0.00101  2.75755E+05 0.00178  1.29217E+05 0.00203  7.67450E+04 0.00240  4.74111E+04 0.00179  3.80344E+04 0.00267  3.43578E+04 0.00235  2.53177E+04 0.00249  1.62777E+04 0.00283  1.33591E+04 0.00267  1.11360E+04 0.00298  8.83793E+03 0.00366  6.52646E+03 0.00473  3.79409E+03 0.00455  1.30384E+03 0.01015 ];

% Integral parameters:

INF_KINF                  (idx, [1:   2]) = [  1.02374E+00 0.00032 ];

% Flux spectra in infinite geometry:

INF_FLX                   (idx, [1:   4]) = [  8.16977E+21 0.00034  2.85183E+20 0.00026 ];
INF_FISS_FLX              (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Reaction cross sections:

INF_TOT                   (idx, [1:   4]) = [  4.14147E-01 5.1E-05  5.16131E-01 0.00024 ];
INF_CAPT                  (idx, [1:   4]) = [  5.93426E-03 0.00021  2.05195E-02 0.00018 ];
INF_ABS                   (idx, [1:   4]) = [  8.77844E-03 0.00016  7.40997E-02 0.00020 ];
INF_FISS                  (idx, [1:   4]) = [  2.84418E-03 0.00020  5.35802E-02 0.00022 ];
INF_NSF                   (idx, [1:   4]) = [  7.05606E-03 0.00020  1.30779E-01 0.00022 ];
INF_NUBAR                 (idx, [1:   4]) = [  2.48088E+00 8.0E-06  2.44080E+00 7.0E-07 ];
INF_KAPPA                 (idx, [1:   4]) = [  2.02719E+02 8.0E-07  2.02332E+02 1.1E-07 ];
INF_INVV                  (idx, [1:   4]) = [  4.88947E-08 0.00045  1.61738E-06 0.00015 ];

% Total scattering cross sections:

INF_SCATT0                (idx, [1:   4]) = [  4.05368E-01 5.3E-05  4.42048E-01 0.00027 ];
INF_SCATT1                (idx, [1:   4]) = [  7.40047E-02 0.00028  6.96958E-02 0.00076 ];
INF_SCATT2                (idx, [1:   4]) = [  2.72729E-02 0.00044  1.87907E-02 0.00258 ];
INF_SCATT3                (idx, [1:   4]) = [  3.18783E-03 0.00223  5.76947E-03 0.00772 ];
INF_SCATT4                (idx, [1:   4]) = [ -1.43650E-03 0.00347  2.19390E-04 0.14593 ];
INF_SCATT5                (idx, [1:   4]) = [  3.53095E-04 0.01293  7.62005E-04 0.04118 ];
INF_SCATT6                (idx, [1:   4]) = [  1.30619E-03 0.00416 -1.11937E-03 0.01900 ];
INF_SCATT7                (idx, [1:   4]) = [  2.23106E-04 0.01683  1.92050E-04 0.12526 ];

% Total scattering production cross sections:

INF_SCATTP0               (idx, [1:   4]) = [  4.05381E-01 5.3E-05  4.42048E-01 0.00027 ];
INF_SCATTP1               (idx, [1:   4]) = [  7.40049E-02 0.00028  6.96958E-02 0.00076 ];
INF_SCATTP2               (idx, [1:   4]) = [  2.72730E-02 0.00044  1.87907E-02 0.00258 ];
INF_SCATTP3               (idx, [1:   4]) = [  3.18785E-03 0.00223  5.76947E-03 0.00772 ];
INF_SCATTP4               (idx, [1:   4]) = [ -1.43648E-03 0.00347  2.19390E-04 0.14593 ];
INF_SCATTP5               (idx, [1:   4]) = [  3.53101E-04 0.01296  7.62005E-04 0.04118 ];
INF_SCATTP6               (idx, [1:   4]) = [  1.30622E-03 0.00416 -1.11937E-03 0.01900 ];
INF_SCATTP7               (idx, [1:   4]) = [  2.23066E-04 0.01690  1.92050E-04 0.12526 ];

% Diffusion parameters:

INF_TRANSPXS              (idx, [1:   4]) = [  3.16294E-01 9.9E-05  4.21006E-01 0.00018 ];
INF_DIFFCOEF              (idx, [1:   4]) = [  1.05387E+00 9.9E-05  7.91754E-01 0.00018 ];

% Reduced absoption and removal:

INF_RABSXS                (idx, [1:   4]) = [  8.76585E-03 0.00016  7.40997E-02 0.00020 ];
INF_REMXS                 (idx, [1:   4]) = [  1.15827E-02 0.00016  8.03298E-02 0.00033 ];

% Poison cross sections:

INF_I135_YIELD            (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_XE135_YIELD           (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_PM147_YIELD           (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_PM148_YIELD           (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_PM148M_YIELD          (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_PM149_YIELD           (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_SM149_YIELD           (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_I135_MICRO_ABS        (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_XE135_MICRO_ABS       (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_PM147_MICRO_ABS       (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_PM148_MICRO_ABS       (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_PM148M_MICRO_ABS      (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_PM149_MICRO_ABS       (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_SM149_MICRO_ABS       (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_XE135_MACRO_ABS       (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_SM149_MACRO_ABS       (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Fission spectra:

INF_CHIT                  (idx, [1:   4]) = [  1.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_CHIP                  (idx, [1:   4]) = [  1.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_CHID                  (idx, [1:   4]) = [  1.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Scattering matrixes:

INF_S0                    (idx, [1:   8]) = [  4.02564E-01 5.2E-05  2.80435E-03 0.00058  6.24765E-03 0.00154  4.35801E-01 0.00027 ];
INF_S1                    (idx, [1:   8]) = [  7.34930E-02 0.00028  5.11705E-04 0.00162  3.30062E-04 0.01964  6.93657E-02 0.00081 ];
INF_S2                    (idx, [1:   8]) = [  2.74773E-02 0.00043 -2.04325E-04 0.00274 -1.35116E-05 0.42624  1.88042E-02 0.00253 ];
INF_S3                    (idx, [1:   8]) = [  3.42428E-03 0.00210 -2.36446E-04 0.00155 -1.32909E-04 0.03556  5.90238E-03 0.00768 ];
INF_S4                    (idx, [1:   8]) = [ -1.34376E-03 0.00384 -9.27418E-05 0.00456 -1.61760E-04 0.02552  3.81150E-04 0.08717 ];
INF_S5                    (idx, [1:   8]) = [  3.66679E-04 0.01244 -1.35840E-05 0.03178 -1.33388E-04 0.02217  8.95393E-04 0.03600 ];
INF_S6                    (idx, [1:   8]) = [  1.32249E-03 0.00408 -1.62936E-05 0.01848 -9.04214E-05 0.02852 -1.02894E-03 0.01950 ];
INF_S7                    (idx, [1:   8]) = [  2.36658E-04 0.01603 -1.35523E-05 0.01872 -5.21558E-05 0.05981  2.44205E-04 0.09516 ];

% Scattering production matrixes:

INF_SP0                   (idx, [1:   8]) = [  4.02577E-01 5.2E-05  2.80435E-03 0.00058  6.24765E-03 0.00154  4.35801E-01 0.00027 ];
INF_SP1                   (idx, [1:   8]) = [  7.34932E-02 0.00028  5.11705E-04 0.00162  3.30062E-04 0.01964  6.93657E-02 0.00081 ];
INF_SP2                   (idx, [1:   8]) = [  2.74773E-02 0.00043 -2.04325E-04 0.00274 -1.35116E-05 0.42624  1.88042E-02 0.00253 ];
INF_SP3                   (idx, [1:   8]) = [  3.42429E-03 0.00210 -2.36446E-04 0.00155 -1.32909E-04 0.03556  5.90238E-03 0.00768 ];
INF_SP4                   (idx, [1:   8]) = [ -1.34373E-03 0.00385 -9.27418E-05 0.00456 -1.61760E-04 0.02552  3.81150E-04 0.08717 ];
INF_SP5                   (idx, [1:   8]) = [  3.66685E-04 0.01246 -1.35840E-05 0.03178 -1.33388E-04 0.02217  8.95393E-04 0.03600 ];
INF_SP6                   (idx, [1:   8]) = [  1.32251E-03 0.00409 -1.62936E-05 0.01848 -9.04214E-05 0.02852 -1.02894E-03 0.01950 ];
INF_SP7                   (idx, [1:   8]) = [  2.36619E-04 0.01610 -1.35523E-05 0.01872 -5.21558E-05 0.05981  2.44205E-04 0.09516 ];

% Micro-group spectrum:

B1_MICRO_FLX              (idx, [1: 140]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Integral parameters:

B1_KINF                   (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
B1_KEFF                   (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
B1_B2                     (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
B1_ERR                    (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];

% Critical spectra in infinite geometry:

B1_FLX                    (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_FISS_FLX               (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Reaction cross sections:

B1_TOT                    (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_CAPT                   (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_ABS                    (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_FISS                   (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_NSF                    (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_NUBAR                  (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_KAPPA                  (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_INVV                   (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Total scattering cross sections:

B1_SCATT0                 (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATT1                 (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATT2                 (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATT3                 (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATT4                 (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATT5                 (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATT6                 (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATT7                 (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Total scattering production cross sections:

B1_SCATTP0                (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATTP1                (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATTP2                (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATTP3                (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATTP4                (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATTP5                (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATTP6                (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATTP7                (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Diffusion parameters:

B1_TRANSPXS               (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_DIFFCOEF               (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Reduced absoption and removal:

B1_RABSXS                 (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_REMXS                  (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Poison cross sections:

B1_I135_YIELD             (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_XE135_YIELD            (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_PM147_YIELD            (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_PM148_YIELD            (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_PM148M_YIELD           (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_PM149_YIELD            (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SM149_YIELD            (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_I135_MICRO_ABS         (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_XE135_MICRO_ABS        (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_PM147_MICRO_ABS        (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_PM148_MICRO_ABS        (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_PM148M_MICRO_ABS       (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_PM149_MICRO_ABS        (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SM149_MICRO_ABS        (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_XE135_MACRO_ABS        (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SM149_MACRO_ABS        (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Fission spectra:

B1_CHIT                   (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_CHIP                   (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_CHID                   (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Scattering matrixes:

B1_S0                     (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_S1                     (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_S2                     (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_S3                     (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_S4                     (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_S5                     (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_S6                     (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_S7                     (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Scattering production matrixes:

B1_SP0                    (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SP1                    (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SP2                    (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SP3                    (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SP4                    (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SP5                    (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SP6                    (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SP7                    (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Additional diffusion parameters:

CMM_TRANSPXS              (idx, [1:   4]) = [  3.05442E-01 0.00028  3.85990E-01 0.00236 ];
CMM_TRANSPXS_X            (idx, [1:   4]) = [  3.07466E-01 0.00055  3.80363E-01 0.00373 ];
CMM_TRANSPXS_Y            (idx, [1:   4]) = [  3.07125E-01 0.00053  3.82214E-01 0.00217 ];
CMM_TRANSPXS_Z            (idx, [1:   4]) = [  3.01803E-01 0.00047  3.95936E-01 0.00548 ];
CMM_DIFFCOEF              (idx, [1:   4]) = [  1.09132E+00 0.00028  8.63648E-01 0.00236 ];
CMM_DIFFCOEF_X            (idx, [1:   4]) = [  1.08413E+00 0.00055  8.76528E-01 0.00375 ];
CMM_DIFFCOEF_Y            (idx, [1:   4]) = [  1.08534E+00 0.00053  8.72171E-01 0.00217 ];
CMM_DIFFCOEF_Z            (idx, [1:   4]) = [  1.10448E+00 0.00047  8.42247E-01 0.00558 ];

% Delayed neutron parameters (Meulekamp method):

BETA_EFF                  (idx, [1:  18]) = [  7.21987E-03 0.00520  2.09985E-04 0.02545  1.02291E-03 0.01341  6.31829E-04 0.01674  1.37666E-03 0.01105  2.24969E-03 0.00879  7.73211E-04 0.01389  6.95250E-04 0.01632  2.60327E-04 0.02508 ];
LAMBDA                    (idx, [1:  18]) = [  4.81508E-01 0.00740  1.24667E-02 0.0E+00  2.82917E-02 4.8E-09  4.25244E-02 6.8E-09  1.33042E-01 0.0E+00  2.92467E-01 0.0E+00  6.66488E-01 0.0E+00  1.63478E+00 5.3E-09  3.55460E+00 0.0E+00 ];

