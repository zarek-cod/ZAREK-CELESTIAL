"""Artist-authored volume stations for the three Celestial Hair V3 sculpts.

Blender coordinates in studs. Front is -Y. Each station is (X,Y,Z,half-width,depth).
Side and rear stations use bearing, radial distance, height, width and depth.
"""
from math import cos, sin, radians


def xyz(name, zone, stations, color=0, roll=0):
    return name, zone, stations, color, roll


def around(name, zone, stations, color=0, roll=0):
    points = [(r*sin(radians(a)), -r*cos(radians(a)), z, w, d) for a,r,z,w,d in stations]
    return xyz(name, zone, points, color, roll)


def fall(name, bearing, sweep, length, wide, radial, color=0, lift=0):
    return around(name, "Nuca", [
        (bearing-sweep*1.35,.25,.230,.045,.035),
        (bearing-sweep*.86,.429,.158,.79*wide,.064),
        (bearing-sweep*.52,.533,.020,wide,.064),
        (bearing-sweep*.22,.566,-.19,wide*.90,.069),
        (bearing,radial-.087,-.48,wide*.75,.066),
        (bearing+sweep*.46,radial-.063,length+.20,wide*.45,.045),
        (bearing+sweep,radial,length+lift,.005,.006),
    ], color, sweep*.010)


def wing(name, bearing, sweep, end, radius, width, color=0):
    return around(name, "Sienes", [
        (bearing-2*sweep,.228,.257,.025,.026),
        (bearing-1.36*sweep,.407,.193,.82*width,.069),
        (bearing-.91*sweep,.529,.015,width,.074),
        (bearing-.47*sweep,.552,-.187,.94*width,.077),
        (bearing,radius-.132,min(end-.11,-.435),.67*width,.055),
        (bearing+sweep*.56,radius-.063,end-.072,.33*width,.030),
        (bearing+sweep*.98,radius,end,.004,.004),
    ], color, sweep*.012)


def crown(name,bearing,sweep,peak=0,color=0):
    return around(name,"Coronilla",[
        (bearing-sweep*3,.07,.281,.035,.04),
        (bearing-sweep*2,.195,.309+peak,.092,.054),
        (bearing-sweep,.344,.276+peak,.106,.056),
        (bearing,.465,.165,.079,.037),
        (bearing+sweep,.533,.075,.004,.005),
    ],color,sweep*.012)


