
% Increase counter:

if (exist('idx', 'var'));
  idx = idx + 1;
else;
  idx = 1;
end;

% Version, title and date:

VERSION                   (idx, [1: 14])  = 'Serpent 2.1.30' ;
COMPILE_DATE              (idx, [1: 20])  = 'Feb 14 2018 21:59:44' ;
DEBUG                     (idx, 1)        = 0 ;
TITLE                     (idx, [1: 52])  = 'themperature coefficient of reactivity 900K for both' ;
CONFIDENTIAL_DATA         (idx, 1)        = 0 ;
INPUT_FILE_NAME           (idx, [1:  4])  = 'core' ;
WORKING_DIRECTORY         (idx, [1: 62])  = '/home/andrei2/Desktop/git/MScThesis-MSBR/serpent/thermal_coeff' ;
HOSTNAME                  (idx, [1: 28])  = 'andrei2-Precision-Tower-3420' ;
CPU_TYPE                  (idx, [1: 41])  = 'Intel(R) Xeon(R) CPU E3-1225 v5 @ 3.30GHz' ;
CPU_MHZ                   (idx, 1)        = 186.0 ;
START_DATE                (idx, [1: 24])  = 'Wed Mar 28 10:26:06 2018' ;
COMPLETE_DATE             (idx, [1: 24])  = 'Wed Mar 28 10:26:51 2018' ;

% Run parameters:

POP                       (idx, 1)        = 1000 ;
CYCLES                    (idx, 1)        = 50 ;
SKIP                      (idx, 1)        = 10 ;
BATCH_INTERVAL            (idx, 1)        = 1 ;
SRC_NORM_MODE             (idx, 1)        = 2 ;
SEED                      (idx, 1)        = 1522250766 ;
UFS_MODE                  (idx, 1)        = 0 ;
UFS_ORDER                 (idx, 1)        = 1.00000;
NEUTRON_TRANSPORT_MODE    (idx, 1)        = 1 ;
PHOTON_TRANSPORT_MODE     (idx, 1)        = 0 ;
GROUP_CONSTANT_GENERATION (idx, 1)        = 1 ;
B1_CALCULATION            (idx, [1:  3])  = [ 0 0 0 ];
B1_BURNUP_CORRECTION      (idx, 1)        = 0 ;
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
OMP_HISTORY_PROFILE       (idx, [1:   4]) = [  1.24948E+00  9.13562E-01  9.34233E-01  9.02728E-01  ];
SHARE_BUF_ARRAY           (idx, 1)        = 0 ;
SHARE_RES2_ARRAY          (idx, 1)        = 1 ;

% File paths:

XS_DATA_FILE_PATH         (idx, [1: 55])  = '/home/andrei2/serpent/xsdata/jeff312/sss_jeff312.xsdata' ;
DECAY_DATA_FILE_PATH      (idx, [1: 51])  = '/home/andrei2/serpent/xsdata/jeff312/sss_jeff33.dec' ;
SFY_DATA_FILE_PATH        (idx, [1: 51])  = '/home/andrei2/serpent/xsdata/jeff312/sss_jeff33.nfy' ;
NFY_DATA_FILE_PATH        (idx, [1: 51])  = '/home/andrei2/serpent/xsdata/jeff312/sss_jeff33.nfy' ;
BRA_DATA_FILE_PATH        (idx, [1:  3])  = 'N/A' ;

% Collision and reaction sampling (neutrons/photons):

