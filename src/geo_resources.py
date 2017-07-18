from shapely.geometry import Polygon
from shapely.geometry import Point
import geopandas as gpd
import matplotlib.pyplot as plt

airport_poly = Polygon(((-3.29377, 41.07961), (-3.88696, 41.08127), (-3.59719, 40.05861), (-2.93164, 40.06891), (-3.29377, 41.07961)))

TMA = Polygon(((-4.12150, 41.30000), (-4.36400, 41.10300), (-4.36400, 39.56200), (-4.08050, 39.33100), (-2.55050, 39.35250), (-2.27480, 39.53210), (-2.22000, 40.00000), (-2.17400, 40.00000), (-2.09300, 40.05200), (-2.09300, 41.02040), (-2.30000, 41.02000), (-2.30000, 41.18000), (-2.22080, 41.30060), (-4.12100, 41.30000)))

poly_north = Polygon(((-3.46352, 40.74744), (-3.68924, 40.74478), (-3.59233, 40.48915), (-3.53872, 40.50060), (-3.46352, 40.74744)))

poly_south = Polygon(((-3.54558, 40.50280), (-3.59287, 40.47710), (-3.45302, 40.24947), (-3.27294, 40.34823), (-3.54558, 40.50280)))

poly_A0 = Polygon(((-3.57818, 40.49282), (-3.57089, 40.49269), (-3.57078, 40.52304), (-3.58158, 40.52295), (-3.57818, 40.49282)))

poly_A1 = Polygon(((-3.56887, 40.57307), (-3.61041, 40.57241), (-3.59407, 40.52293), (-3.56849, 40.52289), (-3.56887, 40.57307)))

poly_A2 = Polygon(((-3.56989, 40.63903), (-3.64513, 40.63983), (-3.62534, 40.57223), (-3.56882, 40.57306), (-3.56989, 40.63903)))

poly_A3 = Polygon(((-3.57175, 40.74122), (-3.63113, 40.74063), (-3.60896, 40.63949), (-3.56951, 40.63901), (-3.57175, 40.74122)))

poly_AA = Polygon(((-3.57195, 40.74416), (-3.68776, 40.74190), (-3.59247, 40.48824), (-3.56693, 40.49252), (-3.57195, 40.74416)))

poly_B0 = Polygon(((-3.56196, 40.49960), (-3.55525, 40.49974), (-3.55285, 40.52805), (-3.56435, 40.52817), (-3.56196, 40.49960)))

poly_B1 = Polygon(((-3.53485, 40.52783), (-3.52343, 40.57740), (-3.56799, 40.57827), (-3.56606, 40.52830), (-3.53485, 40.52783)))

poly_B2 = Polygon(((-3.56811, 40.57833), (-3.51316, 40.57732), (-3.50060, 40.64347), (-3.56969, 40.64485), (-3.56811, 40.57833)))

poly_B3 = Polygon(((-3.53502, 40.64421), (-3.51929, 40.74518), (-3.57187, 40.74469), (-3.56944, 40.64492), (-3.53502, 40.64421)))

poly_BB = Polygon(((-3.56681, 40.49786), (-3.53893, 40.50062), (-3.46393, 40.74682), (-3.57212, 40.74583), (-3.56681, 40.49786)))

poly_C0 = Polygon(((-3.57295, 40.48627), (-3.57759, 40.48399), (-3.55813, 40.46076), (-3.54916, 40.46579), (-3.57295, 40.48627)))

poly_C1 = Polygon(((-3.57380, 40.45225), (-3.54418, 40.40969), (-3.50577, 40.42930), (-3.54683, 40.46681), (-3.57380, 40.45225)))

poly_C2 = Polygon(((-3.55106, 40.40605), (-3.50421, 40.34691), (-3.45115, 40.37566), (-3.50583, 40.42929), (-3.55106, 40.40605)))