A = [
    xyz("A · Cortina larga izquierda","Flequillo",[
        (-.025,-.103,.293,.035,.040),(-.224,-.291,.264,.128,.067),(-.395,-.438,.159,.147,.077),
        (-.480,-.296,-.127,.150,.076),(-.561,-.470,-.397,.131,.092),(-.656,-.518,-.665,.083,.049),
        (-.745,-.349,-.826,.004,.004)],0,.32),
    xyz("A · Seda sobre la sien izquierda","Flequillo",[
        (-.068,-.126,.276,.035,.029),(-.291,-.365,.219,.099,.054),(-.465,-.365,.048,.109,.062),
        (-.527,-.246,-.213,.086,.056),(-.670,-.408,-.519,.078,.062),(-.802,-.334,-.710,.004,.004)],1,.24),
    xyz("A · Cortina derecha exterior","Flequillo",[
        (.021,-.139,.267,.031,.033),(.146,-.361,.239,.107,.066),(.283,-.457,.106,.131,.067),
        (.317,-.442,-.156,.117,.071),(.467,-.571,-.346,.131,.085),(.632,-.545,-.568,.066,.053),
        (.819,-.385,-.606,.004,.004)],0,-.33),
    xyz("A · Flequillo interior en diagonal","Flequillo",[
        (.022,-.209,.219,.032,.037),(.217,-.433,.187,.107,.065),(.323,-.473,.047,.119,.073),
        (.251,-.541,-.169,.113,.062),(.155,-.642,-.343,.092,.074),(.045,-.676,-.503,.004,.004)],0,-.30),
    xyz("A · Separación de la raya","Flequillo",[
        (-.085,-.207,.263,.025,.038),(-.133,-.470,.184,.089,.051),(-.224,-.542,.024,.103,.063),
        (-.232,-.570,-.166,.095,.055),(-.383,-.593,-.350,.076,.047),(-.487,-.527,-.480,.004,.004)],2,.23),
    xyz("A · Hebra curva derecha","Flequillo",[
        (.100,-.187,.274,.022,.024),(.320,-.380,.224,.083,.042),(.469,-.394,.059,.092,.060),
        (.508,-.317,-.188,.100,.055),(.603,-.562,-.388,.077,.053),(.760,-.424,-.560,.004,.004)],1,-.37),
    xyz("A · Mechón largo detrás de la derecha","Flequillo",[
        (.151,-.164,.242,.022,.025),(.385,-.289,.152,.089,.052),(.533,-.151,-.075,.096,.066),
        (.566,-.249,-.276,.092,.071),(.641,-.359,-.552,.068,.060),(.665,-.277,-.838,.004,.004)],0,-.30),
]
A += [wing("A · "+name,a,s,z,r,w,c) for name,a,s,z,r,w,c in [
    ("Ala de seda izquierda",-75,-17,-.425,.931,.128,0),("Onda media izquierda",-93,-9,-.595,.895,.115,1),
    ("Onda inferior izquierda",-114,14,-.792,.885,.098,0),("Curva detrás de oreja izquierda",-134,15,-.878,.802,.102,2),
    ("Ala de seda derecha",70,17,-.440,.910,.122,0),("Onda media derecha",96,11,-.626,.870,.102,0),
    ("Onda inferior derecha",114,-8,-.804,.851,.116,1),("Curva detrás de oreja derecha",134,10,-.853,.812,.118,2),
]]
A += [fall("A · "+name,a,s,z,w,r,c) for name,a,s,z,w,r,c in [
    ("Velo posterior I",120,-12,-1.005,.120,.745,1),("Velo posterior II",138,-20,-1.094,.143,.750,0),
    ("Cascada larga derecha",154,-12,-1.161,.135,.717,0),("Hilo interno derecho",166,4,-1.110,.106,.675,2),
    ("Nuca central abierta",179,13,-1.154,.149,.664,0),("Cascada larga izquierda",200,7,-1.195,.149,.671,0),
    ("Velo posterior III",214,-1,-1.005,.121,.764,1),("Velo posterior IV",227,10,-1.075,.123,.803,0),
    ("Mechón junto a la nuca",241,18,-.961,.100,.748,2),
]]
A += [crown(f"A · Raíz aérea {i}",a,s,p) for i,(a,s,p) in enumerate([(-83,-17,.032),(67,20,.008),(110,18,.024),(167,13,.024),(211,-19,.029),(250,-19,.01)],1)]


