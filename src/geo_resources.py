from shapely.geometry import Polygon
from shapely.geometry import Point
import geopandas as gpd

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
wyp_radius = 0.05

point_WYP_CASTEJON = Point((-2.54461, 40.37195))
poly_WYP_CASTEJON = point_WYP_CASTEJON.buffer(wyp_radius)
waypoints_dict['CASTEJON'] = poly_WYP_CASTEJON

point_WYP_PERALES = Point((-3.34820, 40.25223))
poly_WYP_PERALES = point_WYP_PERALES.buffer(wyp_radius)
waypoints_dict['PERALES'] = poly_WYP_PERALES

point_WYP_NAVAS = Point((-4.24741, 40.36867))
poly_WYP_NAVAS = point_WYP_NAVAS.buffer(wyp_radius)
waypoints_dict['NAVAS'] = poly_WYP_NAVAS

point_WYP_VILLATOBAS = Point((-3.46860, 39.77804))
poly_WYP_VILLATOBAS = point_WYP_VILLATOBAS.buffer(wyp_radius)
waypoints_dict['VILLATOBAS'] = poly_WYP_VILLATOBAS

point_WYP_ROBLEDILLO = Point((-3.24728, 40.85277))
poly_WYP_ROBLEDILLO = point_WYP_ROBLEDILLO.buffer(wyp_radius)
waypoints_dict['ROBLEDILLO'] = poly_WYP_ROBLEDILLO

point_WYP_SOMOSIERRA = Point((-3.60816, 41.15260))
poly_WYP_SOMOSIERRA = point_WYP_SOMOSIERRA.buffer(wyp_radius)
waypoints_dict['SOMOSIERRA'] = poly_WYP_SOMOSIERRA

point_WYP_COLMENAR_VIEJO = Point((-3.73534, 40.64548))
poly_WYP_COLMENAR_VIEJO = point_WYP_COLMENAR_VIEJO.buffer(wyp_radius)
waypoints_dict['COLMENAR_VIEJO'] = poly_WYP_COLMENAR_VIEJO

point_WYP_TOLEDO = Point((-4.33705, 39.96818))
poly_WYP_TOLEDO = point_WYP_TOLEDO.buffer(wyp_radius)
waypoints_dict['TOLEDO'] = poly_WYP_TOLEDO

point_WYP_SALAMANCA = Point((-5.45569, 41.01655))
poly_WYP_SALAMANCA = point_WYP_SALAMANCA.buffer(wyp_radius)
waypoints_dict['SALAMANCA'] = poly_WYP_SALAMANCA

point_WYP_ZAMORA = Point((-5.63972, 41.53014))
poly_WYP_ZAMORA = point_WYP_ZAMORA.buffer(wyp_radius)
waypoints_dict['ZAMORA'] = poly_WYP_ZAMORA

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
waypoints_dict['TABANERA'] = poly_WYP_TABANERA

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
waypoints_dict['BARAHONA'] = poly_WYP_BARAHONA

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
waypoints_dict['CACERES'] = poly_WYP_CACERES

point_WYP_LONGA = Point((-4.87592, 40.43643))
poly_WYP_LONGA = point_WYP_LONGA.buffer(wyp_radius)
waypoints_dict['LONGA'] = poly_WYP_LONGA

point_WYP_NANDO = Point((-2.17385, 39.98835))
poly_WYP_NANDO = point_WYP_NANDO.buffer(wyp_radius)
waypoints_dict['NANDO'] = poly_WYP_NANDO

# Runways

point_32L = Point(-3.554039, 40.463237)
point_32R = Point(-3.536341, 40.473727)
point_18L = Point(-3.559349, 40.527936)
point_18R = Point(-3.574792, 40.522701)

runway_ths_dict = {}
runway_ths_dict['32L'] = (-3.554039, 40.463237)
runway_ths_dict['32R'] = (-3.536341, 40.473727)
runway_ths_dict['18L'] = (-3.559349, 40.527936)
runway_ths_dict['18R'] = (-3.574792, 40.522701)



