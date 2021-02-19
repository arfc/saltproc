from process import Process


class Separator(Process):
    """Class evaluates gas removal efficiency in separator (bubble separator).

    Attributes
    ----------
    qe : float
        liquid flow rate (m^3/s)
        default: same as the value in q_salt defined in sparger class
    qg : float
        gas flow rate (m^3/s)
        default: same as the value in q_he defined in sparger class
    pgamma : float
        the pressure at the densitometer station
    x : float
        the gas injection rate
        default: 5% of total flow

    Methods
    -------
    eff()
        Evaluates gas removal efficiency using Equation 6
         from Gabbard's report. [1]

    References
    ----------
    [1] Gabbard, C. H. Development of an axial-flow centrifugal gas bubble
    separator for use in MSR xenon removal system. United States: N. p.,
    1974. Web. doi:10.2172/4324438.
    """

    def __init__(self, qe=0.1, qg=0.005, pgamma=10, x=0.05):
        """ Initializes the Separator object.

        Parameters
        ----------
        qe : float
            liquid flow rate (m^3/s)
            default: same as the value in q_salt defined in sparger class
        qg : float
            gas flow rate (m^3/s)
            default: same as the value in q_he defined in sparger class
        pgamma : float
            the pressure at the densitometer station
            default: from Gabbard's report [1]
        x : float
            the gas injection rate
            default: 5% of total flow
        """

        # super().__init__(*initial_data, **kwargs)
        self.qe = qe
        self.qg = qg
        self.pgamma = pgamma
        self.x = x

    def description(self):
        """Class attributes' descriptions for plotting purpose in sensitivity
        analysis
        Return
        ------
        pltdict: dict
            contains instances' information
        """

        plt_dict = {'qe': {'xaxis': 'liquid flow rate ${(m^3/s)}$',
                           'fname': 'liquid_flow_rate'},
                    'qg': {'xaxis': 'gas flow rate ${(m^3/s)}$',
                           'fname': 'gas_flow_rate'},
                    'pgamma': {'xaxis': 'densitometer pressure ${(Pa)}$',
                               'fname': 'densitometer_pressure'},
                    'x': {'xaxis': 'the gas injection rate ${(m)}$',
                          'fname': 'the gas_injection_rate'},
                    }

        return plt_dict

    def eff(self):
        """ Evaluates gas removal efficiency using Equation 6
         from Gabbard's report. [1]

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

        sep_eff = (2116.8 * self.qg) /\
                  (self.x * self.qe * self.pgamma + 2116.8 * self.qg)
        rem_eff = {'Xe': sep_eff, 'Kr': sep_eff, 'H': sep_eff}

        return rem_eff