B = [
    xyz("B · Diagonal de tormenta","Flequillo",[
        (.179,-.035,.288,.043,.045),(.123,-.291,.279,.128,.076),(-.104,-.487,.179,.162,.084),
        (-.283,-.484,-.054,.151,.082),(-.445,-.589,-.307,.136,.086),(-.599,-.553,-.460,.073,.062),
        (-.791,-.449,-.362,.005,.004)],0,.39),
    xyz("B · Punta central negra y plata","Flequillo",[
        (.257,-.115,.252,.047,.041),(.216,-.350,.190,.110,.065),(.174,-.520,.108,.126,.067),
        (.180,-.556,-.131,.133,.069),(.117,-.619,-.371,.083,.065),(.008,-.622,-.541,.004,.005)],2,-.42),
    xyz("B · Curva lateral baja","Flequillo",[
        (.305,-.154,.222,.040,.041),(.423,-.354,.149,.127,.071),(.443,-.380,-.082,.128,.072),
        (.578,-.342,-.291,.125,.080),(.666,-.506,-.529,.094,.059),(.833,-.364,-.482,.004,.004)],0,-.52),
    xyz("B · Fleco corto izquierdo","Flequillo",[
        (.023,-.160,.222,.025,.026),(-.191,-.376,.168,.108,.061),(-.355,-.438,-.059,.116,.067),
        (-.456,-.452,-.278,.092,.067),(-.579,-.503,-.487,.060,.050),(-.701,-.373,-.571,.005,.004)],1,.30),
    xyz("B · Mechón fino al ojo derecho","Flequillo",[
        (.179,-.160,.172,.026,.030),(.295,-.394,.119,.098,.059),(.354,-.452,-.072,.103,.066),
        (.382,-.500,-.308,.078,.065),(.358,-.541,-.442,.004,.004)],0,-.31),
]
B += [wing("B · "+name,a,s,z,r,w,c) for name,a,s,z,r,w,c in [
    ("Sien alta alzada izquierda",-67,-25,-.356,.887,.126,1),("Gancho oscuro izquierdo",-91,-23,-.490,.936,.116,2),
    ("Lateral en dos alturas",-116,-12,-.687,.875,.108,0),("Patilla izquierda",-55,-6,-.813,.748,.105,0),
    ("Sien alta hacia atrás",78,19,-.374,.889,.129,0),("Gancho azul derecho",105,19,-.494,.934,.123,2),
    ("Reverso plata derecho",127,8,-.667,.876,.103,0),("Patilla derecha",54,7,-.776,.751,.106,1),
]]
B += [fall("B · "+name,a,s,z,w,r,c,l) for name,a,s,z,w,r,c,l in [
    ("Nuca lateral derecha",130,-7,-.887,.116,.795,2,.055),("Nuca en arco derecha",145,-14,-1.009,.127,.774,0,.005),
    ("Interior de ceniza",158,-5,-1.050,.107,.688,2,0),("Nuca barrida",175,19,-1.136,.160,.691,0,0),
    ("Centro de plata",188,12,-1.056,.135,.758,1,.015),("Cascada alzada izquierda",203,14,-1.021,.115,.784,0,.06),
    ("Interior izquierdo",224,8,-1.010,.105,.734,2,0),("Mechón de cierre",239,14,-.907,.109,.795,0,.03),
]]
B += [crown(f"B · Cresta {i}",a,s,p,c) for i,(a,s,p,c) in enumerate([
    (-100,-20,.050,0),(-50,-16,.012,2),(63,22,.064,0),(119,18,.053,0),(159,21,.058,1),
    (204,22,.027,0),(241,17,.015,2)
],1)]