poly_C3 = Polygon(((-3.45083, 40.37576), (-3.48302, 40.35825), (-3.41353, 40.27202), (-3.37177, 40.29623), (-3.45083, 40.37576)))

poly_CC = Polygon(((-3.56738, 40.49067), (-3.59278, 40.47706), (-3.45210, 40.25049), (-3.37180, 40.29630), (-3.56738, 40.49067)))

poly_D0 = Polygon(((-3.55601, 40.49705), (-3.56269, 40.49324), (-3.54164, 40.47032), (-3.53140, 40.47636), (-3.55601, 40.49705)))

poly_D1 = Polygon(((-3.46477, 40.45083), (-3.51756, 40.48431), (-3.54432, 40.46881), (-3.50496, 40.42969), (-3.46477, 40.45083)))

poly_D2 = Polygon(((-3.45094, 40.37616), (-3.38885, 40.41225), (-3.45691, 40.45496), (-3.50499, 40.42972), (-3.45094, 40.37616)))

poly_D3 = Polygon(((-3.37148, 40.29629), (-3.32268, 40.32432), (-3.41999, 40.39417), (-3.45119, 40.37620), (-3.37148, 40.29629)))

poly_DD = Polygon(((-3.37161, 40.29576), (-3.27507, 40.34928), (-3.54598, 40.50271), (-3.56721, 40.49084), (-3.37161, 40.29576)))

poly_NE = Polygon(((-3.55356, 40.58884), (-3.37778, 40.59099), (-3.29399, 41.07870), (-3.55276, 41.02823), (-3.55356, 40.58884)))

poly_NW = Polygon(((-3.59283, 41.02731), (-3.88569, 41.08090), (-3.72914, 40.58557), (-3.58284, 40.58742), (-3.59283, 41.02731)))

poly_SE = Polygon(((-3.46864, 40.43686), (-3.07089, 40.07006), (-2.93503, 40.07056), (-3.04782, 40.30525), (-3.34639, 40.50898), (-3.46864, 40.43686)))

poly_SW = Polygon(((-3.66551, 40.32802), (-3.59183, 40.06082), (-3.20344, 40.06778), (-3.52975, 40.39949), (-3.66551, 40.32802)))


# waypoints
waypoints_dict = {}
wyp_radius = 0.1

point_WYP_CASTEJON = Point((-2.54461, 40.37195))
poly_WYP_CASTEJON = point_WYP_CASTEJON.buffer(wyp_radius)
waypoints_dict['CJN'] = poly_WYP_CASTEJON

point_WYP_PERALES = Point((-3.34820, 40.25223))
poly_WYP_PERALES = point_WYP_PERALES.buffer(wyp_radius)
waypoints_dict['PDT'] = poly_WYP_PERALES

point_WYP_NAVAS = Point((-4.24741, 40.36867))
poly_WYP_NAVAS = point_WYP_NAVAS.buffer(wyp_radius)
waypoints_dict['NVS'] = poly_WYP_NAVAS

point_WYP_VILLATOBAS = Point((-3.46860, 39.77804))
poly_WYP_VILLATOBAS = point_WYP_VILLATOBAS.buffer(wyp_radius)
waypoints_dict['VTB'] = poly_WYP_VILLATOBAS

point_WYP_ROBLEDILLO = Point((-3.24728, 40.85277))
poly_WYP_ROBLEDILLO = point_WYP_ROBLEDILLO.buffer(wyp_radius)
waypoints_dict['RBO'] = poly_WYP_ROBLEDILLO

point_WYP_SOMOSIERRA = Point((-3.60816, 41.15260))
poly_WYP_SOMOSIERRA = point_WYP_SOMOSIERRA.buffer(wyp_radius)
waypoints_dict['SIE'] = poly_WYP_SOMOSIERRA

point_WYP_COLMENAR_VIEJO = Point((-3.73534, 40.64548))
poly_WYP_COLMENAR_VIEJO = point_WYP_COLMENAR_VIEJO.buffer(wyp_radius)
waypoints_dict['CNR'] = poly_WYP_COLMENAR_VIEJO

