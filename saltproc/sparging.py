import numpy as np


class Sparger():
    """Class evaluates gas removal efficiency in sparger (bubble generator).

    """

    def __init__(self, q_salt=0.1, q_he=0.005, l=10,
                 ds=0.1, db=0.001, salt_temp=900):
        """ Initializes the Sparger object.

        Parameters
        ----------
        Q_salt : float
            volumetric salt flow rate (m^3/s)
        Q_He : float
            volumetric helium flow rate (m^3/s)
        L : float
            sparger/contractor length (m)
        ds : float
            sparger/contractor (pipe) diameter (m)
        db : float
            bubble diameter (m) for bubble generator/separator
        Tsalt : float
            salt temperature (K)
        """

        self.Q_salt = Q_salt
        self.Q_He = Q_He
        self.L = L
        self.ds = ds
        self.db = db
        self.Tsalt = Tsalt

    def eff(self):
        """Evaluates gas removal efficiency in sparger (bubble generator).

        Variables
        ----------
        H : dict
            ``key``
                Name of target isotope.
            ``value``
                Henry's law of constant.
        vl : float
            average liquid velocity (m/s)
        mu : float
            kinematic viscosity Pa.s
        Ac : float
            contactor cross-section (m2)
        rho : float
            density kg/m3
        N_Sh: float
            dimensionless number from slide 8 developed by Jiaqi

        Constants
        ----------
        H : dict
            ``key``
                Name of target isotope.
            ``value``
                Henry's law of constant.
        R : real
            universal gas constant (Pa.m3/mol-K)
        D : real
            liquid phase diffusivity (cm2/s)


        Returns
        -------
        rem_eff : dict
            Dictionary that contains removal efficiency of each target
            element.

            ``key``
                Name of target isotope.
            ``value``
                removal efficiency.

        Note
        ----
        Henry's law of constant (Pa.m3/mol) for Xe, Kr, H from
        Sander, R.: Compilation of Henry's law constants (version 4.0)
        for water as solvent, Atmos. Chem. Phys., 15, 4399–4981
        """

        def eps(H, K_L):
            """Evaluates gas removal efficiency in sparger (bubble generator)
            using Eq. 4 from Peebles report (ORNL-TM-2245).
            Returns
            -------
            efficiency : float
                removal efficiency of a specific chemical element.

            """
            a = (6/self.db) * (self.Q_He / (self.Q_He + self.Q_salt))
            alpha = (R * self.Tsalt / H) * (self.Q_salt / self.Q_He)
            beta = (K_L * a * Ac * self.L * (1 + alpha)) / self.Q_salt

            return (1-np.exp(-beta))/(1+alpha)

        H = {'Xe': 4.3e-5, 'Kr': 2.5e-5, 'H': 2.6e-6}
        H['Xe'] = 1 / (H['Xe'] * np.exp(2300 * (1/self.Tsalt - 1/298.15)))
        H['Kr'] = 1 / (H['Kr'] * np.exp(1900 * (1/self.Tsalt - 1/298.15)))
        H['H'] = 1 / (H['H'] * np.exp(0 * (1/self.Tsalt - 1/298.15)))
        D = 2.5E-9
        R = 8.314
        Ac = np.pi * (self.ds/2)**2
        mu = 1.076111581e-2 * (self.Tsalt/1000)**(-4.833549134)
        rho = (6.105 - 0.001272 * self.Tsalt) * 1000
        nu = mu / rho
        vl = self.Q_salt / Ac
        N_Re = self.ds * vl / nu
        N_Sc = nu / D
        N_Sh = 2.06972 * (N_Re**0.555) * (N_Sc**0.5)
        #  An alternative correlation for Sherwood from ORNL-TM-2245 Eq.36
        # N_Sh = 0.0096 * (N_Re**0.913) * (N_Sc**0.346)
        coeff_K_L = N_Sh * D / self.ds  # m/s

        rem_eff = {}
        for key in H:
            rem_eff[key] = np.around(eps(H[key], coeff_K_L), 3)

        return rem_eff


class Separator():
    """Class evaluates gas removal efficiency in separator (bubble separator).

     """

    def __init__(self, Qe=0.1, Qg=0.005, Pgamma=10, X=0.05):
        """ Initializes the Separator object.

        Parameters
        ----------
        Qe : float
            liquid flow rate (m^3/s)
        Qg : float
            gas flow rate (m3/s)
        Pgamma : float
            the pressure at the densitometer station
        X : float
            the gas injection rate
            default: 5% 0f total flow
        """

        self.Qe = Qe
        self.Qg = Qg
        self.Pgamma = Pgamma
        self.X = X

    def eff(self):
        """ Evaluates gas removal efficiency in bubble separator
            using Equation 6 from Gabbard report.

        Returns
        -------
        rem_eff : dict
            Dictionary that contains removal efficiency of each target
            element.

            ``key``
                Name of target isotope.
            ``value``
                removal efficiency.
        """

        sep_eff = (2116.8 * self.Qg) /\
                  (self.X * self.Qe * self.Pgamma + 2116.8 * self.Qg)
        rem_eff = {}
        rem_eff['Xe'] = np.around(sep_eff, 3)
        rem_eff['Kr'] = np.around(sep_eff, 3)
        rem_eff['H'] = np.around(sep_eff, 3)

        return rem_eff