C = [
    xyz("C · Diagonal blanca principal","Flequillo",[
        (.106,-.116,.265,.052,.045),(.005,-.351,.245,.133,.073),(-.154,-.506,.127,.164,.083),
        (-.310,-.467,-.096,.159,.078),(-.474,-.541,-.310,.139,.077),(-.690,-.524,-.450,.072,.053),
        (-.911,-.349,-.388,.004,.004)],0,.42),
    xyz("C · Punta irregular hacia el entrecejo","Flequillo",[
        (.222,-.168,.229,.039,.038),(.235,-.392,.184,.120,.067),(.241,-.516,.052,.122,.075),
        (.203,-.538,-.175,.108,.073),(.152,-.648,-.359,.089,.071),(.039,-.648,-.532,.004,.004)],0,-.37),
    xyz("C · Cinta interior de plata","Flequillo",[
        (.089,-.152,.222,.022,.027),(-.030,-.407,.162,.088,.052),(-.106,-.539,.024,.103,.062),
        (-.154,-.540,-.202,.106,.069),(-.230,-.611,-.391,.065,.052),(-.368,-.581,-.465,.004,.004)],1,.27),
    xyz("C · Ala derecha del flequillo","Flequillo",[
        (.237,-.136,.242,.043,.031),(.352,-.314,.203,.116,.066),(.407,-.393,.053,.123,.070),
        (.425,-.389,-.173,.128,.073),(.565,-.566,-.363,.118,.073),(.741,-.508,-.484,.051,.053),
        (.886,-.404,-.425,.004,.004)],0,-.47),
    xyz("C · Púa intermedia derecha","Flequillo",[
        (.308,-.148,.211,.036,.036),(.373,-.311,.146,.090,.062),(.433,-.402,-.029,.104,.063),
        (.401,-.462,-.221,.097,.064),(.398,-.548,-.410,.077,.051),(.473,-.517,-.537,.004,.004)],1,-.31),
    xyz("C · Patilla larga izquierda","Flequillo",[
        (-.175,-.079,.215,.036,.040),(-.370,-.252,.155,.095,.068),(-.471,-.327,-.063,.121,.070),
        (-.501,-.304,-.251,.130,.072),(-.577,-.441,-.522,.080,.066),(-.627,-.413,-.803,.004,.005)],0,.43),
    xyz("C · Patilla larga derecha","Flequillo",[
        (.245,-.078,.212,.033,.034),(.434,-.212,.151,.094,.064),(.494,-.272,-.054,.112,.073),
        (.533,-.272,-.258,.111,.073),(.598,-.439,-.527,.080,.063),(.665,-.366,-.803,.004,.005)],0,-.36),
    xyz("C · Hilo eléctrico lateral","Flequillo",[
        (-.194,-.133,.232,.025,.025),(-.381,-.333,.135,.075,.047),(-.494,-.330,-.085,.078,.057),
        (-.522,-.277,-.226,.081,.063),(-.687,-.458,-.475,.059,.057),(-.875,-.347,-.519,.004,.004)],1,.49),
]
C += [wing("C · "+name,a,s,z,r,w,c) for name,a,s,z,r,w,c in [
    ("Puntas izquierda I",-76,-18,-.402,.949,.132,0),("Puntas izquierda II",-96,-13,-.543,.965,.111,1),
    ("Puntas izquierda III",-111,13,-.687,.902,.116,0),("Ala izquierda baja",-128,16,-.804,.853,.107,0),
    ("Puntas derecha I",74,22,-.410,.932,.128,0),("Puntas derecha II",94,12,-.549,.941,.122,1),
    ("Puntas derecha III",111,-8,-.707,.891,.112,0),("Ala derecha baja",135,-9,-.801,.852,.111,0),
]]
C += [fall("C · "+name,a,s,z,w,r,c,l) for name,a,s,z,w,r,c,l in [
    ("Nuca barrida a derecha",126,-8,-.924,.115,.811,1,.02),("Nuca derecha exterior",139,-13,-1.098,.119,.795,0,0),
    ("Nuca derecha profunda",151,-6,-1.064,.137,.755,0,0),("Nuca derecha central",165,-8,-1.146,.133,.709,1,0),
    ("Nuca plata central",177,10,-1.132,.145,.718,0,0),("Nuca desfasada",191,9,-1.106,.132,.743,0,0),
    ("Nuca izquierda central",204,10,-1.160,.131,.736,1,0),("Nuca izquierda profunda",219,12,-1.032,.119,.785,0,.02),
    ("Nuca izquierda exterior",233,15,-.984,.123,.797,0,.05),
]]
C += [around(f"C · Transición posterior {i}","Nuca superior",[
    (a-s*2,.235,.245,.043,.038),(a-s,.427,.172,.097,.060),
    (a,.530,.018,.111,.061),(a+s*.45,.566,-.199,.100,.065),
    (a+s,.696,-.424,.075,.057),(a+s*1.6,.744,z,.004,.005),
],color,s*.015) for i,(a,s,z,color) in enumerate([
    (140,-18,-.530,0),(160,-11,-.591,1),(186,12,-.661,0),(204,19,-.576,0),(226,15,-.512,0),
],1)]
C += [crown(f"C · Dirección superior {i}",a,s,p) for i,(a,s,p) in enumerate([
    (-108,-19,.018),(-63,-18,.019),(58,24,.035),(111,18,.023),(160,-16,.02),(202,22,.022),(242,15,.028),
],1)]

