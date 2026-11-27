
"""Rebuild Celestial Hair V2 from sculpted asymmetric ribbon sections."""
from dataclasses import dataclass
from pathlib import Path
from math import cos, sin, pi, tau, hypot, exp
import struct
import sys
import zlib

import bpy
import bmesh
import numpy as np
from mathutils import Vector

A=Path(__file__).resolve().parents[1]
GRID=6
PADDING=.061
BLUE_ACCENTS={0,4,7,10,13,20,24,28}


@dataclass(frozen=True)
class Ribbon:
    name: str
    group: str
    spine: tuple
    widths: tuple
    lift: float
    outward: tuple
    rolls: tuple
    segments: int
    sides: int


def ribbon(name,group,spine,widths,lift,outward,rolls,segments=8,sides=8):
    return Ribbon(name,group,spine,widths,lift,outward,rolls,segments,sides)


# Sculpted flow paths in stud coordinates, -Y forward. Intermediate points define
# outward hooks and directional changes. Widths and roll vary along every lock.
RIBBONS=[
    ribbon("01 · Left crest swept off the brow","Fringe",
           ((.27,-.095,.106),(.20,-.362,.152),(-.047,-.58,-.117),(-.43,-.701,-.327),(-.76,-.610,-.369),(-.927,-.491,-.297)),
           (.022,.146,.168,.129,.054,0),.064,(0,-.83,.58),(-.11,.08,.25,.54,.80,1.16),10),
    ribbon("02 · Long central curtain","Fringe",
           ((.323,-.104,.104),(.359,-.37,.089),(.266,-.553,-.169),(.171,-.686,-.307),(.045,-.683,-.454),(-.035,-.624,-.525)),
           (.025,.130,.156,.132,.057,0),.065,(.08,-1,.43),(.15,.04,-.15,-.23,-.37,-.62)),
    ribbon("03 · Crossed blade over left eye","Fringe",
           ((.097,-.16,.076),(.031,-.414,.043),(-.087,-.55,-.177),(-.277,-.655,-.327),(-.472,-.634,-.450),(-.598,-.528,-.431)),
           (.021,.126,.143,.118,.051,0),.056,(-.18,-1,.34),(-.16,.06,.18,.32,.72,1.12)),
    ribbon("04 · Right split rising at tip","Fringe",
           ((.27,-.116,.05),(.438,-.344,.039),(.47,-.471,-.254),(.562,-.598,-.400),(.726,-.531,-.471),(.890,-.393,-.358)),
           (.019,.119,.16,.137,.061,0),.056,(.37,-1,.40),(-.03,-.22,-.38,-.62,-.84,-1.18)),
    ribbon("05 · Fine center strand","Fringe",
           ((.149,-.15,.05),(.11,-.416,-.046),(.101,-.595,-.220),(.005,-.681,-.363),(-.100,-.635,-.501)),
           (.020,.094,.123,.085,0),.054,(.03,-1,.40),(.23,.10,.25,.41,.79)),
    ribbon("06 · Clear right eye sweep","Fringe",
           ((.372,-.135,.048),(.429,-.39,-.11),(.466,-.55,-.224),(.366,-.625,-.360),(.327,-.561,-.459)),
           (.025,.108,.125,.084,0),.057,(.45,-.88,.34),(-.22,-.34,-.22,.17,.41)),
    ribbon("07 · Left low flare","Fringe",
           ((-.16,-.176,.072),(-.28,-.375,-.100),(-.451,-.560,-.247),(-.628,-.578,-.424),(-.829,-.458,-.521),(-.988,-.377,-.438)),
           (.019,.127,.132,.106,.059,0),.064,(-.57,-1,.38),(.0,.17,.34,.63,.84,1.28)),
    ribbon("08 · Right low flare","Fringe",
           ((.449,-.091,.04),(.512,-.295,-.12),(.539,-.488,-.307),(.666,-.550,-.506),(.832,-.427,-.553),(.974,-.287,-.451)),
           (.024,.113,.137,.112,.053,0),.067,(.62,-.88,.43),(-.02,-.27,-.51,-.74,-.89,-1.21)),
    ribbon("09 · Left face frame","Fringe",
           ((-.274,-.12,.081),(-.41,-.347,-.105),(-.493,-.483,-.33),(-.595,-.471,-.636),(-.724,-.345,-.736),(-.822,-.27,-.700)),
           (.022,.114,.141,.094,.041,0),.060,(-.67,-.89,.29),(.0,.09,.22,.43,.73,.99),7),
    ribbon("10 · Right face frame","Fringe",
           ((.30,-.116,.046),(.496,-.311,-.133),(.560,-.472,-.407),(.584,-.447,-.659),(.648,-.332,-.748),(.739,-.267,-.718)),
           (.024,.119,.133,.091,.045,0),.060,(.76,-.79,.30),(-.08,-.21,-.35,-.62,-.93,-1.15),7),
    ribbon("11 · Left crest wing","Temples",
           ((-.359,.082,.101),(-.521,-.071,-.141),(-.714,-.266,-.412),(-.853,-.294,-.493),(-1.018,-.210,-.407)),
           (.021,.159,.169,.118,0),.071,(-.87,-.43,.31),(-.15,.04,.35,.67,1.02),7,6),
    ribbon("12 · Left broken wave","Temples",
           ((-.406,.31,.035),(-.569,.194,-.191),(-.711,.027,-.439),(-.846,-.077,-.618),(-.989,-.065,-.561)),
           (.020,.144,.161,.093,0),.065,(-.92,.13,.38),(-.04,.19,.52,.81,1.17),7,6),
    ribbon("13 · Left sideburn","Temples",
           ((-.403,-.075,-.035),(-.548,-.161,-.323),(-.636,-.267,-.53),(-.677,-.27,-.794),(-.751,-.185,-.859)),
           (.016,.11,.123,.071,0),.065,(-.91,-.34,.18),(.03,.19,.31,.54,1.0),7,6),
    ribbon("14 · Left behind the ear","Temples",
           ((-.428,.253,-.005),(-.605,.31,-.28),(-.692,.247,-.516),(-.713,.17,-.811),(-.826,.164,-.774)),
           (.019,.116,.131,.081,0),.063,(-.90,.44,.22),(0,.21,.46,.64,.97),7,6),
    ribbon("15 · Right crest wing","Temples",
           ((.306,.093,.146),(.539,-.056,-.108),(.661,-.222,-.391),(.825,-.242,-.464),(.990,-.137,-.358)),
           (.021,.137,.151,.094,0),.065,(.87,-.43,.40),(.2,.02,-.24,-.63,-.92),7,6),
    ribbon("16 · Right broken wave","Temples",
           ((.376,.279,.017),(.559,.202,-.203),(.719,.055,-.430),(.858,.014,-.584),(.995,.07,-.498)),
           (.022,.130,.16,.09,0),.069,(.92,.22,.36),(0,-.24,-.4,-.78,-1.09),7,6),
    ribbon("17 · Right sideburn","Temples",
           ((.407,-.109,-.09),(.538,-.152,-.334),(.631,-.235,-.55),(.668,-.26,-.827),(.721,-.162,-.87)),
           (.016,.103,.115,.076,0),.067,(.94,-.34,.23),(0,-.29,-.37,-.72,-.99),7,6),
    ribbon("18 · Right behind the ear","Temples",
           ((.416,.297,.04),(.584,.364,-.239),(.678,.27,-.497),(.737,.20,-.805),(.842,.227,-.725)),
           (.021,.113,.144,.093,0),.060,(.90,.46,.27),(.15,-.07,-.32,-.55,-1.08),7,6),
    ribbon("19 · Left nape outer fall","Nape",
           ((-.303,.244,.120),(-.501,.404,-.069),(-.599,.576,-.362),(-.637,.646,-.584),(-.745,.590,-.873),(-.796,.552,-.755)),
           (.025,.146,.181,.151,.067,0),.079,(-.62,.89,.28),(.11,.21,.36,.52,.64,.94)),
    ribbon("20 · Long left cascade","Nape",
           ((-.193,.32,.107),(-.351,.514,-.076),(-.447,.666,-.309),(-.446,.746,-.605),(-.520,.694,-.875),(-.606,.650,-.952)),
           (.022,.150,.181,.153,.079,0),.084,(-.52,.99,.29),(-.18,.04,.27,.38,.68,.94)),
    ribbon("21 · Left braid-shaped fall","Nape",
           ((-.089,.288,.103),(-.23,.495,-.060),(-.258,.663,-.284),(-.340,.749,-.552),(-.283,.753,-.856),(-.391,.684,-.973)),
           (.018,.152,.151,.139,.071,0),.082,(-.28,1,.28),(-.23,-.09,.09,.38,.04,.65)),
    ribbon("22 · Nape center hidden carry","Nape",
           ((.025,.322,.106),(-.083,.542,-.046),(-.066,.698,-.333),(-.112,.780,-.583),(-.084,.729,-.896),(-.185,.658,-.997)),
           (.022,.145,.171,.139,.065,0),.087,(-.05,1,.28),(-.12,-.33,-.22,.13,.35,.58)),
    ribbon("23 · Silver central fall","Nape",
           ((.166,.277,.119),(.149,.483,-.074),(.165,.656,-.307),(.112,.762,-.564),(.153,.775,-.839),(.084,.712,-1.018)),
           (.020,.150,.171,.159,.076,0),.084,(.08,1,.33),(.16,.03,-.13,-.22,.05,.34)),
    ribbon("24 · Long right cascade","Nape",
           ((.209,.234,.083),(.326,.435,-.082),(.364,.600,-.325),(.354,.744,-.549),(.422,.746,-.835),(.371,.704,-.962)),
           (.021,.126,.154,.142,.074,0),.086,(.29,1,.29),(-.03,-.13,-.30,-.49,-.32,-.72)),
    ribbon("25 · Outer right cascade","Nape",
           ((.335,.238,.100),(.461,.404,-.117),(.515,.574,-.33),(.532,.686,-.56),(.629,.629,-.856),(.737,.561,-.842)),
           (.020,.148,.181,.151,.068,0),.083,(.50,1,.26),(.15,-.12,-.25,-.46,-.75,-1.04)),
    ribbon("26 · Right nape last flare","Nape",
           ((.393,.175,.103),(.558,.322,-.118),(.613,.474,-.375),(.679,.562,-.565),(.759,.533,-.763),(.855,.464,-.725)),
           (.016,.132,.138,.141,.063,0),.077,(.75,1,.26),(.0,-.17,-.26,-.45,-.56,-.94)),
    ribbon("27 · Crown flow left","Crown flow",
           ((.223,.125,.130),(-.002,.151,.286),(-.268,.120,.239),(-.438,-.078,.103),(-.547,-.320,-.290)),
           (.023,.157,.185,.138,0),.072,(-.29,-.17,1),(.17,.0,.34,.6,.92),7,6),
    ribbon("28 · Crown flow back","Crown flow",
           ((.105,-.203,.139),(.023,.024,.262),(-.036,.309,.203),(-.043,.540,-.035),(-.172,.654,-.380)),
           (.025,.151,.176,.103,0),.072,(-.12,.31,1),(-.09,.12,.29,.58,.87),7,6),
    ribbon("29 · Crown flow right","Crown flow",
           ((.075,-.215,.135),(.246,-.024,.260),(.421,.164,.184),(.567,.353,-.035),(.632,.52,-.402)),
           (.020,.146,.173,.129,0),.065,(.36,.17,1),(0,-.15,-.35,-.57,-.98),7,6),
    ribbon("30 · Left part and tuck","Crown flow",
           ((.204,.008,.196),(.035,-.15,.287),(-.171,-.325,.191),(-.321,-.512,-.041),(-.542,-.64,-.337)),
           (.023,.135,.154,.118,0),.066,(-.34,-.21,1),(.13,.02,.29,.62,1.12),7,6),
    ribbon("31 · Left stray strand","Flyaways",
           ((-.286,-.382,-.183),(-.449,-.622,-.310),(-.682,-.607,-.393),(-.834,-.485,-.400),(-.962,-.358,-.310)),
           (.009,.037,.046,.026,0),.031,(-.37,-1,.38),(.05,.31,.62,1,1.4),5,6),
    ribbon("32 · Right stray strand","Flyaways",
           ((.397,-.386,-.175),(.527,-.522,-.318),(.703,-.565,-.421),(.859,-.420,-.426),(.964,-.305,-.312)),
           (.010,.039,.052,.028,0),.034,(.44,-1,.43),(.02,-.19,-.62,-1,-1.28),5,6),
    ribbon("33 · Rear silver strand","Flyaways",
           ((-.275,.471,-.073),(-.378,.636,-.242),(-.469,.748,-.428),(-.487,.757,-.621),(-.543,.754,-.758)),
           (.009,.042,.05,.032,0),.040,(-.32,1,.39),(-.07,.21,.31,.53,.71),5,6),
    ribbon("34 · Left nape connective ribbon","Nape",
           ((-.425,.485,-.33),(-.506,.651,-.523),(-.527,.735,-.702),(-.481,.727,-.867),(-.539,.662,-.995)),
           (.010,.092,.110,.069,0),.046,(-.51,.91,.17),(0,.12,.24,.12,.65),5,6),
    ribbon("35 · Right nape connective ribbon","Nape",
           ((.30,.55,-.361),(.425,.686,-.55),(.504,.746,-.708),(.497,.744,-.848),(.593,.658,-.959)),
           (.013,.096,.104,.064,0),.049,(.55,.98,.27),(.09,-.09,-.28,-.36,-.64),4,6),
]