MIN_MACROXS               (idx, [1:   4]) = [  5.00000E-02 0.0E+00  0.00000E+00 0.0E+00 ];
DT_THRESH                 (idx, [1:  2])  = [  9.00000E-01  9.00000E-01 ];
ST_FRAC                   (idx, [1:   4]) = [  1.26734E-03 0.01313  0.00000E+00 0.0E+00 ];
DT_FRAC                   (idx, [1:   4]) = [  9.98733E-01 1.7E-05  0.00000E+00 0.0E+00 ];
DT_EFF                    (idx, [1:   4]) = [  9.11277E-01 0.00033  0.00000E+00 0.0E+00 ];
REA_SAMPLING_EFF          (idx, [1:   4]) = [  1.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
REA_SAMPLING_FAIL         (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
TOT_COL_EFF               (idx, [1:   4]) = [  9.11351E-01 0.00033  0.00000E+00 0.0E+00 ];
AVG_TRACKING_LOOPS        (idx, [1:   8]) = [  2.38972E+00 0.00244  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
AVG_TRACKS                (idx, [1:   4]) = [  1.53754E+02 0.00458  0.00000E+00 0.0E+00 ];
AVG_REAL_COL              (idx, [1:   4]) = [  1.53742E+02 0.00458  0.00000E+00 0.0E+00 ];
AVG_VIRT_COL              (idx, [1:   4]) = [  1.49450E+01 0.00248  0.00000E+00 0.0E+00 ];
AVG_SURF_CROSS            (idx, [1:   4]) = [  8.54575E-02 0.02157  0.00000E+00 0.0E+00 ];
LOST_PARTICLES            (idx, 1)        = 0 ;

% Run statistics:

CYCLE_IDX                 (idx, 1)        = 50 ;
SOURCE_POPULATION         (idx, 1)        = 50133 ;
MEAN_POP_SIZE             (idx, [1:  2])  = [  1.00266E+03 0.00686 ];
MEAN_POP_WGT              (idx, [1:  2])  = [  1.00266E+03 0.00686 ];
SIMULATION_COMPLETED      (idx, 1)        = 1 ;

% Running times:

TOT_CPU_TIME              (idx, 1)        =  9.37779E-01 ;
RUNNING_TIME              (idx, 1)        =  7.35300E-01 ;
INIT_TIME                 (idx, [1:  2])  = [  4.68367E-01  4.68367E-01 ];
PROCESS_TIME              (idx, [1:  2])  = [  7.49997E-04  7.49997E-04 ];
TRANSPORT_CYCLE_TIME      (idx, [1:  3])  = [  1.95267E-01  1.95267E-01  0.00000E+00 ];
BURNUP_CYCLE_TIME         (idx, [1:  2])  = [  0.00000E+00  0.00000E+00 ];
BATEMAN_SOLUTION_TIME     (idx, [1:  2])  = [  0.00000E+00  0.00000E+00 ];
MPI_OVERHEAD_TIME         (idx, [1:  2])  = [  0.00000E+00  0.00000E+00 ];
ESTIMATED_RUNNING_TIME    (idx, [1:  2])  = [  6.64350E-01  0.00000E+00 ];
CPU_USAGE                 (idx, 1)        = 1.27537 ;
TRANSPORT_CPU_USAGE       (idx, [1:   2]) = [  3.03444E+00 0.02284 ];
OMP_PARALLEL_FRAC         (idx, 1)        =  2.47541E-01 ;

% Memory usage:

AVAIL_MEM                 (idx, 1)        = 32069.96 ;
ALLOC_MEMSIZE             (idx, 1)        = 5614.26;
MEMSIZE                   (idx, 1)        = 5547.15;
XS_MEMSIZE                (idx, 1)        = 5492.80;
MAT_MEMSIZE               (idx, 1)        = 35.51;
RES_MEMSIZE               (idx, 1)        = 0.83;
MISC_MEMSIZE              (idx, 1)        = 18.01;
UNKNOWN_MEMSIZE           (idx, 1)        = 0.00;
UNUSED_MEMSIZE            (idx, 1)        = 67.11;

% Geometry parameters:

TOT_CELLS                 (idx, 1)        = 329 ;
UNION_CELLS               (idx, 1)        = 0 ;

% Neutron energy grid:

NEUTRON_ERG_TOL           (idx, 1)        =  5.00000E-05 ;
NEUTRON_ERG_NE            (idx, 1)        = 305328 ;
NEUTRON_EMIN              (idx, 1)        =  1.00000E-09 ;
NEUTRON_EMAX              (idx, 1)        =  1.50000E+01 ;

% Unresolved resonance probability table sampling:

URES_DILU_CUT             (idx, 1)        =  1.00000E-09 ;
URES_EMIN                 (idx, 1)        =  1.00000E+37 ;
URES_EMAX                 (idx, 1)        = -1.00000E+37 ;
URES_AVAIL                (idx, 1)        = 125 ;
URES_USED                 (idx, 1)        = 0 ;

% Nuclides and reaction channels:

TOT_NUCLIDES              (idx, 1)        = 1161 ;
TOT_TRANSPORT_NUCLIDES    (idx, 1)        = 240 ;
TOT_DOSIMETRY_NUCLIDES    (idx, 1)        = 0 ;
TOT_DECAY_NUCLIDES        (idx, 1)        = 921 ;
TOT_PHOTON_NUCLIDES       (idx, 1)        = 0 ;
TOT_REA_CHANNELS          (idx, 1)        = 5162 ;
TOT_TRANSMU_REA           (idx, 1)        = 1692 ;

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

TOT_ACTIVITY              (idx, 1)        =  5.85536E+13 ;
TOT_DECAY_HEAT            (idx, 1)        =  4.60858E+01 ;
TOT_SF_RATE               (idx, 1)        =  4.45749E-01 ;
ACTINIDE_ACTIVITY         (idx, 1)        =  5.85536E+13 ;
ACTINIDE_DECAY_HEAT       (idx, 1)        =  4.60858E+01 ;
FISSION_PRODUCT_ACTIVITY  (idx, 1)        =  0.00000E+00 ;
FISSION_PRODUCT_DECAY_HEAT(idx, 1)        =  0.00000E+00 ;
INHALATION_TOXICITY       (idx, 1)        =  5.65312E+08 ;
INGESTION_TOXICITY        (idx, 1)        =  2.99193E+06 ;
ACTINIDE_INH_TOX          (idx, 1)        =  5.65312E+08 ;
ACTINIDE_ING_TOX          (idx, 1)        =  2.99193E+06 ;
FISSION_PRODUCT_INH_TOX   (idx, 1)        =  0.00000E+00 ;
FISSION_PRODUCT_ING_TOX   (idx, 1)        =  0.00000E+00 ;
SR90_ACTIVITY             (idx, 1)        =  0.00000E+00 ;
TE132_ACTIVITY            (idx, 1)        =  0.00000E+00 ;
I131_ACTIVITY             (idx, 1)        =  0.00000E+00 ;
I132_ACTIVITY             (idx, 1)        =  0.00000E+00 ;
CS134_ACTIVITY            (idx, 1)        =  0.00000E+00 ;
CS137_ACTIVITY            (idx, 1)        =  0.00000E+00 ;
PHOTON_DECAY_SOURCE       (idx, 1)        =  4.95115E+12 ;
NEUTRON_DECAY_SOURCE      (idx, 1)        =  6.68624E-01 ;
ALPHA_DECAY_SOURCE        (idx, 1)        =  5.86059E+13 ;
ELECTRON_DECAY_SOURCE     (idx, 1)        =  2.93616E+13 ;

% Normalization coefficient:

NORM_COEF                 (idx, [1:   4]) = [  1.63964E+17 0.00513  0.00000E+00 0.0E+00 ];

% Parameters for burnup calculation:

BURN_MATERIALS            (idx, 1)        = 1 ;
BURN_MODE                 (idx, 1)        = 2 ;
BURN_STEP                 (idx, 1)        = 0 ;
BURNUP                     (idx, [1:  2])  = [  0.00000E+00  0.00000E+00 ];
BURN_DAYS                 (idx, 1)        =  0.00000E+00 ;

% Analog reaction rate estimators:

CONVERSION_RATIO          (idx, [1:   2]) = [  9.63350E-01 0.00819 ];
TH232_FISS                (idx, [1:   4]) = [  3.15626E+17 0.09457  4.42982E-03 0.09360 ];
U233_FISS                 (idx, [1:   4]) = [  7.07258E+19 0.00692  9.95570E-01 0.00042 ];
TH232_CAPT                (idx, [1:   4]) = [  7.61785E+19 0.00670  8.34748E-01 0.00236 ];
U233_CAPT                 (idx, [1:   4]) = [  8.47366E+18 0.01976  9.29122E-02 0.01918 ];

% Neutron balance (particles/weight):

BALA_SRC_NEUTRON_SRC     (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_SRC_NEUTRON_FISS    (idx, [1:  2])  = [ 50133 5.00000E+04 ];
BALA_SRC_NEUTRON_NXN     (idx, [1:  2])  = [ 0 1.31399E+02 ];
BALA_SRC_NEUTRON_VR      (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_SRC_NEUTRON_TOT     (idx, [1:  2])  = [ 50133 5.01314E+04 ];

BALA_LOSS_NEUTRON_CAPT    (idx, [1:  2])  = [ 27820 2.78284E+04 ];
BALA_LOSS_NEUTRON_FISS    (idx, [1:  2])  = [ 21675 2.16644E+04 ];
BALA_LOSS_NEUTRON_LEAK    (idx, [1:  2])  = [ 638 6.38577E+02 ];
BALA_LOSS_NEUTRON_CUT     (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_LOSS_NEUTRON_ERR     (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_LOSS_NEUTRON_TOT     (idx, [1:  2])  = [ 50133 5.01314E+04 ];

BALA_NEUTRON_DIFF         (idx, [1:  2])  = [ 0 -5.82077E-11 ];

% Normalized total reaction rates (neutrons):

TOT_POWER                 (idx, [1:   6]) = [  2.25000E+09 0.0E+00  2.25000E+09 0.0E+00  0.00000E+00 0.0E+00 ];
TOT_POWDENS               (idx, [1:   6]) = [  2.80838E-01 7.3E-09  2.80838E-01 7.3E-09  0.00000E+00 0.0E+00 ];
TOT_GENRATE               (idx, [1:   6]) = [  1.75333E+20 4.8E-06  1.75333E+20 4.8E-06  0.00000E+00 0.0E+00 ];
TOT_FISSRATE              (idx, [1:   6]) = [  7.04764E+19 5.0E-07  7.04764E+19 5.0E-07  0.00000E+00 0.0E+00 ];
TOT_CAPTRATE              (idx, [1:   6]) = [  9.11089E+19 0.00333  8.74058E+19 0.00334  3.70314E+18 0.00979 ];
TOT_ABSRATE               (idx, [1:   6]) = [  1.61585E+20 0.00188  1.57882E+20 0.00185  3.70314E+18 0.00979 ];
TOT_SRCRATE               (idx, [1:   6]) = [  1.63964E+20 0.00513  1.63964E+20 0.00513  0.00000E+00 0.0E+00 ];
TOT_FLUX                  (idx, [1:   6]) = [  6.26901E+22 0.00473  9.79808E+21 0.00513  5.28920E+22 0.00512 ];
TOT_PHOTON_PRODRATE       (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
TOT_LEAKRATE              (idx, [1:   2]) = [  2.09702E+18 0.05344 ];
ALBEDO_LEAKRATE           (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
TOT_LOSSRATE              (idx, [1:   2]) = [  1.63682E+20 0.00214 ];
TOT_CUTRATE               (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
TOT_RR                    (idx, [1:   2]) = [  2.52539E+22 0.00498 ];
INI_FMASS                 (idx, 1)        =  8.01172E+03 ;
TOT_FMASS                 (idx, 1)        =  8.01172E+03 ;
INI_BURN_FMASS            (idx, 1)        =  8.01172E+03 ;
TOT_BURN_FMASS            (idx, 1)        =  8.01172E+03 ;

% Six-factor formula:

SIX_FF_ETA                (idx, [1:   2]) = [  1.40811E+00 0.00547 ];
SIX_FF_F                  (idx, [1:   2]) = [  9.67442E-01 0.00104 ];
SIX_FF_P                  (idx, [1:   2]) = [  5.98030E-01 0.00398 ];
SIX_FF_EPSILON            (idx, [1:   2]) = [  1.34145E+00 0.00394 ];
SIX_FF_LF                 (idx, [1:   2]) = [  9.99937E-01 3.5E-05 ];
SIX_FF_LT                 (idx, [1:   2]) = [  9.87290E-01 0.00067 ];
SIX_FF_KINF               (idx, [1:   2]) = [  1.09175E+00 0.00463 ];
SIX_FF_KEFF               (idx, [1:   2]) = [  1.07782E+00 0.00477 ];

% Fission neutron and energy production:

NUBAR                     (idx, [1:   2]) = [  2.48783E+00 4.7E-06 ];
FISSE                     (idx, [1:   2]) = [  1.99264E+02 5.0E-07 ];

% Criticality eigenvalues:

ANA_KEFF                  (idx, [1:   6]) = [  1.07823E+00 0.00491  1.07491E+00 0.00474  2.91407E-03 0.13660 ];
IMP_KEFF                  (idx, [1:   2]) = [  1.07447E+00 0.00213 ];
COL_KEFF                  (idx, [1:   2]) = [  1.07072E+00 0.00515 ];
ABS_KEFF                  (idx, [1:   2]) = [  1.07447E+00 0.00213 ];
ABS_KINF                  (idx, [1:   2]) = [  1.08840E+00 0.00187 ];
GEOM_ALBEDO               (idx, [1:   6]) = [  1.00000E+00 0.0E+00  1.00000E+00 0.0E+00  1.00000E+00 0.0E+00 ];

% ALF (Average lethargy of neutrons causing fission):
% Based on E0 = 1.500000E+01 MeV

ANA_ALF                   (idx, [1:   2]) = [  1.75549E+01 0.00093 ];
IMP_ALF                   (idx, [1:   2]) = [  1.75394E+01 0.00054 ];

% EALF (Energy corresponding to average lethargy of neutrons causing fission):

ANA_EALF                  (idx, [1:   2]) = [  3.58863E-07 0.01653 ];
IMP_EALF                  (idx, [1:   2]) = [  3.62924E-07 0.00954 ];

% AFGE (Average energy of neutrons causing fission):

ANA_AFGE                  (idx, [1:   2]) = [  1.65174E-02 0.08970 ];
IMP_AFGE                  (idx, [1:   2]) = [  1.61617E-02 0.01229 ];

% Forward-weighted delayed neutron parameters:

FWD_ANA_BETA_ZERO         (idx, [1:  18]) = [  2.42174E-03 0.09647  1.73310E-04 0.34047  2.96571E-04 0.26280  4.67323E-04 0.18627  4.75011E-04 0.23920  7.59248E-04 0.15173  1.16889E-04 0.46163  9.32662E-05 0.42973  4.01238E-05 0.70264 ];
FWD_ANA_LAMBDA            (idx, [1:  18]) = [  2.80129E-01 0.19060  1.99467E-03 0.32733  7.35584E-03 0.24101  1.78602E-02 0.16788  4.25734E-02 0.20825  1.63782E-01 0.12663  6.66488E-02 0.42857  1.63478E-01 0.42857  1.42184E-01 0.69985 ];

% Beta-eff using Meulekamp's method:

ADJ_MEULEKAMP_BETA_EFF    (idx, [1:  18]) = [  2.57606E-03 0.12501  2.01319E-04 0.50811  3.49938E-04 0.34587  3.86107E-04 0.26764  3.34605E-04 0.37092  9.64366E-04 0.21864  2.58993E-04 0.54010  4.62060E-05 0.69779  3.45223E-05 0.70761 ];
ADJ_MEULEKAMP_LAMBDA      (idx, [1:  18]) = [  3.03367E-01 0.25916  1.24667E-02 0.0E+00  2.82917E-02 0.0E+00  4.25244E-02 0.0E+00  1.33042E-01 0.0E+00  2.92467E-01 2.7E-09  6.66488E-01 0.0E+00  1.63478E+00 5.9E-09  3.55460E+00 1.5E-08 ];

% Adjoint weighted time constants using Nauchi's method:

ADJ_NAUCHI_GEN_TIME       (idx, [1:   6]) = [  3.55996E-04 0.01518  3.56168E-04 0.01518  1.83993E-04 0.21484 ];
ADJ_NAUCHI_LIFETIME       (idx, [1:   6]) = [  3.83516E-04 0.01488  3.83708E-04 0.01490  1.95912E-04 0.21159 ];
ADJ_NAUCHI_BETA_EFF       (idx, [1:  18]) = [  2.66131E-03 0.13870  7.69360E-05 0.70009  4.39537E-04 0.34651  6.36377E-04 0.25502  4.64960E-04 0.38681  7.40134E-04 0.26506  2.02039E-04 0.49389  6.03015E-05 1.00000  4.10256E-05 1.00000 ];
ADJ_NAUCHI_LAMBDA         (idx, [1:  18]) = [  3.24440E-01 0.34033  1.24667E-02 0.0E+00  2.82917E-02 0.0E+00  4.25244E-02 0.0E+00  1.33042E-01 5.7E-09  2.92467E-01 3.9E-09  6.66488E-01 0.0E+00  1.63478E+00 0.0E+00  3.55460E+00 0.0E+00 ];

% Adjoint weighted time constants using IFP:

ADJ_IFP_GEN_TIME          (idx, [1:   6]) = [  3.15719E-04 0.05446  3.15663E-04 0.05433  4.67945E-05 0.48372 ];
ADJ_IFP_LIFETIME          (idx, [1:   6]) = [  3.41600E-04 0.05513  3.41531E-04 0.05500  5.14609E-05 0.48413 ];
ADJ_IFP_IMP_BETA_EFF      (idx, [1:  18]) = [  3.61261E-03 0.37357  0.00000E+00 0.0E+00  1.14752E-03 0.72167  0.00000E+00 0.0E+00  1.34888E-03 0.70330  3.07067E-04 1.00000  8.09152E-04 0.70112  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
ADJ_IFP_IMP_LAMBDA        (idx, [1:  18]) = [  2.77073E-01 0.38123  0.00000E+00 0.0E+00  2.82917E-02 9.1E-09  0.00000E+00 0.0E+00  1.33042E-01 0.0E+00  2.92467E-01 0.0E+00  6.66488E-01 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
ADJ_IFP_ANA_BETA_EFF      (idx, [1:  18]) = [  3.65022E-03 0.37087  0.00000E+00 0.0E+00  1.04391E-03 0.72205  0.00000E+00 0.0E+00  1.28973E-03 0.70632  3.30579E-04 1.00000  9.85999E-04 0.71076  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
ADJ_IFP_ANA_LAMBDA        (idx, [1:  18]) = [  2.74108E-01 0.38539  0.00000E+00 0.0E+00  2.82917E-02 9.1E-09  0.00000E+00 0.0E+00  1.33042E-01 0.0E+00  2.92467E-01 0.0E+00  6.66488E-01 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
ADJ_IFP_ROSSI_ALPHA       (idx, [1:   2]) = [ -1.19831E+01 0.36147 ];

% Adjoint weighted time constants using perturbation technique:

ADJ_PERT_GEN_TIME         (idx, [1:   2]) = [  3.49877E-04 0.00673 ];
ADJ_PERT_LIFETIME         (idx, [1:   2]) = [  3.76867E-04 0.00530 ];
ADJ_PERT_BETA_EFF         (idx, [1:   2]) = [  2.04622E-03 0.08293 ];
ADJ_PERT_ROSSI_ALPHA      (idx, [1:   2]) = [ -5.83443E+00 0.08205 ];

% Inverse neutron speed :

ANA_INV_SPD               (idx, [1:   2]) = [  9.15489E-07 0.00516 ];

% Analog slowing-down and thermal neutron lifetime (total/prompt/delayed):

ANA_SLOW_TIME             (idx, [1:   6]) = [  3.06253E-05 0.00187  3.06267E-05 0.00186  2.49697E-05 0.08146 ];
ANA_THERM_TIME            (idx, [1:   6]) = [  5.42321E-04 0.00863  5.42702E-04 0.00862  3.33792E-04 0.13419 ];
ANA_THERM_FRAC            (idx, [1:   6]) = [  6.07140E-01 0.00383  6.07001E-01 0.00380  8.43142E-01 0.17493 ];
ANA_DELAYED_EMTIME        (idx, [1:   2]) = [  1.51224E+01 0.14960 ];
ANA_MEAN_NCOL             (idx, [1:   4]) = [  1.53742E+02 0.00458  1.67792E+02 0.00571 ];

% Group constant generation:

GC_UNIVERSE_NAME          (idx, [1:  1])  = '0' ;

% Micro- and macro-group structures:

MICRO_NG                  (idx, 1)        = 70 ;
MICRO_E                   (idx, [1:  71]) = [  1.00000E-11  5.00000E-09  1.00000E-08  1.50000E-08  2.00000E-08  2.50000E-08  3.00000E-08  3.50000E-08  4.20000E-08  5.00000E-08  5.80000E-08  6.70000E-08  8.00000E-08  1.00000E-07  1.40000E-07  1.80000E-07  2.20000E-07  2.50000E-07  2.80000E-07  3.00000E-07  3.20000E-07  3.50000E-07  4.00000E-07  5.00000E-07  6.25000E-07  7.80000E-07  8.50000E-07  9.10000E-07  9.50000E-07  9.72000E-07  9.96000E-07  1.02000E-06  1.04500E-06  1.07100E-06  1.09700E-06  1.12300E-06  1.15000E-06  1.30000E-06  1.50000E-06  1.85500E-06  2.10000E-06  2.60000E-06  3.30000E-06  4.00000E-06  9.87700E-06  1.59680E-05  2.77000E-05  4.80520E-05  7.55014E-05  1.48728E-04  3.67262E-04  9.06898E-04  1.42510E-03  2.23945E-03  3.51910E-03  5.50000E-03  9.11800E-03  1.50300E-02  2.47800E-02  4.08500E-02  6.74300E-02  1.11000E-01  1.83000E-01  3.02500E-01  5.00000E-01  8.21000E-01  1.35300E+00  2.23100E+00  3.67900E+00  6.06550E+00  2.00000E+01 ];

MACRO_NG                  (idx, 1)        = 2 ;
MACRO_E                   (idx, [1:   3]) = [  1.00000E+37  6.25000E-07  0.00000E+00 ];

% Micro-group spectrum:

INF_MICRO_FLX             (idx, [1: 140]) = [  8.41806E+03 0.07267  3.96618E+04 0.00117  9.11116E+04 0.00147  1.68354E+05 0.00329  1.85778E+05 0.00508  1.86004E+05 0.00382  1.56021E+05 0.00652  1.35574E+05 0.00567  1.55520E+05 0.00205  1.53192E+05 0.00154  1.58780E+05 0.00697  1.56401E+05 0.00313  1.62513E+05 0.00442  1.58626E+05 0.00454  1.58187E+05 0.00703  1.38477E+05 0.00031  1.38628E+05 0.00303  1.37001E+05 3.2E-05  1.34822E+05 0.00171  2.64830E+05 0.00199  2.52128E+05 0.00233  1.80859E+05 0.00527  1.14650E+05 0.00407  1.39365E+05 0.00533  1.26592E+05 0.00043  1.08289E+05 0.00831  2.02853E+05 0.00153  4.38385E+04 0.00478  5.43286E+04 0.00787  4.83023E+04 0.00763  2.80267E+04 0.00183  4.78271E+04 0.00945  3.27656E+04 0.01796  2.88809E+04 0.00400  5.52826E+03 0.00635  5.70676E+03 0.02345  5.83135E+03 0.02086  5.97564E+03 0.01299  6.01770E+03 0.00039  5.99153E+03 0.03667  6.25228E+03 0.01703  5.71021E+03 0.03287  1.10182E+04 0.00984  1.79933E+04 0.00464  2.39263E+04 0.01350  7.44978E+04 0.00223  1.08249E+05 0.01402  1.66959E+05 0.01072  1.34373E+05 0.00560  1.05580E+05 0.00878  8.38914E+04 0.00707  9.53433E+04 0.00364  1.69314E+05 0.01055  2.04637E+05 0.00018  3.36024E+05 0.00379  4.10110E+05 0.00025  4.69251E+05 0.00121  2.43147E+05 0.00097  1.54693E+05 0.00102  1.00634E+05 0.00322  8.59448E+04 0.00483  8.04010E+04 0.00669  6.18564E+04 0.01402  4.13950E+04 0.01440  3.45231E+04 0.00783  3.20708E+04 0.01246  2.61662E+04 0.00966  1.68861E+04 0.02619  1.11297E+04 0.01674  3.48739E+03 0.01402 ];

% Integral parameters:

INF_KINF                  (idx, [1:   2]) = [  1.08416E+00 0.00550 ];

% Flux spectra in infinite geometry:

INF_FLX                   (idx, [1:   4]) = [  3.66694E+22 0.00548  2.60482E+22 0.00366 ];
INF_FISS_FLX              (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Reaction cross sections:

INF_TOT                   (idx, [1:   4]) = [  3.79946E-01 0.00099  4.34989E-01 0.00039 ];
INF_CAPT                  (idx, [1:   4]) = [  1.28998E-03 0.00895  1.68698E-03 0.01062 ];
INF_ABS                   (idx, [1:   4]) = [  1.79036E-03 0.01131  3.69183E-03 0.01110 ];
INF_FISS                  (idx, [1:   4]) = [  5.00381E-04 0.01739  2.00486E-03 0.01151 ];
INF_NSF                   (idx, [1:   4]) = [  1.24502E-03 0.01739  4.98750E-03 0.01151 ];
INF_NUBAR                 (idx, [1:   4]) = [  2.48814E+00 3.7E-06  2.48771E+00 0.0E+00 ];
INF_KAPPA                 (idx, [1:   4]) = [  1.99237E+02 1.6E-06  1.99273E+02 0.0E+00 ];
INF_INVV                  (idx, [1:   4]) = [  1.02385E-07 0.00293  2.06235E-06 0.00122 ];

% Total scattering cross sections:

INF_SCATT0                (idx, [1:   4]) = [  3.78154E-01 0.00107  4.31279E-01 0.00047 ];
INF_SCATT1                (idx, [1:   4]) = [  2.41551E-02 0.00203  1.17329E-02 0.02393 ];
INF_SCATT2                (idx, [1:   4]) = [  2.65106E-03 0.00282 -5.70397E-03 0.00782 ];
INF_SCATT3                (idx, [1:   4]) = [  4.63149E-04 0.13446 -5.00840E-03 0.00722 ];
INF_SCATT4                (idx, [1:   4]) = [ -1.95918E-04 0.26777 -5.85729E-03 0.00250 ];
INF_SCATT5                (idx, [1:   4]) = [  1.34492E-04 0.37807 -3.47226E-03 0.00794 ];
INF_SCATT6                (idx, [1:   4]) = [ -4.40485E-04 0.01073 -5.73188E-03 0.00296 ];
INF_SCATT7                (idx, [1:   4]) = [  1.30983E-04 0.18147 -6.95125E-04 0.08230 ];

% Total scattering production cross sections:

INF_SCATTP0               (idx, [1:   4]) = [  3.78165E-01 0.00107  4.31279E-01 0.00047 ];
INF_SCATTP1               (idx, [1:   4]) = [  2.41582E-02 0.00204  1.17329E-02 0.02393 ];
INF_SCATTP2               (idx, [1:   4]) = [  2.65168E-03 0.00298 -5.70397E-03 0.00782 ];
INF_SCATTP3               (idx, [1:   4]) = [  4.63595E-04 0.13673 -5.00840E-03 0.00722 ];
INF_SCATTP4               (idx, [1:   4]) = [ -1.95648E-04 0.26740 -5.85729E-03 0.00250 ];
INF_SCATTP5               (idx, [1:   4]) = [  1.34723E-04 0.37592 -3.47226E-03 0.00794 ];
INF_SCATTP6               (idx, [1:   4]) = [ -4.40126E-04 0.01131 -5.73188E-03 0.00296 ];
INF_SCATTP7               (idx, [1:   4]) = [  1.31276E-04 0.17570 -6.95125E-04 0.08230 ];

% Diffusion parameters:

INF_TRANSPXS              (idx, [1:   4]) = [  3.29660E-01 0.00026  4.21480E-01 0.00099 ];
INF_DIFFCOEF              (idx, [1:   4]) = [  1.01114E+00 0.00026  7.90864E-01 0.00099 ];

% Reduced absoption and removal:

INF_RABSXS                (idx, [1:   4]) = [  1.77934E-03 0.01100  3.69183E-03 0.01110 ];
INF_REMXS                 (idx, [1:   4]) = [  6.01024E-03 0.00022  5.85840E-03 0.00594 ];

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

INF_S0                    (idx, [1:   8]) = [  3.73936E-01 0.00101  4.21825E-03 0.00660  2.14854E-03 0.00113  4.29130E-01 0.00048 ];
INF_S1                    (idx, [1:   8]) = [  2.51383E-02 0.00194 -9.83243E-04 0.00035 -2.38847E-04 0.01573  1.19718E-02 0.02376 ];
INF_S2                    (idx, [1:   8]) = [  2.81916E-03 0.00030 -1.68103E-04 0.03945 -1.50814E-04 0.03098 -5.55316E-03 0.00888 ];
INF_S3                    (idx, [1:   8]) = [  5.08516E-04 0.14261 -4.53667E-05 0.22590 -4.85086E-05 0.32079 -4.95989E-03 0.01043 ];
INF_S4                    (idx, [1:   8]) = [ -1.66497E-04 0.33969 -2.94208E-05 0.13924 -3.24298E-05 0.07580 -5.82486E-03 0.00294 ];
INF_S5                    (idx, [1:   8]) = [  1.33206E-04 0.35389  1.28590E-06 1.00000 -7.13224E-06 0.27400 -3.46513E-03 0.00852 ];
INF_S6                    (idx, [1:   8]) = [ -4.12087E-04 0.01166 -2.83981E-05 0.00287 -2.15490E-05 0.18560 -5.71033E-03 0.00227 ];
INF_S7                    (idx, [1:   8]) = [  1.10626E-04 0.19761  2.03565E-05 0.09377  6.14086E-06 1.00000 -7.01266E-04 0.09582 ];

% Scattering production matrixes:

INF_SP0                   (idx, [1:   8]) = [  3.73947E-01 0.00101  4.21825E-03 0.00660  2.14854E-03 0.00113  4.29130E-01 0.00048 ];
INF_SP1                   (idx, [1:   8]) = [  2.51415E-02 0.00195 -9.83243E-04 0.00035 -2.38847E-04 0.01573  1.19718E-02 0.02376 ];
INF_SP2                   (idx, [1:   8]) = [  2.81978E-03 0.00045 -1.68103E-04 0.03945 -1.50814E-04 0.03098 -5.55316E-03 0.00888 ];
INF_SP3                   (idx, [1:   8]) = [  5.08962E-04 0.14468 -4.53667E-05 0.22590 -4.85086E-05 0.32079 -4.95989E-03 0.01043 ];
INF_SP4                   (idx, [1:   8]) = [ -1.66227E-04 0.33937 -2.94208E-05 0.13924 -3.24298E-05 0.07580 -5.82486E-03 0.00294 ];
INF_SP5                   (idx, [1:   8]) = [  1.33437E-04 0.35176  1.28590E-06 1.00000 -7.13224E-06 0.27400 -3.46513E-03 0.00852 ];
INF_SP6                   (idx, [1:   8]) = [ -4.11728E-04 0.01229 -2.83981E-05 0.00287 -2.15490E-05 0.18560 -5.71033E-03 0.00227 ];
INF_SP7                   (idx, [1:   8]) = [  1.10919E-04 0.19074  2.03565E-05 0.09377  6.14086E-06 1.00000 -7.01266E-04 0.09582 ];

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

CMM_TRANSPXS              (idx, [1:   4]) = [  3.26049E-01 0.00270  5.63333E-01 0.05622 ];
CMM_TRANSPXS_X            (idx, [1:   4]) = [  3.24518E-01 0.00582  5.63619E-01 0.07021 ];
CMM_TRANSPXS_Y            (idx, [1:   4]) = [  3.27461E-01 0.00272  5.67013E-01 0.04361 ];
CMM_TRANSPXS_Z            (idx, [1:   4]) = [  3.26188E-01 0.00046  5.59618E-01 0.05473 ];
CMM_DIFFCOEF              (idx, [1:   4]) = [  1.02235E+00 0.00270  5.93592E-01 0.05622 ];
CMM_DIFFCOEF_X            (idx, [1:   4]) = [  1.02720E+00 0.00582  5.94346E-01 0.07021 ];
CMM_DIFFCOEF_Y            (idx, [1:   4]) = [  1.01794E+00 0.00272  5.88996E-01 0.04361 ];
CMM_DIFFCOEF_Z            (idx, [1:   4]) = [  1.02191E+00 0.00046  5.97434E-01 0.05473 ];

% Delayed neutron parameters (Meulekamp method):

BETA_EFF                  (idx, [1:  18]) = [  2.57606E-03 0.12501  2.01319E-04 0.50811  3.49938E-04 0.34587  3.86107E-04 0.26764  3.34605E-04 0.37092  9.64366E-04 0.21864  2.58993E-04 0.54010  4.62060E-05 0.69779  3.45223E-05 0.70761 ];
LAMBDA                    (idx, [1:  18]) = [  3.03367E-01 0.25916  1.24667E-02 0.0E+00  2.82917E-02 0.0E+00  4.25244E-02 0.0E+00  1.33042E-01 0.0E+00  2.92467E-01 2.7E-09  6.66488E-01 0.0E+00  1.63478E+00 5.9E-09  3.55460E+00 1.5E-08 ];


% Increase counter:

if (exist('idx', 'var'));
  idx = idx + 1;
else;
  idx = 1;
end;

% Version, title and date:

VERSION                   (idx, [1: 14])  = 'Serpent 2.1.30' ;
COMPILE_DATE              (idx, [1: 20])  = 'Feb 14 2018 21:59:44' ;
DEBUG                     (idx, 1)        = 0 ;
TITLE                     (idx, [1: 52])  = 'themperature coefficient of reactivity 900K for both' ;
CONFIDENTIAL_DATA         (idx, 1)        = 0 ;
INPUT_FILE_NAME           (idx, [1:  4])  = 'core' ;
WORKING_DIRECTORY         (idx, [1: 62])  = '/home/andrei2/Desktop/git/MScThesis-MSBR/serpent/thermal_coeff' ;
HOSTNAME                  (idx, [1: 28])  = 'andrei2-Precision-Tower-3420' ;
CPU_TYPE                  (idx, [1: 41])  = 'Intel(R) Xeon(R) CPU E3-1225 v5 @ 3.30GHz' ;
CPU_MHZ                   (idx, 1)        = 186.0 ;
START_DATE                (idx, [1: 24])  = 'Wed Mar 28 10:26:06 2018' ;
COMPLETE_DATE             (idx, [1: 24])  = 'Wed Mar 28 10:27:17 2018' ;

% Run parameters:

POP                       (idx, 1)        = 1000 ;
CYCLES                    (idx, 1)        = 50 ;
SKIP                      (idx, 1)        = 10 ;
BATCH_INTERVAL            (idx, 1)        = 1 ;
SRC_NORM_MODE             (idx, 1)        = 2 ;
SEED                      (idx, 1)        = 1522250766 ;
UFS_MODE                  (idx, 1)        = 0 ;
UFS_ORDER                 (idx, 1)        = 1.00000;
NEUTRON_TRANSPORT_MODE    (idx, 1)        = 1 ;
PHOTON_TRANSPORT_MODE     (idx, 1)        = 0 ;
GROUP_CONSTANT_GENERATION (idx, 1)        = 1 ;
B1_CALCULATION            (idx, [1:  3])  = [ 0 0 0 ];
B1_BURNUP_CORRECTION      (idx, 1)        = 0 ;
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
OMP_HISTORY_PROFILE       (idx, [1:   4]) = [  1.22418E+00  8.72761E-01  9.33751E-01  9.69306E-01  ];
SHARE_BUF_ARRAY           (idx, 1)        = 0 ;
SHARE_RES2_ARRAY          (idx, 1)        = 1 ;

% File paths:

XS_DATA_FILE_PATH         (idx, [1: 55])  = '/home/andrei2/serpent/xsdata/jeff312/sss_jeff312.xsdata' ;
DECAY_DATA_FILE_PATH      (idx, [1: 51])  = '/home/andrei2/serpent/xsdata/jeff312/sss_jeff33.dec' ;
SFY_DATA_FILE_PATH        (idx, [1: 51])  = '/home/andrei2/serpent/xsdata/jeff312/sss_jeff33.nfy' ;
NFY_DATA_FILE_PATH        (idx, [1: 51])  = '/home/andrei2/serpent/xsdata/jeff312/sss_jeff33.nfy' ;
BRA_DATA_FILE_PATH        (idx, [1:  3])  = 'N/A' ;

% Collision and reaction sampling (neutrons/photons):

MIN_MACROXS               (idx, [1:   4]) = [  5.00000E-02 0.0E+00  0.00000E+00 0.0E+00 ];
DT_THRESH                 (idx, [1:  2])  = [  9.00000E-01  9.00000E-01 ];
ST_FRAC                   (idx, [1:   4]) = [  1.28033E-03 0.01136  0.00000E+00 0.0E+00 ];
DT_FRAC                   (idx, [1:   4]) = [  9.98720E-01 1.5E-05  0.00000E+00 0.0E+00 ];
DT_EFF                    (idx, [1:   4]) = [  9.11017E-01 0.00035  0.00000E+00 0.0E+00 ];
REA_SAMPLING_EFF          (idx, [1:   4]) = [  1.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
REA_SAMPLING_FAIL         (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
TOT_COL_EFF               (idx, [1:   4]) = [  9.11092E-01 0.00035  0.00000E+00 0.0E+00 ];
AVG_TRACKING_LOOPS        (idx, [1:   8]) = [  2.38194E+00 0.00252  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
AVG_TRACKS                (idx, [1:   4]) = [  1.52788E+02 0.00427  0.00000E+00 0.0E+00 ];
AVG_REAL_COL              (idx, [1:   4]) = [  1.52776E+02 0.00426  0.00000E+00 0.0E+00 ];
AVG_VIRT_COL              (idx, [1:   4]) = [  1.49000E+01 0.00283  0.00000E+00 0.0E+00 ];
AVG_SURF_CROSS            (idx, [1:   4]) = [  8.54277E-02 0.01643  0.00000E+00 0.0E+00 ];
LOST_PARTICLES            (idx, 1)        = 0 ;

% Run statistics:

CYCLE_IDX                 (idx, 1)        = 50 ;
SOURCE_POPULATION         (idx, 1)        = 50087 ;
MEAN_POP_SIZE             (idx, [1:  2])  = [  1.00174E+03 0.00827 ];
MEAN_POP_WGT              (idx, [1:  2])  = [  1.00174E+03 0.00827 ];
SIMULATION_COMPLETED      (idx, 1)        = 1 ;

% Running times:

TOT_CPU_TIME              (idx, 1)        =  2.02578E+00 ;
RUNNING_TIME              (idx, 1)        =  1.16955E+00 ;
INIT_TIME                 (idx, [1:  2])  = [  4.68367E-01  4.68367E-01 ];
PROCESS_TIME              (idx, [1:  2])  = [  1.09667E-02  5.06667E-03 ];
TRANSPORT_CYCLE_TIME      (idx, [1:  3])  = [  5.97200E-01  2.19917E-01  1.82017E-01 ];
BURNUP_CYCLE_TIME         (idx, [1:  2])  = [  2.20500E-02  1.12667E-02 ];
BATEMAN_SOLUTION_TIME     (idx, [1:  2])  = [  5.50000E-04  5.50000E-04 ];
MPI_OVERHEAD_TIME         (idx, [1:  2])  = [  0.00000E+00  0.00000E+00 ];
ESTIMATED_RUNNING_TIME    (idx, [1:  2])  = [  1.16953E+00  1.16953E+00 ];
CPU_USAGE                 (idx, 1)        = 1.73211 ;
TRANSPORT_CPU_USAGE       (idx, [1:   2]) = [  2.66512E+00 0.02209 ];
OMP_PARALLEL_FRAC         (idx, 1)        =  5.07603E-01 ;

% Memory usage:

AVAIL_MEM                 (idx, 1)        = 32069.96 ;
ALLOC_MEMSIZE             (idx, 1)        = 5614.26;
MEMSIZE                   (idx, 1)        = 5547.15;
XS_MEMSIZE                (idx, 1)        = 5492.80;
MAT_MEMSIZE               (idx, 1)        = 35.51;
RES_MEMSIZE               (idx, 1)        = 0.83;
MISC_MEMSIZE              (idx, 1)        = 18.01;
UNKNOWN_MEMSIZE           (idx, 1)        = 0.00;
UNUSED_MEMSIZE            (idx, 1)        = 67.11;

% Geometry parameters:

TOT_CELLS                 (idx, 1)        = 329 ;
UNION_CELLS               (idx, 1)        = 0 ;

% Neutron energy grid:

NEUTRON_ERG_TOL           (idx, 1)        =  5.00000E-05 ;
NEUTRON_ERG_NE            (idx, 1)        = 305328 ;
NEUTRON_EMIN              (idx, 1)        =  1.00000E-09 ;
NEUTRON_EMAX              (idx, 1)        =  1.50000E+01 ;

% Unresolved resonance probability table sampling:

URES_DILU_CUT             (idx, 1)        =  1.00000E-09 ;
URES_EMIN                 (idx, 1)        =  1.00000E+37 ;
URES_EMAX                 (idx, 1)        = -1.00000E+37 ;
URES_AVAIL                (idx, 1)        = 125 ;
URES_USED                 (idx, 1)        = 0 ;

% Nuclides and reaction channels:

TOT_NUCLIDES              (idx, 1)        = 1161 ;
TOT_TRANSPORT_NUCLIDES    (idx, 1)        = 240 ;
TOT_DOSIMETRY_NUCLIDES    (idx, 1)        = 0 ;
TOT_DECAY_NUCLIDES        (idx, 1)        = 921 ;
TOT_PHOTON_NUCLIDES       (idx, 1)        = 0 ;
TOT_REA_CHANNELS          (idx, 1)        = 5162 ;
TOT_TRANSMU_REA           (idx, 1)        = 1692 ;

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

TOT_ACTIVITY              (idx, 1)        =  3.71394E+20 ;
TOT_DECAY_HEAT            (idx, 1)        =  1.13874E+08 ;
TOT_SF_RATE               (idx, 1)        =  3.98669E+00 ;
ACTINIDE_ACTIVITY         (idx, 1)        =  8.48537E+19 ;
ACTINIDE_DECAY_HEAT       (idx, 1)        =  6.03689E+06 ;
FISSION_PRODUCT_ACTIVITY  (idx, 1)        =  2.83784E+20 ;
FISSION_PRODUCT_DECAY_HEAT(idx, 1)        =  1.04567E+08 ;
INHALATION_TOXICITY       (idx, 1)        =  6.76847E+10 ;
INGESTION_TOXICITY        (idx, 1)        =  8.28661E+10 ;
ACTINIDE_INH_TOX          (idx, 1)        =  2.30355E+10 ;
ACTINIDE_ING_TOX          (idx, 1)        =  5.23412E+09 ;
FISSION_PRODUCT_INH_TOX   (idx, 1)        =  4.46492E+10 ;
FISSION_PRODUCT_ING_TOX   (idx, 1)        =  7.76319E+10 ;
SR90_ACTIVITY             (idx, 1)        =  9.24393E+14 ;
TE132_ACTIVITY            (idx, 1)        =  1.53767E+18 ;
I131_ACTIVITY             (idx, 1)        =  4.80108E+17 ;
I132_ACTIVITY             (idx, 1)        =  1.62995E+18 ;
CS134_ACTIVITY            (idx, 1)        =  2.76380E+12 ;
CS137_ACTIVITY            (idx, 1)        =  8.35736E+14 ;
PHOTON_DECAY_SOURCE       (idx, 1)        =  3.52696E+20 ;
NEUTRON_DECAY_SOURCE      (idx, 1)        =  4.75043E+17 ;
ALPHA_DECAY_SOURCE        (idx, 1)        =  1.86289E+18 ;
ELECTRON_DECAY_SOURCE     (idx, 1)        =  5.10210E+20 ;

% Normalization coefficient:

NORM_COEF                 (idx, [1:   4]) = [  1.72633E+17 0.00553  0.00000E+00 0.0E+00 ];

% Parameters for burnup calculation:

BURN_MATERIALS            (idx, 1)        = 1 ;
BURN_MODE                 (idx, 1)        = 2 ;
BURN_STEP                 (idx, 1)        = 1 ;
BURNUP                     (idx, [1:  2])  = [  8.42515E-01  8.43463E-01 ];
BURN_DAYS                 (idx, 1)        =  3.00000E+00 ;

% Analog reaction rate estimators:

CONVERSION_RATIO          (idx, [1:   2]) = [  1.01731E+00 0.00944 ];
TH232_FISS                (idx, [1:   4]) = [  2.76616E+17 0.08881  3.92722E-03 0.08893 ];
U233_FISS                 (idx, [1:   4]) = [  7.01628E+19 0.00717  9.96073E-01 0.00035 ];
TH232_CAPT                (idx, [1:   4]) = [  7.97911E+19 0.00840  7.93244E-01 0.00349 ];
U233_CAPT                 (idx, [1:   4]) = [  8.52872E+18 0.02014  8.47915E-02 0.01900 ];
XE135_CAPT                (idx, [1:   4]) = [  3.50967E+18 0.03449  3.51086E-02 0.03726 ];
SM149_CAPT                (idx, [1:   4]) = [  2.93310E+17 0.11623  2.92821E-03 0.11559 ];

% Neutron balance (particles/weight):

BALA_SRC_NEUTRON_SRC     (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_SRC_NEUTRON_FISS    (idx, [1:  2])  = [ 50087 5.00000E+04 ];
BALA_SRC_NEUTRON_NXN     (idx, [1:  2])  = [ 0 1.41525E+02 ];
BALA_SRC_NEUTRON_VR      (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_SRC_NEUTRON_TOT     (idx, [1:  2])  = [ 50087 5.01415E+04 ];

BALA_LOSS_NEUTRON_CAPT    (idx, [1:  2])  = [ 29085 2.91242E+04 ];
BALA_LOSS_NEUTRON_FISS    (idx, [1:  2])  = [ 20395 2.04073E+04 ];
BALA_LOSS_NEUTRON_LEAK    (idx, [1:  2])  = [ 607 6.10043E+02 ];
BALA_LOSS_NEUTRON_CUT     (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_LOSS_NEUTRON_ERR     (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_LOSS_NEUTRON_TOT     (idx, [1:  2])  = [ 50087 5.01415E+04 ];

BALA_NEUTRON_DIFF         (idx, [1:  2])  = [ 0 7.27596E-12 ];

% Normalized total reaction rates (neutrons):

TOT_POWER                 (idx, [1:   6]) = [  2.25000E+09 0.0E+00  2.25000E+09 0.0E+00  0.00000E+00 0.0E+00 ];
TOT_POWDENS               (idx, [1:   6]) = [  2.80838E-01 7.3E-09  2.80838E-01 7.3E-09  0.00000E+00 0.0E+00 ];
TOT_GENRATE               (idx, [1:   6]) = [  1.75332E+20 5.0E-06  1.75332E+20 5.0E-06  0.00000E+00 0.0E+00 ];
TOT_FISSRATE              (idx, [1:   6]) = [  7.04765E+19 5.8E-07  7.04765E+19 5.8E-07  0.00000E+00 0.0E+00 ];
TOT_CAPTRATE              (idx, [1:   6]) = [  1.00754E+20 0.00383  9.69280E+19 0.00391  3.82616E+18 0.01092 ];
TOT_ABSRATE               (idx, [1:   6]) = [  1.71231E+20 0.00225  1.67404E+20 0.00226  3.82616E+18 0.01092 ];
TOT_SRCRATE               (idx, [1:   6]) = [  1.72633E+20 0.00553  1.72633E+20 0.00553  0.00000E+00 0.0E+00 ];
TOT_FLUX                  (idx, [1:   6]) = [  6.56606E+22 0.00566  1.02697E+22 0.00561  5.53909E+22 0.00601 ];
TOT_PHOTON_PRODRATE       (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
TOT_LEAKRATE              (idx, [1:   2]) = [  2.11467E+18 0.05202 ];
ALBEDO_LEAKRATE           (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
TOT_LOSSRATE              (idx, [1:   2]) = [  1.73345E+20 0.00254 ];
TOT_CUTRATE               (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
TOT_RR                    (idx, [1:   2]) = [  2.64378E+22 0.00587 ];
INI_FMASS                 (idx, 1)        =  8.01172E+03 ;
TOT_FMASS                 (idx, 1)        =  8.00468E+03 ;
INI_BURN_FMASS            (idx, 1)        =  8.01172E+03 ;
TOT_BURN_FMASS            (idx, 1)        =  8.00468E+03 ;

% Six-factor formula:

SIX_FF_ETA                (idx, [1:   2]) = [  1.30812E+00 0.00616 ];
SIX_FF_F                  (idx, [1:   2]) = [  9.67526E-01 0.00115 ];
SIX_FF_P                  (idx, [1:   2]) = [  6.00030E-01 0.00460 ];
SIX_FF_EPSILON            (idx, [1:   2]) = [  1.35515E+00 0.00429 ];
SIX_FF_LF                 (idx, [1:   2]) = [  9.99903E-01 4.2E-05 ];
SIX_FF_LT                 (idx, [1:   2]) = [  9.87895E-01 0.00061 ];
SIX_FF_KINF               (idx, [1:   2]) = [  1.02792E+00 0.00557 ];
SIX_FF_KEFF               (idx, [1:   2]) = [  1.01539E+00 0.00566 ];

% Fission neutron and energy production:

NUBAR                     (idx, [1:   2]) = [  2.48781E+00 4.8E-06 ];
FISSE                     (idx, [1:   2]) = [  1.99264E+02 5.8E-07 ];

% Criticality eigenvalues:

ANA_KEFF                  (idx, [1:   6]) = [  1.01329E+00 0.00622  1.01214E+00 0.00568  3.25462E-03 0.11487 ];
IMP_KEFF                  (idx, [1:   2]) = [  1.01463E+00 0.00252 ];
COL_KEFF                  (idx, [1:   2]) = [  1.01718E+00 0.00561 ];
ABS_KEFF                  (idx, [1:   2]) = [  1.01463E+00 0.00252 ];
ABS_KINF                  (idx, [1:   2]) = [  1.02713E+00 0.00225 ];
GEOM_ALBEDO               (idx, [1:   6]) = [  1.00000E+00 0.0E+00  1.00000E+00 0.0E+00  1.00000E+00 0.0E+00 ];

% ALF (Average lethargy of neutrons causing fission):
% Based on E0 = 1.500000E+01 MeV

ANA_ALF                   (idx, [1:   2]) = [  1.75276E+01 0.00132 ];
IMP_ALF                   (idx, [1:   2]) = [  1.75358E+01 0.00058 ];

% EALF (Energy corresponding to average lethargy of neutrons causing fission):

ANA_EALF                  (idx, [1:   2]) = [  3.71218E-07 0.02330 ];
IMP_EALF                  (idx, [1:   2]) = [  3.64314E-07 0.01020 ];

% AFGE (Average energy of neutrons causing fission):

ANA_AFGE                  (idx, [1:   2]) = [  1.64311E-02 0.07466 ];
IMP_AFGE                  (idx, [1:   2]) = [  1.68165E-02 0.01363 ];

% Forward-weighted delayed neutron parameters:

FWD_ANA_BETA_ZERO         (idx, [1:  18]) = [  2.60698E-03 0.07881  2.09187E-04 0.29866  5.71282E-04 0.18430  3.01760E-04 0.23877  5.01449E-04 0.19352  7.67104E-04 0.14747  3.96914E-05 0.70005  2.16508E-04 0.32659  0.00000E+00 0.0E+00 ];
FWD_ANA_LAMBDA            (idx, [1:  18]) = [  2.42430E-01 0.14552  2.49334E-03 0.28571  1.24483E-02 0.16116  1.19068E-02 0.22908  5.32168E-02 0.17496  1.63782E-01 0.12663  2.66595E-02 0.69985  2.94261E-01 0.30491  0.00000E+00 0.0E+00 ];

% Beta-eff using Meulekamp's method:

ADJ_MEULEKAMP_BETA_EFF    (idx, [1:  18]) = [  2.96096E-03 0.12522  2.06677E-04 0.46495  5.78893E-04 0.30174  4.43222E-04 0.38580  4.55577E-04 0.25429  8.63815E-04 0.20856  4.65868E-05 0.95132  3.66188E-04 0.38874  0.00000E+00 0.0E+00 ];
ADJ_MEULEKAMP_LAMBDA      (idx, [1:  18]) = [  3.21730E-01 0.17269  1.24667E-02 3.9E-09  2.82917E-02 0.0E+00  4.25244E-02 0.0E+00  1.33042E-01 0.0E+00  2.92467E-01 5.4E-09  6.66488E-01 0.0E+00  1.63478E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Adjoint weighted time constants using Nauchi's method:

ADJ_NAUCHI_GEN_TIME       (idx, [1:   6]) = [  3.71799E-04 0.01237  3.71801E-04 0.01236  2.70767E-04 0.27574 ];
ADJ_NAUCHI_LIFETIME       (idx, [1:   6]) = [  3.76451E-04 0.01258  3.76472E-04 0.01263  2.68824E-04 0.27249 ];
ADJ_NAUCHI_BETA_EFF       (idx, [1:  18]) = [  3.20193E-03 0.11419  1.96608E-04 0.49385  6.79513E-04 0.25413  3.47466E-04 0.36358  8.20779E-04 0.23610  8.92340E-04 0.21767  6.10998E-05 1.00000  2.04120E-04 0.49153  0.00000E+00 0.0E+00 ];
ADJ_NAUCHI_LAMBDA         (idx, [1:  18]) = [  2.80278E-01 0.24167  1.24667E-02 0.0E+00  2.82917E-02 0.0E+00  4.25244E-02 5.7E-09  1.33042E-01 0.0E+00  2.92467E-01 5.4E-09  6.66488E-01 0.0E+00  1.63478E+00 8.6E-09  0.00000E+00 0.0E+00 ];

% Adjoint weighted time constants using IFP:

ADJ_IFP_GEN_TIME          (idx, [1:   6]) = [  3.14325E-04 0.05762  3.14319E-04 0.05771  4.28761E-05 0.50734 ];
ADJ_IFP_LIFETIME          (idx, [1:   6]) = [  3.20392E-04 0.05834  3.20381E-04 0.05842  4.27381E-05 0.50021 ];
ADJ_IFP_IMP_BETA_EFF      (idx, [1:  18]) = [  2.16665E-03 0.45671  0.00000E+00 0.0E+00  3.68406E-04 1.00000  0.00000E+00 0.0E+00  1.15434E-03 0.76119  6.43905E-04 0.55727  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
ADJ_IFP_IMP_LAMBDA        (idx, [1:  18]) = [  2.09973E-01 0.16343  0.00000E+00 0.0E+00  2.82917E-02 0.0E+00  0.00000E+00 0.0E+00  1.33042E-01 0.0E+00  2.92467E-01 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
ADJ_IFP_ANA_BETA_EFF      (idx, [1:  18]) = [  2.39803E-03 0.42993  0.00000E+00 0.0E+00  4.40252E-04 1.00000  0.00000E+00 0.0E+00  1.27565E-03 0.70808  6.82123E-04 0.51609  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
ADJ_IFP_ANA_LAMBDA        (idx, [1:  18]) = [  2.09973E-01 0.16343  0.00000E+00 0.0E+00  2.82917E-02 0.0E+00  0.00000E+00 0.0E+00  1.33042E-01 0.0E+00  2.92467E-01 5.9E-09  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
ADJ_IFP_ROSSI_ALPHA       (idx, [1:   2]) = [ -7.30654E+00 0.47620 ];

% Adjoint weighted time constants using perturbation technique:

ADJ_PERT_GEN_TIME         (idx, [1:   2]) = [  3.63252E-04 0.00664 ];
ADJ_PERT_LIFETIME         (idx, [1:   2]) = [  3.67649E-04 0.00586 ];
ADJ_PERT_BETA_EFF         (idx, [1:   2]) = [  3.24972E-03 0.06348 ];
ADJ_PERT_ROSSI_ALPHA      (idx, [1:   2]) = [ -9.01864E+00 0.06527 ];

% Inverse neutron speed :

ANA_INV_SPD               (idx, [1:   2]) = [  9.05485E-07 0.00519 ];

% Analog slowing-down and thermal neutron lifetime (total/prompt/delayed):

ANA_SLOW_TIME             (idx, [1:   6]) = [  3.05495E-05 0.00191  3.05515E-05 0.00192  2.41421E-05 0.07816 ];
ANA_THERM_TIME            (idx, [1:   6]) = [  5.32230E-04 0.01080  5.32302E-04 0.01076  4.27568E-04 0.14925 ];
ANA_THERM_FRAC            (idx, [1:   6]) = [  6.08238E-01 0.00427  6.08242E-01 0.00429  7.80920E-01 0.17700 ];
ANA_DELAYED_EMTIME        (idx, [1:   2]) = [  1.99604E+01 0.15295 ];
ANA_MEAN_NCOL             (idx, [1:   4]) = [  1.52776E+02 0.00426  1.65363E+02 0.00470 ];

% Group constant generation:

GC_UNIVERSE_NAME          (idx, [1:  1])  = '0' ;

% Micro- and macro-group structures:

MICRO_NG                  (idx, 1)        = 70 ;
MICRO_E                   (idx, [1:  71]) = [  1.00000E-11  5.00000E-09  1.00000E-08  1.50000E-08  2.00000E-08  2.50000E-08  3.00000E-08  3.50000E-08  4.20000E-08  5.00000E-08  5.80000E-08  6.70000E-08  8.00000E-08  1.00000E-07  1.40000E-07  1.80000E-07  2.20000E-07  2.50000E-07  2.80000E-07  3.00000E-07  3.20000E-07  3.50000E-07  4.00000E-07  5.00000E-07  6.25000E-07  7.80000E-07  8.50000E-07  9.10000E-07  9.50000E-07  9.72000E-07  9.96000E-07  1.02000E-06  1.04500E-06  1.07100E-06  1.09700E-06  1.12300E-06  1.15000E-06  1.30000E-06  1.50000E-06  1.85500E-06  2.10000E-06  2.60000E-06  3.30000E-06  4.00000E-06  9.87700E-06  1.59680E-05  2.77000E-05  4.80520E-05  7.55014E-05  1.48728E-04  3.67262E-04  9.06898E-04  1.42510E-03  2.23945E-03  3.51910E-03  5.50000E-03  9.11800E-03  1.50300E-02  2.47800E-02  4.08500E-02  6.74300E-02  1.11000E-01  1.83000E-01  3.02500E-01  5.00000E-01  8.21000E-01  1.35300E+00  2.23100E+00  3.67900E+00  6.06550E+00  2.00000E+01 ];

MACRO_NG                  (idx, 1)        = 2 ;
MACRO_E                   (idx, [1:   3]) = [  1.00000E+37  6.25000E-07  0.00000E+00 ];

% Micro-group spectrum:

INF_MICRO_FLX             (idx, [1: 140]) = [  8.78610E+03 0.02631  4.05469E+04 0.00345  9.08009E+04 0.00860  1.68014E+05 0.00659  1.85160E+05 0.00469  1.86516E+05 0.00030  1.57421E+05 0.00553  1.36304E+05 0.00525  1.56149E+05 0.00302  1.53326E+05 0.00106  1.58398E+05 0.00299  1.57068E+05 0.00077  1.62355E+05 0.00229  1.58521E+05 0.00381  1.58825E+05 0.00241  1.39424E+05 0.00195  1.38760E+05 0.00206  1.37161E+05 0.00288  1.35589E+05 0.00054  2.65513E+05 0.00030  2.53104E+05 0.00047  1.80880E+05 0.00014  1.15093E+05 0.00091  1.40246E+05 0.00233  1.27382E+05 0.00253  1.08575E+05 0.00190  2.03293E+05 0.00423  4.39718E+04 0.00495  5.53419E+04 0.00714  4.87884E+04 0.00135  2.77127E+04 0.00272  4.80821E+04 0.00445  3.27873E+04 0.00869  2.87161E+04 0.00099  5.60617E+03 0.00568  5.57475E+03 0.01760  5.78088E+03 0.01651  5.86465E+03 0.02284  5.89341E+03 0.01377  5.81147E+03 0.00759  6.01079E+03 0.01443  5.65755E+03 0.00034  1.10340E+04 0.00124  1.78713E+04 0.00338  2.40076E+04 0.00326  7.37825E+04 0.00335  1.07824E+05 0.00294  1.63667E+05 0.00831  1.32689E+05 0.01353  1.04882E+05 0.01158  8.26936E+04 0.00708  9.36743E+04 0.01573  1.65436E+05 0.00966  2.01180E+05 0.01421  3.28034E+05 0.01332  4.02308E+05 0.01472  4.60412E+05 0.01272  2.40119E+05 0.01195  1.49704E+05 0.01229  9.83073E+04 0.01828  8.39401E+04 0.01295  7.96965E+04 0.00644  6.06417E+04 0.01999  4.10242E+04 0.01583  3.42512E+04 0.00836  3.02560E+04 0.02009  2.60852E+04 0.02335  1.62540E+04 0.00796  1.10803E+04 0.01043  3.07151E+03 0.02014 ];

% Integral parameters:

INF_KINF                  (idx, [1:   2]) = [  1.02764E+00 0.00286 ];

% Flux spectra in infinite geometry:

INF_FLX                   (idx, [1:   4]) = [  3.87777E+22 0.00396  2.69716E+22 0.00864 ];
INF_FISS_FLX              (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Reaction cross sections:

INF_TOT                   (idx, [1:   4]) = [  3.80191E-01 4.3E-05  4.34747E-01 0.00044 ];
INF_CAPT                  (idx, [1:   4]) = [  1.30947E-03 0.00034  1.87418E-03 0.01171 ];
INF_ABS                   (idx, [1:   4]) = [  1.77848E-03 0.00339  3.81712E-03 0.01207 ];
INF_FISS                  (idx, [1:   4]) = [  4.69004E-04 0.01188  1.94294E-03 0.01241 ];
INF_NSF                   (idx, [1:   4]) = [  1.16693E-03 0.01190  4.83345E-03 0.01241 ];
INF_NUBAR                 (idx, [1:   4]) = [  2.48811E+00 1.5E-05  2.48770E+00 1.5E-08 ];
INF_KAPPA                 (idx, [1:   4]) = [  1.99235E+02 8.2E-07  1.99273E+02 0.0E+00 ];
INF_INVV                  (idx, [1:   4]) = [  1.02125E-07 0.00303  2.05993E-06 0.00013 ];

% Total scattering cross sections:

INF_SCATT0                (idx, [1:   4]) = [  3.78407E-01 4.7E-06  4.30958E-01 0.00051 ];
INF_SCATT1                (idx, [1:   4]) = [  2.42139E-02 0.00021  1.17587E-02 0.01310 ];
INF_SCATT2                (idx, [1:   4]) = [  2.80132E-03 0.04622 -5.66546E-03 0.03187 ];
INF_SCATT3                (idx, [1:   4]) = [  4.86481E-04 0.12725 -5.09274E-03 0.01450 ];
INF_SCATT4                (idx, [1:   4]) = [ -1.31043E-04 0.60180 -5.80674E-03 0.03192 ];
INF_SCATT5                (idx, [1:   4]) = [  1.34889E-04 0.08612 -3.49129E-03 0.01541 ];
INF_SCATT6                (idx, [1:   4]) = [ -2.90074E-04 0.14648 -5.72119E-03 0.02034 ];
INF_SCATT7                (idx, [1:   4]) = [  2.19284E-04 0.23779 -7.21200E-04 0.13811 ];

% Total scattering production cross sections:

INF_SCATTP0               (idx, [1:   4]) = [  3.78420E-01 8.9E-06  4.30958E-01 0.00051 ];
INF_SCATTP1               (idx, [1:   4]) = [  2.42160E-02 0.00018  1.17587E-02 0.01310 ];
INF_SCATTP2               (idx, [1:   4]) = [  2.80207E-03 0.04644 -5.66546E-03 0.03187 ];
INF_SCATTP3               (idx, [1:   4]) = [  4.86301E-04 0.12672 -5.09274E-03 0.01450 ];
INF_SCATTP4               (idx, [1:   4]) = [ -1.31107E-04 0.59890 -5.80674E-03 0.03192 ];
INF_SCATTP5               (idx, [1:   4]) = [  1.35055E-04 0.08348 -3.49129E-03 0.01541 ];
INF_SCATTP6               (idx, [1:   4]) = [ -2.89758E-04 0.14872 -5.72119E-03 0.02034 ];
INF_SCATTP7               (idx, [1:   4]) = [  2.19736E-04 0.23566 -7.21200E-04 0.13811 ];

% Diffusion parameters:

INF_TRANSPXS              (idx, [1:   4]) = [  3.29898E-01 0.00062  4.21287E-01 0.00080 ];
INF_DIFFCOEF              (idx, [1:   4]) = [  1.01041E+00 0.00062  7.91226E-01 0.00080 ];

% Reduced absoption and removal:

INF_RABSXS                (idx, [1:   4]) = [  1.76585E-03 0.00431  3.81712E-03 0.01207 ];
INF_REMXS                 (idx, [1:   4]) = [  5.97014E-03 0.00305  5.93799E-03 0.00477 ];

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

INF_S0                    (idx, [1:   8]) = [  3.74221E-01 9.3E-05  4.18579E-03 0.00785  2.14954E-03 0.00074  4.28809E-01 0.00051 ];
INF_S1                    (idx, [1:   8]) = [  2.51670E-02 0.00071 -9.53056E-04 0.01337 -2.44978E-04 0.00516  1.20037E-02 0.01273 ];
INF_S2                    (idx, [1:   8]) = [  2.97636E-03 0.04005 -1.75034E-04 0.05871 -1.57039E-04 0.00989 -5.50842E-03 0.03306 ];
INF_S3                    (idx, [1:   8]) = [  5.40133E-04 0.11002 -5.36518E-05 0.04625 -3.99700E-05 0.11587 -5.05277E-03 0.01370 ];
INF_S4                    (idx, [1:   8]) = [ -9.94042E-05 0.72358 -3.16393E-05 0.21917 -3.04243E-05 0.00495 -5.77631E-03 0.03211 ];
INF_S5                    (idx, [1:   8]) = [  1.28292E-04 0.10351  6.59659E-06 0.25217 -6.07546E-06 0.59970 -3.48522E-03 0.01648 ];
INF_S6                    (idx, [1:   8]) = [ -2.53617E-04 0.16141 -3.64576E-05 0.04262 -3.04485E-05 0.05897 -5.69074E-03 0.02014 ];
INF_S7                    (idx, [1:   8]) = [  1.97246E-04 0.29255  2.20379E-05 0.25233  1.40517E-05 0.32255 -7.35252E-04 0.12930 ];

% Scattering production matrixes:

INF_SP0                   (idx, [1:   8]) = [  3.74234E-01 9.7E-05  4.18579E-03 0.00785  2.14954E-03 0.00074  4.28809E-01 0.00051 ];
INF_SP1                   (idx, [1:   8]) = [  2.51690E-02 0.00068 -9.53056E-04 0.01337 -2.44978E-04 0.00516  1.20037E-02 0.01273 ];
INF_SP2                   (idx, [1:   8]) = [  2.97710E-03 0.04026 -1.75034E-04 0.05871 -1.57039E-04 0.00989 -5.50842E-03 0.03306 ];
INF_SP3                   (idx, [1:   8]) = [  5.39953E-04 0.10953 -5.36518E-05 0.04625 -3.99700E-05 0.11587 -5.05277E-03 0.01370 ];
INF_SP4                   (idx, [1:   8]) = [ -9.94679E-05 0.71968 -3.16393E-05 0.21917 -3.04243E-05 0.00495 -5.77631E-03 0.03211 ];
INF_SP5                   (idx, [1:   8]) = [  1.28458E-04 0.10071  6.59659E-06 0.25217 -6.07546E-06 0.59970 -3.48522E-03 0.01648 ];
INF_SP6                   (idx, [1:   8]) = [ -2.53300E-04 0.16399 -3.64576E-05 0.04262 -3.04485E-05 0.05897 -5.69074E-03 0.02014 ];
INF_SP7                   (idx, [1:   8]) = [  1.97698E-04 0.29006  2.20379E-05 0.25233  1.40517E-05 0.32255 -7.35252E-04 0.12930 ];

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

CMM_TRANSPXS              (idx, [1:   4]) = [  3.24829E-01 0.00969  5.31346E-01 0.02389 ];
CMM_TRANSPXS_X            (idx, [1:   4]) = [  3.27732E-01 0.02344  5.32814E-01 0.01816 ];
CMM_TRANSPXS_Y            (idx, [1:   4]) = [  3.23011E-01 0.00225  5.14264E-01 0.05998 ];
CMM_TRANSPXS_Z            (idx, [1:   4]) = [  3.23874E-01 0.00356  5.49413E-01 0.00890 ];
CMM_DIFFCOEF              (idx, [1:   4]) = [  1.02628E+00 0.00969  6.27696E-01 0.02389 ];
CMM_DIFFCOEF_X            (idx, [1:   4]) = [  1.01765E+00 0.02344  6.25815E-01 0.01816 ];
CMM_DIFFCOEF_Y            (idx, [1:   4]) = [  1.03196E+00 0.00225  6.50516E-01 0.05998 ];
CMM_DIFFCOEF_Z            (idx, [1:   4]) = [  1.02922E+00 0.00356  6.06756E-01 0.00890 ];

% Delayed neutron parameters (Meulekamp method):

BETA_EFF                  (idx, [1:  18]) = [  2.96096E-03 0.12522  2.06677E-04 0.46495  5.78893E-04 0.30174  4.43222E-04 0.38580  4.55577E-04 0.25429  8.63815E-04 0.20856  4.65868E-05 0.95132  3.66188E-04 0.38874  0.00000E+00 0.0E+00 ];
LAMBDA                    (idx, [1:  18]) = [  3.21730E-01 0.17269  1.24667E-02 3.9E-09  2.82917E-02 0.0E+00  4.25244E-02 0.0E+00  1.33042E-01 0.0E+00  2.92467E-01 5.4E-09  6.66488E-01 0.0E+00  1.63478E+00 0.0E+00  0.00000E+00 0.0E+00 ];

