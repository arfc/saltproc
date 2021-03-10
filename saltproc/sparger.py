import numpy as np
from saltproc import Process


class Sparger(Process):
    """Class evaluates gas removal efficiency in sparger (bubble generator).

    Attributes
    ----------
    h_const : dict
        ``key``
            Name of target isotope.
        ``value``
            Henry's law constant.
    gas_const : real
        universal gas constant (Pa.m^3/mol-K)
    diffusivity : real
        liquid phase diffusivity (cm^2/s)
    temp_room: real
        room temperature (Kelvin)
    exp_const: dict
        ``key``
            Name of target isotope.
        ``value``
            exponential constant from following reference
    q_salt : float
        volumetric salt flow rate (m^3/s)
        Default: 0.1
    q_he : float
        volumetric helium flow rate (m^3/s)
        Default: 0.005
    length : float
        sparger/contractor length (m)
        Default: 10
    dp : float
        sparger/contractor (pipe) diameter (m)
        Default: 0.1
    db : float
        bubble diameter (m) for bubble generator/separator
        Default: 0.001
    temp_salt: float
        salt temperature (K)
        Default: 900
    area : float
        contactor cross-section (m^2)

    Methods
    -------
    eps(h_const, kl_const)
        Defines gas removal efficiency for sparger (bubble generator)
        using Eq. 4 from Peebles report (ORNL-TM-2245). [2]
    eff()
        Evaluates gas removal efficiencies for target isotopes.
    sherwood()
        Contains Sherwood number correlations from different sources.
    description()
        Contains a dictionary of plot properties.
    calc_rem_efficiency(el_name)
        Overrides exiting method in Parent class.

    References
    ----------
    [1] Henry's law constants (Pa.m3/mol) for Xe, Kr, H from
    Sander, R.: Compilation of Henry's law constants (version 4.0)
    for water as solvent, Atmos. Chem. Phys., 15, 4399–4981,
    https://doi.org/10.5194/acp-15-4399-2015, 2015.
    [2] Peebles, F. , 1968, “ Removal of Xenon-135 From Circulating
    Fuel Salt of the MSBR by Mass Transfer to Helium Bubbles,” Oak Ridge
    National Laboratory, Oak Ridge, TN, Report No. ORNL-TM-2245.
    [3] Jiaqi Chen and Caleb S. Brooks. Milestone 1.2 Report: CFD
    Sensitivity Analysis. In preparation
    """

    diffusivity = 2.5E-9
    gas_const = 8.314
    h_const = {'Xe': 4.3e-5, 'Kr': 2.5e-5, 'H': 2.6e-6}
    temp_room = 298.15
    exp_const = {'Xe': 2300, 'Kr': 1900, 'H': 0}

    def __init__(self, q_salt=0.1, q_he=0.005, length=10,
                 dp=0.1, db=0.001, temp_salt=900, corr='Jiaqi',
                 *initial_data, **kwargs):
        """ Initializes the Sparger object.

        Parameters
        ----------
        q_salt : float
            volumetric salt flow rate (m^3/s)
            Default: 0.1
        q_he : float
            volumetric helium flow rate (m^3/s)
            Default: 0.005
        length : float
            sparger/contractor length (m)
            Default: 10
        dp : float
            sparger/contractor (pipe) diameter (m)
            Default: 0.1
        db : float
            bubble diameter (m) for bubble generator/separator
            Default: 0.001
        temp_salt: float
            salt temperature (K)
            Default: 900
        area : float
            contactor cross-section (m^2)
        corr: string
             Sherwood correlations: ORNL-TM-2245 or Jaiqi's
             (1) milestone report from Jiaqi [3]
             (2) ORNL-TM-2245 Eq.36 [2]
             default: Sherwood correlation from ORNL-TM-2245 Eq.36

        Notes
        -----
        Default values comes from Jiaqi's simulation
        """
        super().__init__(*initial_data, **kwargs)
        self.q_salt = q_salt
        self.q_he = q_he
        self.length = length
        self.dp = dp
        self.db = db
        self.temp_salt = temp_salt
        self.area = np.pi * (self.dp / 2) ** 2
        self.corr = corr
        self.efficiency = self.eff()

    def calc_rem_efficiency(self, el_name):
        """Overrides the existing method in Process class to provide
        efficiency values of target isotopes calculated in eff() function.

        Parameters
        ----------
        el_name : str
            Name of target element to be removed.

        Returns
        -------
        efficiency : float
            Extraction efficiency for el_name element.

        """
        isotope = self.eff()[el_name]

        return isotope

    def description(self):
        """Class attributes' descriptions for plotting purpose in sensitivity
        analysis
        Return
        ------
        pltdict: dict
            contains instances' information
        """
        plt_dict = {'q_salt': {'xaxis': 'salt flow rate ${(m^3/s)}$',
                               'yaxis': 'removal efficiency (%)',
                               'vs': 'Xe_eff'},
                    'q_he': {'xaxis': 'helium flow rate ${(m^3/s)}$',
                             'yaxis': 'removal efficiency (%)',
                             'vs': 'Xe_eff'},
                    'length': {'xaxis': 'sparger pipe length ${(m)}$',
                               'yaxis': 'removal efficiency (%)',
                               'vs': 'Xe_eff'},
                    'dp': {'xaxis': 'sparger pipe diameter ${(m)}$',
                           'yaxis': 'removal efficiency (%)',
                           'vs': 'Xe_eff'},
                    'db': {'xaxis': 'bubble diameter ${(m)}$',
                           'yaxis': 'removal efficiency (%)',
                           'vs': 'Xe_eff'},
                    'temp_salt': {'xaxis': 'average salt temperature ${(K)}$',
                                  'yaxis': 'removal efficiency (%)',
                                  'vs': 'Xe_eff'}
                    }

        return plt_dict

    def eps(self, h_const, kl_const):
        """Evaluates gas removal efficiency using Eq. 4
        from Peebles report (ORNL-TM-2245).

        Returns
        -------
        efficiency : float
            removal efficiency of a specific chemical element.

        """
        a = (6/self.db) * (self.q_he / (self.q_he + self.q_salt))
        alpha = (self.gas_const * self.temp_salt / h_const) *\
                (self.q_salt / self.q_he)
        beta = (kl_const * a * self.area *
                self.length * (1 + alpha)) / self.q_salt

        return (1-np.exp(-beta))/(1+alpha)

    def sherwood(self):
        """ Contains Sherwood number correlations.
             Sherwood correlations: ORNL-TM-2245 or Jaiqi
             (1) Jaiqi Ph.D. dissertation
             (2) ORNL-TM-2245 Eq.36
             default: Sherwood correlation from ORNL-TM-2245 Eq.36
         """
        sh_corr = {
            'ORNL-TM-2245': '0.0096 * (number_re**0.913) * (number_sc**0.346)',
            'Jiaqi': '2.06972 * (number_re ** 0.555) * (number_sc ** 0.5)'}

        return sh_corr

    def eff(self):
        """Evaluates gas removal efficiencies for target isotopes.
        In this function, vl, mu, rho, number_sh, number_sc, number_re and kl
        are average liquid velocity (m/s), kinematic viscosity (Pa.s),
        density (kg/m^3), sherwood number from slide 8 developed by Jiaqi,
        schmidt number, reynold number and liquid phase mass transfer
        coefficient (m/s), respectively.

        Returns
        -------
        rem_eff : dict
            Dictionary containing removal efficiency of each target isotope.
            ``key``
                Name of target isotope.
            ``value``
                removal efficiency.
        """
        hh = {}
        for key in self.h_const:
            hh[key] = 1 / (self.h_const[key] *
                           np.exp(self.exp_const[key] * (1/self.temp_salt -
                                                         1/self.temp_room)))

        mu = 1.076111581e-2 * (self.temp_salt / 1000)**(-4.833549134)
        rho = (6.105 - 0.001272 * self.temp_salt) * 1000
        nu = mu / rho
        vl = self.q_salt / self.area
        number_re = self.dp * vl / nu
        number_sc = nu / self.diffusivity
        number_sh = eval(self.sherwood()[self.corr],
                         {'number_sc': number_sc, 'number_re': number_re})
        kl = number_sh * self.diffusivity / self.dp
        rem_eff = {key: self.eps(hh[key], kl) for key in self.h_const}

        return rem_eff


if __name__ == '__main__':
    print(Sparger().eff())