point_WYP_TOLEDO = Point((-4.33705, 39.96818))
poly_WYP_TOLEDO = point_WYP_TOLEDO.buffer(wyp_radius)
waypoints_dict['TLD'] = poly_WYP_TOLEDO

point_WYP_SALAMANCA = Point((-5.45569, 41.01655))
poly_WYP_SALAMANCA = point_WYP_SALAMANCA.buffer(wyp_radius)
waypoints_dict['BBI'] = poly_WYP_SALAMANCA

point_WYP_ZAMORA = Point((-5.63972, 41.53014))
poly_WYP_ZAMORA = point_WYP_ZAMORA.buffer(wyp_radius)
waypoints_dict['ZMR'] = poly_WYP_ZAMORA

point_WYP_ORBIS = Point((-4.19628, 41.26455))
poly_WYP_ORBIS = point_WYP_ORBIS.buffer(wyp_radius)
waypoints_dict['ORBIS'] = poly_WYP_ORBIS

point_WYP_AVILA = Point((-4.54917, 40.62362))
poly_WYP_AVILA = point_WYP_AVILA.buffer(wyp_radius)
waypoints_dict['AVILA'] = poly_WYP_AVILA

point_WYP_MORAL = Point((-3.54152, 38.99938))
poly_WYP_MORAL = point_WYP_MORAL.buffer(wyp_radius)
waypoints_dict['MORAL'] = poly_WYP_MORAL

point_WYP_SOTUK = Point((-4.74593, 39.19341))
poly_WYP_SOTUK = point_WYP_SOTUK.buffer(wyp_radius)
waypoints_dict['SOTUK'] = poly_WYP_SOTUK

point_WYP_RIDAV = Point((-5.80795, 40.53447))
poly_WYP_RIDAV = point_WYP_RIDAV.buffer(wyp_radius)
waypoints_dict['RIDAV'] = poly_WYP_RIDAV

point_WYP_EREMA = Point((-4.13884, 41.08185))
poly_WYP_EREMA = point_WYP_EREMA.buffer(wyp_radius)
waypoints_dict['EREMA'] = poly_WYP_EREMA

point_WYP_TABANERA = Point((-4.10819, 42.02782))
poly_WYP_TABANERA = point_WYP_TABANERA.buffer(wyp_radius)
waypoints_dict['NEA'] = poly_WYP_TABANERA

point_WYP_LALPI = Point((-3.70249, 40.95951))
poly_WYP_LALPI = point_WYP_LALPI.buffer(wyp_radius)
waypoints_dict['LALPI'] = poly_WYP_LALPI

point_WYP_RESBI = Point((-4.18606, 40.73531))
poly_WYP_RESBI = point_WYP_RESBI.buffer(wyp_radius)
waypoints_dict['RESBI'] = poly_WYP_RESBI

point_WYP_BUREX = Point((-3.93781, 39.81050))
poly_WYP_BUREX = point_WYP_BUREX.buffer(wyp_radius)
waypoints_dict['BUREX'] = poly_WYP_BUREX

point_WYP_NASOS = Point((-3.02638, 39.39891))
poly_WYP_NASOS = point_WYP_NASOS.buffer(wyp_radius)
waypoints_dict['NASOS'] = poly_WYP_NASOS

point_WYP_SIRGU = Point((-2.59871, 40.26058))
poly_WYP_SIRGU = point_WYP_SIRGU.buffer(wyp_radius)
waypoints_dict['SIRGU'] = poly_WYP_SIRGU

point_WYP_PRADO = Point((-2.01048, 40.14665))
poly_WYP_PRADO = point_WYP_PRADO.buffer(wyp_radius)
waypoints_dict['PRADO'] = poly_WYP_PRADO

point_WYP_ADUXO = Point((-2.06352, 40.51171))
poly_WYP_ADUXO = point_WYP_ADUXO.buffer(wyp_radius)
waypoints_dict['ADUXO'] = poly_WYP_ADUXO