def ease(a,b,x):
    t=np.clip((x-a)/(b-a),0,1)
    return t*t*(3-2*t)


def uv(i,u,v):
    return ((i%GRID+PADDING+u*(1-2*PADDING))/GRID,
            (i//GRID+PADDING+v*(1-2*PADDING))/GRID)


def ring_clearance(vertex):
    # Keep the comb under the fixed inner metal rim, then allow expansion beneath it.
    t=float(ease(.242,.410,-vertex.z))
    x_radius=.683+.380*t
    y_radius=.610+.294*t
    scale=hypot(vertex.x/x_radius,vertex.y/y_radius)
    # Monotone soft compression preserves separation between layered surfaces.
    # A hard projection would make neighboring locks coplanar against the rim.
    start=.790
    if scale>start:
        soft=start+(1-start)*(1-exp(-(scale-start)/(1-start)))
        vertex.x*=soft/scale
        vertex.y*=soft/scale
    radius=hypot(vertex.x,vertex.y)
    # Keep the visible comb above the fitted underlayer without widening the tips.
    # The fixed crown's oval is more generous at the temples than at the forehead.
    guard=float(ease(.35,.495,radius)*ease(.061,-.069,vertex.z)*(1-ease(.185,.340,-vertex.z)))
    if guard>0:
        limit=.605+.056*abs(vertex.x/radius)**1.76
        outward=.86*guard*max(0.0,limit-radius)
        factor=1+outward/radius
        vertex.x*=factor
        vertex.y*=factor
    return vertex


def handles(path):
    return [(path[min(i+1,len(path)-1)]-path[max(0,i-1)])*(1/6 if 0<i<len(path)-1 else 1/3)
            for i in range(len(path))]


def frame(spec,t):
    path=[Vector(c) for c in spec.spine]
    guides=handles(path)
    samples=len(path)-1
    a=min(samples-1,int(t*samples))
    f=t*samples-a
    p0,p3=path[a],path[a+1]
    p1=p0+guides[a]
    p2=p3-guides[a+1]
    k=1-f
    p=k**3*p0+3*k*k*f*p1+3*k*f*f*p2+f**3*p3
    direction=(3*k*k*(p1-p0)+6*k*f*(p2-p1)+3*f*f*(p3-p2)).normalized()
    normal=Vector(spec.outward)
    normal=(normal-direction*normal.dot(direction)).normalized()
    side=direction.cross(normal).normalized()
    tilt=(1-f)*spec.rolls[a]+f*spec.rolls[a+1]+.06*sin(pi*t*2)
    width=(1-f)*spec.widths[a]+f*spec.widths[a+1]
    return p,side*cos(tilt)+normal*sin(tilt),normal*cos(tilt)-side*sin(tilt),width,direction


def grain(u,t,index):
    # The same curved flow drives the geometry and the color channels.
    bend=.31*np.sin(t*7.4+index*.47)+.29*np.sin(t*4.7-index*.81)
    a=tau*u
    grouped=.58*np.cos(a*12+bend+index*.81)+.29*np.cos(a*19-bend*.7)
    fine=.33*np.sin(a*34+bend*2.4+index)+.17*np.cos(a*43-bend*2)
    return grouped,fine


def cross_sections(s,ix,high):
    # More vertices on the visible folded surface. The backside remains a smooth closure.
    if high:
        return np.arange(64)/64
    if s.sides==8:
        return [0,.063,.128,.205,.294,.405,.5,.75]
    return [0,.081,.182,.315,.5,.75]


def make_ribbon(s,ix,high):
    uu=cross_sections(s,ix,high)
    cols=len(uu)
    n=48 if high else s.segments
    # Every UGC section is sampled from the sculpt. Extra concentration is carried
    # by the hand-picked section count of the hero locks, while the tip is a separate pole.
    samples=np.linspace(.035,.948,n)
    if not high:
        times=np.linspace(.035,.958,111)
        frames=[frame(s,float(t)) for t in times]
        points=[ring_clearance(f[0].copy()) for f in frames]
        measure=[0]
        for j in range(1,len(times)):
            arc=(points[j]-points[j-1]).length
            bend=frames[j][4].angle(frames[j-1][4],0)
            guard=.0015*float(np.exp(-((points[j].z+.167)/.088)**2))
            measure.append(measure[-1]+arc+.062*bend+guard)
        samples=np.interp(np.linspace(0,measure[-1],n),measure,times)
    span=samples[-1]-samples[0]
    vertices=[]
    for t in samples:
        p,side,out,width,_=frame(s,float(t))
        for u in uu:
            angle=tau*u
            shoulder=max(0.0,sin(angle))
            x=cos(angle)
            elevation=(.39*shoulder+.61*shoulder**1.65) if shoulder>0 else sin(angle)*.53
            elevation+=.23*shoulder*sin(angle*3.35+s.rolls[1]+.8*t)
            elevation-=.13*np.exp(-((u-.31+.053*sin(t*pi))/.054)**2)
            depth_envelope=.14+.95*sin(pi*(min(.97,t)**.84))**.66
            depth_envelope*=1-float(ease(.69,1,t))*.92
            if high:
                small,micro=grain(u,t,ix)
                elevation+=(.123*small+.057*micro)*shoulder**.52*sin(t*pi)**.59
            skew=.33*width*sin(t*4.5+ix*.61)*(1-x*x)*sin(pi*t)
            vertices.append(ring_clearance(p+side*(width*x+skew)+out*(s.lift*depth_envelope*elevation)))
    tip=len(vertices)
    vertices.append(ring_clearance(Vector(s.spine[-1])))
    root=len(vertices)
    vertices.append(ring_clearance(Vector(s.spine[0])))
    faces=[]
    xy=[]
    def add(vertices_,coords):
        faces.append(vertices_)
        xy.append([uv(ix,u,v) for u,v in coords])
    for j,u0 in enumerate(uu):
        u1=uu[j+1] if j+1<cols else 1
        k=(j+1)%cols
        add((root,k,j),((.5,0),(u1,.040),(u0,.040)))
        for r in range(n-1):
            v0=.04+.91*(samples[r]-samples[0])/span
            v1=.04+.91*(samples[r+1]-samples[0])/span
            add((r*cols+j,r*cols+k,(r+1)*cols+k,(r+1)*cols+j),
                ((u0,v0),(u1,v0),(u1,v1),(u0,v1)))
        r=(n-1)*cols
        add((r+j,r+k,tip),((u0,.95),(u1,.95),((u0+u1)*.5,1)))
    return vertices,faces,xy


def make_mass(index,high):
    """Connected closed scalp sculpture shaped under the comb flow."""
    n=112 if high else 24
    # Absolute upper rings follow the Classic skull dome. Descending hairline
    # rings conform to the front, temples and nape independently.
    upper=[(.136,.282),(.043,.507),(-.041,.579),(-.143,.588)]
    if high:
        heights=np.linspace(upper[0][0], upper[-1][0], 17)
        radii=np.interp(heights, [z for z,_ in upper[::-1]], [r for _,r in upper[::-1]])
        upper=list(zip(heights,radii))
    lower=np.linspace(.074,1,13).tolist() if high else [.37,.71,1]
    sections=[(z,r,0) for z,r in upper]+[(None,.588,t) for t in lower]+[(None,.474,1.075)]
    vertices=[]
    for z_ref,r,t in sections:
        for j in range(n):
            theta=tau*j/n
            front=.5+.5*cos(theta)
            terminal=-.96+.555*front**1.16+.034*cos(theta*7)+.024*sin(theta*11+.8)
            z=z_ref if z_ref is not None else -.143+(terminal+.143)*min(t,1)
            if t>1:
                z+=.047
            groove_amplitude=float(ease(.055,-.31,z))
            groove=groove_amplitude*(.010*cos(16*theta+.74*t)+.007*sin(24*theta+1.5*t))
            flow=max(0.0,float(ease(-.20,-.45,z)))*(1-front)*min(t,1)
            x=(r+.006+groove+.038*flow)*sin(theta)
            y=-(r+groove+.082*flow)*cos(theta)
            vertices.append(Vector((x,y,z)))
    top=len(vertices)
    bottom=top+1
    vertices.extend((Vector((0,.012,.194)),Vector((0,.012,-.376))))
    faces=[]
    xy=[]
    def add(f,vs):
        faces.append(f)
        xy.append([uv(index,u,v) for u,v in vs])
    for j in range(n):
        k=(j+1)%n
        a,b=j/n,(j+1)/n
        add((top,j,k),((.5,0),(a,.035),(b,.035)))
        for r in range(len(sections)-1):
            v=.035+.922*r/(len(sections)-1)
            w=.035+.922*(r+1)/(len(sections)-1)
            add((r*n+j,(r+1)*n+j,(r+1)*n+k,r*n+k),((a,v),(a,w),(b,w),(b,v)))
        r=(len(sections)-1)*n
        add((r+j,bottom,r+k),((a,.957),(.5,1),(b,.957)))
    return vertices,faces,xy


def png(path,array):
    height,width=array.shape[:2]
    kind=2 if array.ndim==3 else 0
    def chunk(name,data):
        return struct.pack(">I",len(data))+name+data+struct.pack(">I",zlib.crc32(name+data))
    payload=b"".join(b"\0"+row.tobytes() for row in array[::-1])
    header=struct.pack(">IIBBBBB",width,height,8,kind,0,0,0)
    path.write_bytes(b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",header)+chunk(b"IDAT",zlib.compress(payload,9))+chunk(b"IEND",b""))


def texture_arrays(size):
    y,x=np.mgrid[:size,:size].astype(np.float32)
    x=(x+.5)/size*GRID
    y=(y+.5)/size*GRID
    index=x.astype(np.int32)+y.astype(np.int32)*GRID
    u=np.clip((x%1-PADDING)/(1-2*PADDING),0,1)
    v=np.clip((y%1-PADDING)/(1-2*PADDING),0,1)
    outer=np.maximum(0,np.sin(tau*u))
    inner=np.maximum(0,-np.sin(tau*u))
    grouped,fine=grain(u,v,index)
    # Mix in sRGB so neutral white stays dominant and dark lining is in the exported atlas.
    palette=lambda triple: np.asarray(triple,dtype=np.float32)
    deep=palette((8,15,30))
    shade=palette((100,118,157))
    silver=palette((184,201,232))
    white=palette((247,250,254))
    snow=palette((255,255,255))
    root_light=ease(.035,.30,v)
    tip=ease(.70,1,v)
    bright=ease(.14,.83,outer)
    fiber=(grouped*.68+fine*.32)
    pearl=np.clip(.49+.30*bright+.14*fiber+.13*np.sin(u*35-v*1.2+index*.61),0,1)
    ribbon_light=.47+.36*np.sin(tau*u*2.8 + .29*np.sin(v*8+index*.37))+ .13*fiber
    ribbon_light=np.clip(ribbon_light,0,1)
    rgb=silver+(white-silver)*(pearl*.61+.39*ribbon_light)[:,:,None]
    rgb=rgb+(snow-rgb)*(.20*bright*ease(.34,.72,v))[:,:,None]
    edge_gap=np.where(inner>0,.38+.54*(1-inner)**1.7,.91*(1-ease(.035,.205,outer)))
    edge_break=.93+.07*np.cos(v*15+index)
    fiber_shadow=(.074+.100*(1-ribbon_light))*np.clip(-grouped+.45,0,1)
    shade_amount=(.29*(1-bright)+fiber_shadow)[:,:,None]
    rgb=rgb+(shade-rgb)*shade_amount
    rgb=rgb+(deep-rgb)*(edge_gap*edge_break*(1-.21*tip))[:,:,None]
    root_amp=(1-root_light)*(.47+.37*(1-bright))
    rgb=rgb+(deep-rgb)*root_amp[:,:,None]
    electric=np.isin(index,list(BLUE_ACCENTS))
    azure=electric*np.exp(-((outer-.239)/.126)**2) * (.065+.20*tip) * ease(.36,.77,v)
    rgb=rgb+(palette((0,71,255))-rgb)*azure[:,:,None]
    cap=index==len(RIBBONS)
    cap_channels=.35+.23*np.cos(tau*u*13+v*5)+.14*np.cos(tau*u*22-v*3)
    cap_mid=.37+.42*(1-ease(.26,.95,v))+.27*cap_channels
    color_cap=palette((22,33,58))+(palette((168,190,226))-palette((22,33,58)))*cap_mid[:,:,None]
    rgb[cap]=color_cap[cap]
    rough=np.clip(.47+edge_gap*.18+root_amp*.07-.07*pearl+.026*fiber,.34,.68)
    rough[cap]=.58+.04*cap_channels[cap]
    return np.clip(rgb+.5,0,255).astype(np.uint8),np.clip(rough*255+.5,0,255).astype(np.uint8)


def object_mesh(name,data,collection):
    v,f,xy=data
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(v,[],f)
    mesh.update()
    lay=mesh.uv_layers.new(name="FiberAtlas")
    for face,uvs in zip(mesh.polygons,xy):
        face.use_smooth=True
        for loop,pos in zip(face.loop_indices,uvs):
            lay.data[loop].uv=pos
    bm=bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    if bm.calc_volume(signed=True)<0:
        bmesh.ops.reverse_faces(bm,faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj=bpy.data.objects.new(name,mesh)
    collection.objects.link(obj)
    return obj


def group(name):
    c=bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c


def select(objects):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]


def join(objects,name):
    select(objects)
    bpy.ops.object.join()
    obj=bpy.context.object
    obj.name=name
    return obj


def triangulate(obj):
    select([obj])
    mod=obj.modifiers.new("UGC tangent basis","TRIANGULATE")
    mod.quad_method="FIXED"
    mod.ngon_method="BEAUTY"
    mod.keep_custom_normals=True
    bpy.ops.object.modifier_apply(modifier=mod.name)


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version=0
    bpy.context.scene.unit_settings.system="NONE"


def make_objects(high):
    objects=[]
    cols={}
    for i,s in enumerate(RIBBONS):
        if s.group not in cols:
            cols[s.group]=group(s.group)
        obj=object_mesh(s.name,make_ribbon(s,i,high),cols[s.group])
        obj["UV tile"]=i
        obj["Role"]=s.group
        objects.append(obj)
    obj=object_mesh("Scalp · continuous underlayer",make_mass(len(RIBBONS),high),group("Scalp"))
    obj["UV tile"]=len(RIBBONS)
    objects.append(obj)
    return objects


def add_guides():
    guide_group=group("Bézier guides · show to edit paths")
    for item in RIBBONS:
        data=bpy.data.curves.new(item.name,"CURVE")
        data.dimensions="3D"
        data.resolution_u=24
        spline=data.splines.new("BEZIER")
        spline.bezier_points.add(len(item.spine)-1)
        path=[Vector(p) for p in item.spine]
        for j,(point,co,tangent) in enumerate(zip(spline.bezier_points,path,handles(path))):
            point.co=co
            point.handle_left_type="FREE"
            point.handle_right_type="FREE"
            point.handle_left=co-tangent
            point.handle_right=co+tangent
            point.tilt=item.rolls[j]
            point.radius=max(.003,item.widths[j])
        obj=bpy.data.objects.new("Guide / "+item.name,data)
        guide_group.objects.link(obj)
        obj.hide_set(True)
        obj.hide_render=True


def material(variant,with_normal=True):
    mat=bpy.data.materials.new("V2 · celestial silver fibers "+variant)
    mat.diffuse_color=(.70,.77,.90,1)
    mat.use_backface_culling=True
    nt=mat.node_tree
    shader=nt.nodes.get("Principled BSDF")
    shader.inputs["Metallic"].default_value=0
    shader.inputs["IOR"].default_value=1.47
    shader.inputs["Specular IOR Level"].default_value=.31
    maps=[("BaseColor",shader.inputs["Base Color"],"sRGB"),("Roughness",shader.inputs["Roughness"],"Non-Color")]
    if with_normal and variant=="UGC":
        node=nt.nodes.new("ShaderNodeNormalMap")
        node.location=(-290,-200)
        node.uv_map="FiberAtlas"
        node.inputs["Strength"].default_value=.78
        nt.links.new(node.outputs[0],shader.inputs["Normal"])
        maps.append(("Normal",node.inputs["Color"],"Non-Color"))
    if variant=="MASTER":
        tangent=nt.nodes.new("ShaderNodeTangent")
        tangent.direction_type="UV_MAP"
        tangent.uv_map="FiberAtlas"
        nt.links.new(tangent.outputs[0],shader.inputs["Tangent"])
        shader.inputs["Anisotropic"].default_value=.26
        shader.inputs["Anisotropic Rotation"].default_value=.25
        shader.inputs["Sheen Weight"].default_value=.10
    for i,(name,socket,space) in enumerate(maps):
        img=bpy.data.images.load(str(A/"texturas"/f"CelestialHair_{name}.png"),check_existing=True)
        img.colorspace_settings.name=space
        img.pack()
        node=nt.nodes.new("ShaderNodeTexImage")
        node.image=img
        node.name=name
        node.location=(-630,380-i*280)
        nt.links.new(node.outputs["Color"],socket)
    return mat


def named_anchor():
    anchor=bpy.data.objects.new("HairAttachment · Classic placement guide",None)
    anchor.empty_display_type="ARROWS"
    anchor.empty_display_size=.13
    bpy.context.scene.collection.objects.link(anchor)
    bpy.context.scene["Units"]="One Blender unit is one stud; +Z up, -Y facing."
    bpy.context.scene["Asset"]="ZAREK Celestial Hair V2"
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=="VIEW_3D":
                v=area.spaces.active
                v.region_3d.view_rotation=Vector((-.49,1,-.31)).to_track_quat("-Z","Y")
                v.region_3d.view_distance=3.7
                v.region_3d.view_location=(0,0,-.32)
                v.shading.color_type="MATERIAL"


def save(variant):
    named_anchor()
    bpy.ops.wm.save_as_mainfile(filepath=str(A/"blender"/f"CelestialHair_{variant}.blend"),compress=True)


def bake_normal(high_meshes,low_meshes):
    # Move corresponding sculpt and low-mesh pieces together. Neighbors can no longer
    # project their normals into one another when the strands cross in the hairstyle.
    high=[]
    low=[]
    for i,(source,target) in enumerate(zip(high_meshes,low_meshes)):
        shift=Vector((3.0*(i%GRID),3.0*(i//GRID),0))
        for original,destination in [(source,high),(target,low)]:
            copy=bpy.data.objects.new(original.name+" · bake",original.data.copy())
            bpy.context.scene.collection.objects.link(copy)
            copy.location=shift
            destination.append(copy)
    source=join(high,"Exploded high sculpt")
    target=join(low,"Exploded low cage")
    triangulate(target)
    bake_mat=bpy.data.materials.new("Tangent output")
    texture=bake_mat.node_tree.nodes.new("ShaderNodeTexImage")
    image=bpy.data.images.new("V2 normal bake 1024",1024,1024,alpha=True,float_buffer=False)
    image.colorspace_settings.name="Non-Color"
    texture.image=image
    texture.select=True
    bake_mat.node_tree.nodes.active=texture
    target.data.materials.append(bake_mat)
    scene=bpy.context.scene
    scene.render.engine="CYCLES"
    scene.cycles.device="CPU"
    scene.cycles.samples=4
    select([target,source])
    bpy.ops.object.bake(type="NORMAL",normal_space="TANGENT",use_selected_to_active=True,
                        max_ray_distance=.230,cage_extrusion=.071,margin=7,margin_type="EXTEND",
                        normal_r="POS_X",normal_g="POS_Y",normal_b="POS_Z",use_clear=True)
    image.filepath_raw=str(A/"work/v2/bake_1024_raw.png")
    image.file_format="PNG"
    image.save()
    pixels=np.asarray(image.pixels[:],dtype=np.float32).reshape(256,4,256,4,4)
    xyz=pixels[:,:,:,:,:3]*2-1
    good=(pixels[:,:,:,:,3]>.2)&(xyz[:,:,:,:,2]>-.2)
    sample_weights=np.where(good,1,.0)[:,:,:,:,None]
    mean=(xyz*sample_weights).sum(axis=(1,3))
    weight=sample_weights.sum(axis=(1,3))
    assert np.count_nonzero(weight)>15000,np.count_nonzero(weight)
    mean/=np.maximum(1,weight)
    lengths=np.linalg.norm(mean,axis=2,keepdims=True)
    mean/=np.maximum(.001,lengths)
    mean[weight[:,:,0]==0]=[0,0,1]
    final=np.rint(np.clip(mean*.5+.5,0,1)*255).astype(np.uint8)
    png(A/"texturas/CelestialHair_Normal.png",final)
    print("V2_NORMAL_BAKE_PASS",dict(source_polygons=sum(len(s.data.polygons) for s in high_meshes),
                                    texels_with_valid_normal_256=int(np.count_nonzero(weight)),method="selected to active, tangent, isolated pairs"),flush=True)


def export(obj):
    select([obj])
    root=A/"exportaciones/CelestialHair_UGC"
    bpy.ops.export_scene.fbx(filepath=str(root.with_suffix(".fbx")),use_selection=True,
        object_types={"MESH"},apply_scale_options="FBX_SCALE_UNITS",axis_forward="-Z",axis_up="Y",
        bake_space_transform=True,path_mode="COPY",embed_textures=True,bake_anim=False)
    bpy.ops.export_scene.gltf(filepath=str(root.with_suffix(".glb")),use_selection=True,export_format="GLB",
        export_yup=True,export_apply=True,export_animations=False)


def main():
    mode=sys.argv[sys.argv.index("--")+1] if "--" in sys.argv else "full"
    for folder in ("blender","texturas","exportaciones","work/v2"):
        (A/folder).mkdir(parents=True,exist_ok=True)
    base,_=texture_arrays(1024)
    _,rough=texture_arrays(256)
    png(A/"texturas/CelestialHair_BaseColor.png",base)
    png(A/"texturas/CelestialHair_Roughness.png",rough)
    reset()
    high=make_objects(True)
    mat=material("MASTER")
    for o in high:
        o.data.materials.append(mat)
    add_guides()
    select(high[:1])
    save("MASTER")
    if mode=="sculpt":
        return
    # Build an isolated bake scene before building and serializing the export model.
    reset()
    if mode=="full":
        high=make_objects(True)
        low=make_objects(False)
        bake_normal(high,low)
    reset()
    low=make_objects(False)
    obj=join(low,"CelestialHair_UGC")
    triangulate(obj)
    obj.data.name="CelestialHair V2 rigid mesh"
    obj.data.calc_loop_triangles()
    print("V2_UGC_TRIANGLES",len(obj.data.loop_triangles),flush=True)
    assert len(obj.data.loop_triangles)<=4000
    obj.data.materials.append(material("UGC",mode!="preview"))
    save("UGC")
    if mode!="preview":
        export(obj)
    print("V2_BUILD_PASS",flush=True)


if __name__=="__main__":
    main()
