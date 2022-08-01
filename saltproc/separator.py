"""Separator module"""
import numpy as np
from saltproc import Process


class Separator(Process):
    """Represents a bubble separator.

    Attributes
    ----------
    q_salt : float
        volumetric salt flow rate (m^3/s)
        Default: 0.1
    q_he : float
        volumetric helium flow rate (m^3/s)
        Default: 0.005
    do : float
        gas outlet diameter (m)
        Ranging from 1~3cm in our simulations
        Default: 0.02
    dp : float
        sparger/contractor (pipe) diameter (m)
        Default: 0.1
    db : float
        bubble diameter (m) for bubble generator/separator
        Default: 0.001
    deltap : float
        Pressure difference between the inlet and the gas outlet (Pa)
        (from 2e5 to 5e5 Pa)
        Default: 4e5
    temp_room: real
        room temperature (Kelvin)
        Default: 900
    k : float
        Slope of the initial swirling (use 1 for this).

    Methods
    -------
    eff()
        Evaluates gas removal efficiency from Jiaqi's correlation. [1]
    description()
        Contains a dictionary of plot properties.
    calc_rem_efficiency(el_name)
        Overrides exiting method in Parent class.

    References
    ----------
    [1] Jiaqi Chen and Caleb S. Brooks. Milestone 1.2 Report: CFD
    Sensitivity Analysis. In preparation
    """

    k = 1.0

    def __init__(self, q_salt=0.1, q_he=0.005, do=0.02, dp=0.1, db=0.001,
                 deltap=4e5, temp_salt=900, *initial_data, **kwargs):
        """ Initializes the Separator object.

        Parameters
        ----------
        q_salt : float
            volumetric salt flow rate (m^3/s)
            Default: 0.1
        q_he : float
            volumetric helium flow rate (m^3/s)
            Default: 0.005
        do : float
            gas outlet diameter (m)
            Ranging from 1~3cm in our simulations
            Default: 0.02
        dp : float
            sparger/contractor (pipe) diameter (m)
            Default: 0.1
        db : float
            bubble diameter (m) for bubble generator/separator
            Default: 0.001
        deltap : float
            Pressure difference between the inlet and the gas outlet (Pa)
            (from 2e5 to 5e5 Pa)
            Default: 4e5
        temp_room: real
            room temperature (Kelvin)
            Default: 900
        area : float
            contactor cross-section (m^2)
        jl : float
            liquid superficial velocity (m/s)
        alpha : float
            void fraction

        Notes
        -----
        Default values from Jiaqi's simulation
        """
        super().__init__(*initial_data, **kwargs)
        self.q_salt = q_salt
        self.q_he = q_he
        self.do = do
        self.deltap = deltap
        self.db = db
        self.dp = dp
        self.temp_salt = temp_salt
        self.area = np.pi * (self.dp / 2) ** 2
        self.alpha = self.q_he / (self.q_he + self.q_salt)
        self.jl = self.q_salt / self.area
        self.efficiency = self.eff()

    def calculate_removal_efficiency(self, nuc_name):
        """Calculate the value of the removal efficiency for a given nuclide
        in this process.

        Overrides the existing method in :class`openmc.process.Process` to
        provide efficiency values of target isotopes calculated in the
        ``eff()`` function.

        Parameters
        ----------
        nuc_name : str
            Name of target nuclide to be removed.

        Returns
        -------
        efficiency : float
            Extraction efficiency for the given nuclide.

        """

        return self.eff()[nuc_name]

    def description(self):
        """Class attributes' descriptions for plotting purpose in
        sensitivity analysis

        Returns
        ------
        pltdict: dict of str to str
            contains instances' information
        """
        plt_dict = {'q_salt': {'xaxis': 'salt flow rate ${(m^3/s)}$',
                               'yaxis': 'bubble separation efficiency (%)',
                               'vs': 'sep_eff'},
                    'q_he': {'xaxis': 'helium flow rate ${(m^3/s)}$',
                             'yaxis': 'bubble separation efficiency (%)',
                             'vs': 'sep_eff'},
                    'do': {'xaxis': 'gas outlet diameter ${(m)}$',
                           'yaxis': 'bubble separation efficiency (%)',
                           'vs': 'sep_eff'},
                    'dp': {'xaxis': 'pipe diameter ${(m)}$',
                           'yaxis': 'bubble separation efficiency (%)',
                           'vs': 'sep_eff'},
                    'db': {'xaxis': 'bubble diameter ${(m)}$',
                           'yaxis': 'bubble separation efficiency (%)',
                           'vs': 'sep_eff'},
                    'deltap': {'xaxis': 'pressure difference ${(Pa)}$',
                               'yaxis': 'bubble separation efficiency (%)',
                               'vs': 'sep_eff'},
                    'temp_salt': {'xaxis': 'average salt temperature ${(K)}$',
                                  'yaxis': 'bubble separation efficiency (%)',
                                  'vs': 'sep_eff'}
                    }

        return plt_dict

    def eff(self):
        """ Evaluates gas/bubble separation efficiency from Jiaqi's correlation

        Returns
        -------
        rem_eff : dict of str to float
            Dictionary that contains removal efficiency of each target
            element.

            ``key``
                Name of target isotope.
            ``value``
                removal efficiency.
        """

        dc = 3.41 * self.do
        mu = 1.076111581e-2 * (self.temp_salt / 1000)**(-4.833549134)
        rho = (6.105 - 0.001272 * self.temp_salt) * 1000
        nu = mu / rho
        vl = self.q_salt / self.area
        number_re = self.dp * vl / nu
        etha = 1 / (3.2 * rho * self.jl**2 * dc**2 /
                    (self.do**2 * self.deltap) + 1)
        dvoid = (4.89 * self.dp * (self.dp / self.db)**1.27) /\
                (1 + self.k**4 * number_re)
        df = self.do / (self.do + dvoid / (100 * self.alpha)**0.5)
        sep_eff = df / (1 + 0.23 * etha) + 3.26 * etha * (1 - df) * df
        rem_eff = {'Xe': sep_eff, 'Kr': sep_eff, 'H': sep_eff}

        return rem_eff


if __name__ == "__main__":

    print(Separator().eff())