point_WYP_TERSA = Point((-2.13670, 40.72500))
poly_WYP_TERSA = point_WYP_TERSA.buffer(wyp_radius)
waypoints_dict['TERSA'] = poly_WYP_TERSA

point_WYP_NOSKO = Point((-2.81557, 40.65606))
poly_WYP_NOSKO = point_WYP_NOSKO.buffer(wyp_radius)
waypoints_dict['NOSKO'] = poly_WYP_NOSKO

point_WYP_PINAR = Point((-2.59796, 40.97968))
poly_WYP_PINAR = point_WYP_PINAR.buffer(wyp_radius)
waypoints_dict['PINAR'] = poly_WYP_PINAR

point_WYP_BARAHONA = Point((-2.62984, 41.32356))
poly_WYP_BARAHONA = point_WYP_BARAHONA.buffer(wyp_radius)
waypoints_dict['BAN'] = poly_WYP_BARAHONA

point_WYP_TAGOM = Point((-3.43177, 40.98377))
poly_WYP_TAGOM = point_WYP_TAGOM.buffer(wyp_radius)
waypoints_dict['TAGOM'] = poly_WYP_TAGOM

point_WYP_OBIKI = Point((-2.85877, 41.22684))
poly_WYP_OBIKI = point_WYP_OBIKI.buffer(wyp_radius)
waypoints_dict['OBIKI'] = poly_WYP_OBIKI

point_WYP_BARDI = Point((-6.30172, 40.58340))
poly_WYP_BARDI = point_WYP_BARDI.buffer(wyp_radius)
waypoints_dict['BARDI'] = poly_WYP_BARDI

point_WYP_CACERES = Point((-6.43475, 39.52442))
poly_WYP_CACERES = point_WYP_CACERES.buffer(wyp_radius)
waypoints_dict['CCS'] = poly_WYP_CACERES

point_WYP_LONGA = Point((-4.87592, 40.43643))
poly_WYP_LONGA = point_WYP_LONGA.buffer(wyp_radius)
waypoints_dict['LONGA'] = poly_WYP_LONGA

point_WYP_NANDO = Point((-2.17385, 39.98835))
poly_WYP_NANDO = point_WYP_NANDO.buffer(wyp_radius)
waypoints_dict['NANDO'] = poly_WYP_NANDO

point_WYP_VILLA = Point((-2.41056, 40.23306))
poly_WYP_VILLA = point_WYP_VILLA.buffer(wyp_radius)
waypoints_dict['VILLA'] = poly_WYP_VILLA

point_WYP_TOBEK = Point((-3.42446, 40.19635))
poly_WYP_TOBEK = point_WYP_TOBEK.buffer(wyp_radius)
waypoints_dict['TOBEK'] = poly_WYP_TOBEK

point_WYP_ASBIN = Point((-3.17639, 40.25500))
poly_WYP_ASBIN = point_WYP_ASBIN.buffer(wyp_radius)
waypoints_dict['ASBIN'] = poly_WYP_ASBIN

point_WYP_SSY = Point((-3.57528, 40.54639))
poly_WYP_SSY = point_WYP_SSY.buffer(wyp_radius/2)
waypoints_dict['SSY'] = poly_WYP_SSY

point_WYP_BRA = Point((-3.55773, 40.46914))  # TODO this is not needed
poly_WYP_BRA = point_WYP_BRA.buffer(wyp_radius/4)
waypoints_dict['BRA'] = poly_WYP_BRA


# SID/STAR
class WYP_seq:
    def __init__(self, name, cat, seq):
        self.name = name
        self.cat = cat
        self.seq = seq

    def check_runway(self, op_runway):
        if op_runway in self.cat:
            return True
        else: return False

    def check_seq(self, waypoint_list):
        if not waypoint_list:  # empty list
            return False
        prev_index = -1
        for waypoint in self.seq:
            if waypoint in waypoint_list and prev_index < waypoint_list.index(waypoint):
                prev_index = waypoint_list.index(waypoint)
            else:
                return False
        return True