def canopy(name,a,s,z,width,color=0,sweep=.72):
    return around(name,"Coronilla exterior",[
        (a-s*3,.110,.302,.026,.023),
        (a-s*2,.237,.324,.70*width,.063),
        (a-s,.394,.255,width,.073),
        (a-s*.43,.499,.157,.92*width,.069),
        (a,.556,-.052,.82*width,.060),
        (a+s*.48,.672,-.345,.61*width,.063),
        (a+s*sweep,.789,z,.004,.004),
    ],color,s*.012)


A += [canopy(f"A · Superposición sedosa {i}",a,s,z,w,c) for i,(a,s,z,w,c) in enumerate([
    (-124,-19,-.478,.098,0),(-150,-14,-.541,.094,0),(-177,-13,-.577,.090,1),
    (159,12,-.540,.094,0),(128,18,-.490,.089,0),(94,25,-.365,.100,0),
    (43,18,-.279,.081,0),(-36,-20,-.273,.080,0)
],1)]
B = [ (name,zone,[(x,y,z+(.115*max(0,-z-.42) if zone=="Nuca" and x<.13 else 0),w,d) for x,y,z,w,d in stations],c,roll)
      for name,zone,stations,c,roll in B ]
B += [canopy(f"B · Coronilla barrida {i}",a,s,z,w,c) for i,(a,s,z,w,c) in enumerate([
    (-119,-27,-.529,.103,2),(-143,-20,-.510,.107,0),(-171,-19,-.614,.104,1),
    (160,31,-.469,.115,0),(132,26,-.408,.102,0),(112,17,-.371,.094,2),
    (49,-25,-.295,.109,0),(-38,-23,-.361,.088,2)
],1)]
C = [ (name,zone,[(x,y,z+(.14*max(0,-z-.35) if zone=="Nuca" else 0),w,d) for x,y,z,w,d in stations],c,roll)
      for name,zone,stations,c,roll in C ]
C += [canopy(f"C · Superposición de plata {i}",a,s,z,w,c) for i,(a,s,z,w,c) in enumerate([
    (-127,-23,-.526,.110,0),(-147,-18,-.607,.105,1),(-172,-19,-.622,.110,0),
    (174,16,-.604,.114,0),(151,17,-.572,.095,0),(118,24,-.483,.104,0),
    (-47,-25,-.345,.086,0),(38,23,-.334,.085,1)
],1)]


A.append(xyz("A · Hebra larga entre las cortinas","Flequillo",[
    (-.065,-.145,.254,.023,.025),(-.05,-.362,.210,.067,.052),(-.077,-.497,.108,.077,.063),
    (-.108,-.554,-.075,.074,.069),(-.109,-.592,-.260,.060,.052),(-.017,-.657,-.493,.004,.004)
],0,.30))

# B is shorter on the avatar's right, with one dark sweep below the lifted temple.
B = [
    (name, zone, [
        (x-0.037*max(0,-z-.46),y,z+(.28*max(0,-z-.34) if x>.49 and zone in {"Sienes","Nuca"} else 0),w,d)
        for x,y,z,w,d in stations
    ],color,roll)
    for name,zone,stations,color,roll in B
]
B.append(around("B · Remolino curvo de la nuca","Nuca superior",[
    (143,.269,.243,.024,.027),(161,.476,.161,.087,.072),(178,.552,-.071,.128,.071),
    (190,.562,-.259,.132,.073),(217,.707,-.499,.095,.064),(238,.799,-.438,.004,.005)
],2,.37))


DESIGNS = {
    "A": ("Angelical", A),
    "B": ("Celestial oscuro", B),
    "C": ("Concepto ZAREK", C),
}