# SID
# 14R diurno
BARDI2Q = WYP_seq('BARDI2Q', 'SID: 14R', ['NVS', 'BARDI'])
PINAR2B = WYP_seq('PINAR2B', 'SID: 14R', ['RBO', 'BARDI'])
VTB1Q = WYP_seq('VTB1Q', 'SID: 14R', ['PDT', 'VTB'])
CCS1Q = WYP_seq('CCS1Q', 'SID: 14R', ['NVS', 'CSS'])
RBO1B = WYP_seq('RBO1B', 'SID: 14R', ['RBO'])
ZMR1Q = WYP_seq('ZMR1Q', 'SID: 14R', ['NVS', 'ZMR'])
NANDO1B = WYP_seq('NANDO1B', 'SID: 14R', ['PDT', 'NANDO'])
SIE1Q = WYP_seq('SIE1Q', 'SID: 14R', ['CNR', 'SIE'])

# 14L diurno
BARDI2V = WYP_seq('BARDI2V', 'SID: 14L', ['NVS', 'BARDI'])
PINAR1E = WYP_seq('PINAR1E', 'SID: 14L', ['RBO', 'PINAR'])
VTB1V = WYP_seq('VTB1V', 'SID: 14L', ['PDT', 'VTB'])
ZMR1V = WYP_seq('ZMR1V', 'SID: 14L', ['NVS', 'ZMR'])
RBO1E = WYP_seq('RBO1E', 'SID: 14L', ['RBO'])
CCS2V = WYP_seq('CCS2V', 'SID: 14L', ['NVS', 'CCS'])
SIE1E = WYP_seq('SIE1E', 'SID: 14L', ['RBO', 'SIE'])
NANDO1E = WYP_seq('NANDO1E', 'SID: 14L', ['NANDO'])

# 36R diurno
BARDI5W = WYP_seq('BARDI5W', 'SID: 36R', ['CNR', 'AVILA', 'LONGA', 'BARDI'])
PINAR1D = WYP_seq('PINAR1D', 'SID: 36R', ['RBO', 'PINAR'])
VTB1D = WYP_seq('VTB1D', 'SID: 36R', ['PDT', 'VTB'])
ZMR2W = WYP_seq('ZMR2W', 'SID: 36R', ['SIE', 'ZMR'])
RBO1D = WYP_seq('RBO1D', 'SID: 36R', ['RBO'])
CCS4W = WYP_seq('CCS4W', 'SID: 36R', ['CNR', 'AVILA', 'LONGA', 'CSS'])
SIE2W = WYP_seq('SIE2W', 'SID: 36R', ['SIE'])
NANDO1D = WYP_seq('NANDO1D', 'SID: 36R', ['PDT', 'NANDO'])

# 36L diurno
ZMR1T = WYP_seq('ZMR1T', 'SID: 36L', ['SSY', 'SIE', 'ORBIS', 'ZMR'])
SIE1T = WYP_seq('SIE1T', 'SID: 36L', ['SSY', 'SIE'])
NANDO2N = WYP_seq('NANDO2N', 'SID: 36L', ['SSY', 'PDT', 'NANDO'])
BARDI2K = WYP_seq('BARDI2K', 'SID: 36L', ['SSY', 'AVILA', 'LONGA', "BARDI"])
VTB1K = WYP_seq('VTB1K', 'SID: 36L', ['SSY', 'CNR', 'BRA', 'VTB'])
PINAR2N = WYP_seq('PINAR2N', 'SID: 36L', ['SSY', 'RBO', 'PINAR'])
BARDI2T = WYP_seq('BARDI2T', 'SID: 36L', ['SSY', 'CNR', 'AVILA', 'LONGA', 'BARDI'])
VTB1T = WYP_seq('VTB1T', 'SID: 36L', ['SSY', 'CNR', 'BRA', 'VTB'])
RBO1N = WYP_seq('RBO1N', 'SID: 36L', ['SSY', 'RBO'])
CCS1K = WYP_seq('CCS1K', 'SID: 36L', ['SSY', 'AVILA', 'LONGA', 'CSS'])
ZMR1K = WYP_seq('SIE1T', 'SID: 36L', ['SSY', 'SIE', 'ORBIS', 'ZMR'])
SIE1K = WYP_seq('SIE1T', 'SID: 36L', ['SSY', 'SIE'])
CCS1T = WYP_seq('CCS1T', 'SID: 36L', ['SSY', 'CNR', 'AVILA', 'LONGA', 'CSS'])

# STAR
# 32L/32R, north config, east
ADUXO1D = WYP_seq('ADUXO1D', 'STAR: 32L/32R, east', ['ADUXO', 'SIRGU', 'ASBIN', 'PDT'])
VILLA1D = WYP_seq('VILLA1D', 'STAR: 32L/32R, east', ['VILLA', 'SIRGU', 'ASBIN', 'PDT'])
BAN4D = WYP_seq('BAN4D', 'STAR: 32L/32R, east', ['BAN', 'PINAR', 'NOSKO', 'ASBIN', 'PDT'])
NASOS1D = WYP_seq('NASOS1D', 'STAR: 32L/32R, east', ['NASOS', 'SIRGU', 'ASBIN', 'PDT'])
TERSA2Z = WYP_seq('TERSA2Z', 'STAR: 32L/32R, east', ['TERSA', 'NOSKO', 'ASBIN', 'PDT'])
PRADO1D = WYP_seq('PRADO1D', 'STAR: 32L/32R, east', ['PRADO', 'SIRGU', 'ASBIN', 'PDT'])

# 32L/32R, north config, west
ORBIS1C = WYP_seq('ORBIS1C', 'STAR: 32L/32R, west', ['ORBIS', 'NVS', 'TOBEK', 'PDT'])
SOTUK2C = WYP_seq('SOTUK2C', 'STAR: 32L/32R, west', ['SOTUK', 'BUREX', 'TOBEK', 'PDT'])
TLD2C = WYP_seq('TLD2C', 'STAR: 32L/32R, west', ['TLD', 'BUREX', 'TOBEK', 'PDT'])
MORAL4C = WYP_seq('MORAL4C', 'STAR: 32L/32R, west', ['MORAL', 'BUREX', 'TOBEK', 'PDT'])
RIDAV3C = WYP_seq('RIDAV3C', 'STAR: 32L/32R, west', ['RIDAV', 'TLD', 'BUREX', 'TOBEK', 'PDT'])
ZMR3C = WYP_seq('ZMR3C', 'STAR: 32L/32R, west', ['ZMR', 'AVILA', 'NVS', 'TOBEK', 'PDT'])

# 18L/18R, south config, east
ADUXO4B = WYP_seq('ADUXO4B', 'STAR: 18L/18R, east', ['ADUXO', 'NOSKO', 'RBO', 'TAGOM'])
BAN3B = WYP_seq('BAN3B', 'STAR: 18L/18R, east', ['BAN', 'OBIKI', 'TAGOM'])
PRADO4E = WYP_seq('PRADO4E', 'STAR: 18L/18R, east', ['PRADO', 'CJN', 'NOSKO', 'RBO', 'TAGOM'])
TERSA4E = WYP_seq('TERSA4E', 'STAR: 18L/18R, east', ['TERSA', 'NOSKO', 'RBO', 'TAGOM'])
VILLA4E = WYP_seq('VILLA4E', 'STAR: 18L/18R, east', ['VILLA', 'CJN', 'NOSKO', 'RBO', 'TAGOM'])
NASOS4A = WYP_seq('NASOS4A', 'STAR: 18L/18R, east', ['NASOS', 'CJN', 'NOSKO', 'RBO', 'TAGOM'])

# 18L/18R, south config, west
SOTUK5A = WYP_seq('SOTUK5A', 'STAR: 18L/18R, west', ['SOTUK', 'TLD', 'NVS', 'RESBI', 'LALPI'])
MORAL5A = WYP_seq('MORAL5A', 'STAR: 18L/18R, west', ['MORAL', 'TLD', 'NVS', 'RESBI', 'LALPI'])
TLD3Z = WYP_seq('TLD3Z', 'STAR: 18L/18R, west', ['TLD', 'NVS', 'RESBI', 'SIE'])
RIDAV1A = WYP_seq('RIDAV1A', 'STAR: 18L/18R, west', ['RIDAV', 'BBI', 'EREMA', 'LALPI'])
TLD5A = WYP_seq('TLD5A', 'STAR: 18L/18R, west', ['TLD', 'NVS', 'RESBI', 'LALPI'])
ORBIS4A = WYP_seq('ORBIS4A', 'STAR: 18L/18R, west', ['ORBIS', 'EREMA', 'LALPI'])
ORBIS1Z = WYP_seq('ORBIS1Z', 'STAR: 18L/18R, west', ['ORBIS', 'SIE'])
ZMR3A = WYP_seq('ZMR3A', 'STAR: 18L/18R, west', ['ZMR', 'EREMA', 'LALPI'])

# make a list of all SID_STAR
all_wyp_seq = [BARDI2Q, PINAR2B, VTB1Q, CCS1Q, RBO1B, ZMR1Q, NANDO1B, SIE1Q,
               BARDI2V, PINAR1E, VTB1V, ZMR1V, RBO1E, CCS2V, SIE1E, NANDO1E,
               BARDI5W, PINAR1D, VTB1D, ZMR2W, RBO1D, CCS4W, SIE2W, NANDO1D,
               ZMR1T, SIE1T, NANDO2N, BARDI2K, VTB1K, PINAR2N, BARDI2T, VTB1T, RBO1N, CCS1K, ZMR1K, SIE1K, CCS1T,
               ADUXO1D, VILLA1D, BAN4D, NASOS1D, TERSA2Z, PRADO1D,
               ORBIS1C, SOTUK2C, TLD2C, MORAL4C, RIDAV3C, ZMR3C,
               ADUXO4B, BAN3B, PRADO4E, TERSA4E, VILLA4E, NASOS4A,
               SOTUK5A, MORAL5A, TLD3Z, RIDAV1A, TLD5A, ORBIS4A, ORBIS1Z, ZMR3A]

# Runways

point_32L = Point(-3.554039, 40.463237)
point_32R = Point(-3.536341, 40.473727)
point_18L = Point(-3.559349, 40.527936)
point_18R = Point(-3.574792, 40.522701)

runway_ths_dict = {}
runway_ths_dict['32L'] = point_32L
runway_ths_dict['32R'] = point_32R
runway_ths_dict['18L'] = point_18L
runway_ths_dict['18R'] = point_18R

# analysis/visualization
if __name__ == '__main__':
    figsize = 6, 6
    for point in waypoints_dict.keys():
        print point
    pts = gpd.GeoSeries([point for point in waypoints_dict.values()])
    pts2 = gpd.GeoSeries([airport_poly, TMA])
    pts3 = gpd.GeoSeries([point for point in runway_ths_dict.values()])

    plt.style.use('bmh')
    fig, ax = plt.subplots(1, 1, figsize = (figsize))
    pts.crs = {'init': 'epsg:4326'}
    # pts2.crs = {'init': 'epsg:4326'}
    # pts3.crs = {'init': 'epsg:4326'}
    pts.plot(marker='.', color='red', markersize=4, ax=ax)
    pts2.plot(marker='.', color='blue', markersize=4, ax=ax)
    pts3.plot(marker='.', color='red', markersize=4, ax=ax)
    plt.show()




