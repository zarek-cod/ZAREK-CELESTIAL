
"""Verify editable/optimized geometry, UV atlas, export payloads and real-mesh R15 fit."""
from pathlib import Path
from math import cos, sin, tau
from collections import defaultdict
import hashlib
import json
import struct

import bpy
import bmesh
from mathutils.bvhtree import BVHTree

A=Path(__file__).resolve().parents[1]
FIT=A.parent/"02-eternal-halo/blender/EternalHalo_R15_DivineCrown.blend"
MANNEQUIN=A.parents[1]/"referencias/oficiales/ClassicMannequin.fbx"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def mesh_data(objects):
    verts,faces,names=[],[],[]
    deps=bpy.context.evaluated_depsgraph_get()
    for source in objects:
        o=source.evaluated_get(deps)
        me=o.to_mesh()
        me.calc_loop_triangles()
        offset=len(verts)
        verts.extend(o.matrix_world@v.co for v in me.vertices)
        faces.extend(tuple(i+offset for i in t.vertices) for t in me.loop_triangles)
        names.extend([source.name]*len(me.loop_triangles))
        o.to_mesh_clear()
    return verts,faces,names


def bvh(g):
    return BVHTree.FromPolygons(g[0],g[1],all_triangles=True,epsilon=0)


def bounds(vv):
    return [[round(f(v[k] for v in vv),6) for k in range(3)] for f in (min,max)]


def open_variant(name):
    bpy.ops.wm.open_mainfile(filepath=str(A/f"blender/CelestialHair_{name}.blend"))
    return [o for o in bpy.context.scene.objects if o.type=="MESH"]


def stats(objects):
    out=dict(meshes=len(objects),vertices=0,triangles=0,shells=0,
             nonmanifold_edges=0,boundary_edges=0,degenerate_faces=0,inconsistent_edge_winding=0,inward_shells=0)
    for o in objects:
        m=o.data
        m.calc_loop_triangles()
        out["vertices"]+=len(m.vertices)
        out["triangles"]+=len(m.loop_triangles)
        bm=bmesh.new()
        bm.from_mesh(m)
        out["nonmanifold_edges"]+=sum(not e.is_manifold for e in bm.edges)
        out["boundary_edges"]+=sum(e.is_boundary for e in bm.edges)
        out["inconsistent_edge_winding"]+=sum(e.is_manifold and not e.is_contiguous for e in bm.edges)
        out["degenerate_faces"]+=sum(f.calc_area()<1e-10 for f in bm.faces)
        pool=set(bm.faces)
        while pool:
            stack=[pool.pop()]
            vol=0.0
            while stack:
                face=stack.pop()
                vv=face.verts
                vol+=sum(vv[0].co.dot(vv[j].co.cross(vv[j+1].co))/6 for j in range(1,len(vv)-1))
                for edge in face.edges:
                    for other in edge.link_faces:
                        if other in pool:
                            pool.remove(other)
                            stack.append(other)
            out["shells"]+=1
            out["inward_shells"]+=vol<=0
        bm.free()
    for key in ("nonmanifold_edges","boundary_edges","inconsistent_edge_winding","degenerate_faces","inward_shells"):
        assert out[key]==0,(key,out[key])
    return out


def area(poly):
    return sum(x[0]*y[1]-x[1]*y[0] for x,y in zip(poly,poly[1:]+poly[:1]))*.5


def intersect_area(subject,clip):
    for p,q in zip(clip,clip[1:]+clip[:1]):
        if not subject:
            return 0
        def dist(x):
            return (q[0]-p[0])*(x[1]-p[1])-(q[1]-p[1])*(x[0]-p[0])
        output=[]
        for x,y in zip(subject,subject[1:]+subject[:1]):
            dx,dy=dist(x),dist(y)
            if dx*dy<0:
                a=dx/(dx-dy)
                output.append((x[0]+a*(y[0]-x[0]), x[1]+a*(y[1]-x[1])))
            if dy>=0:
                output.append(y)
        subject=output
    return abs(area(subject))


def check_uv(o):
    m=o.data
    assert len(m.uv_layers)==1 and len(m.materials)==1 and len(m.color_attributes)==0
    m.calc_loop_triangles()
    uv=m.uv_layers.active.data
    tile=defaultdict(list)
    for tri in m.loop_triangles:
        poly=[tuple(uv[i].uv) for i in tri.loops]
        assert all(0<=c<=1 for v in poly for c in v),poly
        signed=area(poly)
        assert abs(signed)>1e-11,poly
        if signed<0:
            poly.reverse()
        keys={(int(v[0]*6),int(v[1]*6)) for v in poly}
        assert len(keys)==1,keys
        tile[keys.pop()].append((min(p[0] for p in poly),max(p[0] for p in poly),
                               min(p[1] for p in poly),max(p[1] for p in poly),poly))
    overlap=[]
    for key,triangles in tile.items():
        byx=sorted(triangles,key=lambda r:r[0])
        for i,(x0,x1,y0,y1,p) in enumerate(byx):
            for a,b,c,d,q in byx[i+1:]:
                if a>=x1-1e-8:
                    break
                if c<y1-1e-8 and d>y0+1e-8:
                    overlap_area=intersect_area(p,q)
                    if overlap_area>5e-9:
                        overlap.append((key,overlap_area))
    assert not overlap,overlap[:10]
    return dict(uv_sets=1,tiles=len(tile),positive_area_overlap_pairs_above_5e_9=0,
                out_of_range_coords=0,degenerate_uv_triangles=0)


def read_glb(path):
    data=path.read_bytes()
    magic,version,size,n,kind=struct.unpack_from("<4sIII4s",data)
    assert (magic,version,size,kind)==(b"glTF",2,len(data),b"JSON")
    doc=json.loads(data[20:20+n])
    assert len(doc["meshes"])==len(doc["materials"])==len(doc["meshes"][0]["primitives"])==1
    mat=doc["materials"][0]
    pbr=mat["pbrMetallicRoughness"]
    assert pbr["metallicFactor"]==0
    assert mat.get("alphaMode","OPAQUE")=="OPAQUE" and not mat.get("doubleSided",False)
    refs={"ColorMap":pbr["baseColorTexture"]["index"],"NormalMap":mat["normalTexture"]["index"],
          "RoughnessPacked":pbr["metallicRoughnessTexture"]["index"]}
    result={}
    for label,tex in refs.items():
        img=doc["images"][doc["textures"][tex]["source"]]
        chunk=doc["bufferViews"][img["bufferView"]]
        offset=28+n+chunk.get("byteOffset",0)
        raw=data[offset:offset+chunk["byteLength"]]
        assert raw.startswith(b"\x89PNG\r\n\x1a\n")
        result[label]=list(struct.unpack_from(">II",raw,16))
    assert result=={"ColorMap":[1024,1024],"NormalMap":[256,256],"RoughnessPacked":[256,256]},result
    return {"image_dimensions":result,"metallic_factor":0,"backface_culling":True}


def roundtrip(expected):
    out={}
    for ext in ("fbx","glb"):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        path=A/f"exportaciones/CelestialHair_UGC.{ext}"
        if ext=="fbx":
            bpy.ops.import_scene.fbx(filepath=str(path),use_anim=False)
        else:
            bpy.ops.import_scene.gltf(filepath=str(path))
        meshes=[obj for obj in bpy.context.scene.objects if obj.type=="MESH"]
        assert len(meshes)==1
        assert len(meshes[0].data.uv_layers)==len(meshes[0].data.materials)==1
        g=mesh_data(meshes)
        lim=bounds(g[0])
        assert len(g[1])==len(expected[1])
        assert max(abs(a-b) for a,b in zip(sum(lim,[]),sum(bounds(expected[0]),[])))<1e-4
        out[ext]={"triangles":len(g[1]),"meshes":1,"bounds_blender_xyz":lim,"sha256":sha(path)}
        if ext=="glb":
            out[ext]["pbr_payload"]=read_glb(path)
    return out


def compare(g1,g2,nearest=True):
    t1,t2=bvh(g1),bvh(g2)
    pairs=t1.overlap(t2)
    out={"crossing_triangle_pairs":len(pairs)}
    if nearest:
        out["sampled_min_vertex_surface_distance_studs"]=round(
             min(min(t2.find_nearest(v)[3] for v in g1[0]),min(t1.find_nearest(v)[3] for v in g2[0])),6)
    return out,pairs


def front_visibility(head,hair):
    h,t=bvh(head),bvh(hair)
    results={}
    # Rectangles bracket the visible eye relief on the official Classic mannequin
    # in these coordinates, with margins excluded for the eyebrows and temples.
    regions={"left_eye":(-.37,-.13,-.705,-.563),"right_eye":(.13,.37,-.705,-.563),
             "central_future_mask_area":(-.35,.35,-.98,-.79)}
    for name,(x0,x1,z0,z1) in regions.items():
        samples=occluded=0
        for j in range(10):
            z=z0+(z1-z0)*(j+.5)/10
            for i in range(12):
                x=x0+(x1-x0)*(i+.5)/12
                origin=(x,-2.,z)
                target=h.ray_cast(origin,(0,1,0),3)[3]
                if target is not None:
                    samples+=1
                    occluded+=t.ray_cast(origin,(0,1,0),target-.0002)[0] is not None
        results[name]={"tested":samples,"hair_occlusions":occluded,"xz_bounds":[x0,x1,z0,z1]}
    return results


def scalp_coverage(head, hair):
    skull, locks = bvh(head), bvh(hair)
    heights = [-.02, -.06, -.10, -.14, -.18, -.22, -.26, -.30]
    angles_per_height = 96
    tested = uncovered = 0
    for height in heights:
        for i in range(angles_per_height):
            angle = tau * i / angles_per_height
            direction = (cos(angle), sin(angle), 0)
            origin = (-2 * direction[0], -2 * direction[1], height)
            distance = skull.ray_cast(origin, direction, 3)[3]
            if distance is not None:
                tested += 1
                uncovered += locks.ray_cast(origin, direction, distance - .0002)[0] is None
    return {"tested": tested, "uncovered": uncovered, "sampled_z": heights,
            "angles_per_height": angles_per_height}


def points_near_regions(hair):
    # These are relative volumes to facilitate planning later accessories.
    # They assert nothing about missing mask or earrings geometries.
    slots={"left_lobe":(-.60,-.02,-1.00),"right_lobe":(.60,-.02,-1.00)}
    tree=bvh(hair)
    return {name:{"sample_position":xyz,"nearest_surface_studs":round(tree.find_nearest(xyz)[3],6)}
            for name,xyz in slots.items()}


def main():
    ugc=open_variant("UGC")
    report={"blender":bpy.app.version_string,"UGC":stats(ugc)}
    assert len(ugc)==1 and report["UGC"]["triangles"]<=4000
    report["atlas"]=check_uv(ugc[0])
    g=mesh_data(ugc)
    lim=bounds(g[0])
    assert lim[0][0]>=-1.5 and lim[1][0]<=1.5
    assert lim[0][2]>=-3 and lim[1][2]<=2
    # In the asset, -Y is front and +Y is behind.
    assert lim[0][1]>=-1.5 and lim[1][1]<=2.0
    report["classic_Hair"]={"bounds_blender_xyz":lim,"dimensions_roblox_xyz":[round(lim[1][i]-lim[0][i],6) for i in (0,2,1)],
                           "conditional_max_X_up_down_front_back":[3,2,3,1.5,2],"reference_HairAttachment_blender":[0,0,0]}
    report["exports"]=roundtrip(g)
    master=open_variant("MASTER")
    report["MASTER"]=stats(master)
    hi=mesh_data(master)
    bpy.ops.wm.open_mainfile(filepath=str(FIT))
    head=mesh_data([bpy.data.objects["Head_Geo"]])
    crown=mesh_data([bpy.data.objects["DivineCrown_UGC"]])
    halo=mesh_data([bpy.data.objects["EternalHalo_UGC"]])
    body=mesh_data([o for o in bpy.context.scene.objects if o.name.endswith("_Geo") and o.name!="Head_Geo"])
    report["fit_reference"]={"source_blend_sha256":sha(FIT),"mannequin_fbx_sha256":sha(MANNEQUIN),
                             "mode":"Static Blender fit. Independently created Studio RBXL attachments not used."}
    report["fit"]={}
    for name,geo in [("UGC",g),("MASTER",hi)]:
        result={}
        for k,ob in [("head",head),("crown",crown),("halo",halo),("body_excluding_head",body)]:
            result[k],pairs=compare(geo,ob,k!="body_excluding_head")
            if k=="head":
                affected=[geo[0][index] for i,_ in pairs for index in geo[1][i]]
                result[k]["hair_triangle_bounds_blender_xyz"]=bounds(affected) if affected else None
                result[k]["intended_contact"]= "Concealed root/scalp fit; check visible head and eye regions separately."
                if name=="MASTER":
                    result[k]["root_or_lock_names"]=sorted({geo[2][i] for i,_ in pairs})
            elif pairs:
                print("FIT CROSSING",name,k,[geo[2][i] for i,_ in pairs[:20]],flush=True)
        result["visibility_sampling"]=front_visibility(head,geo)
        result["scalp_coverage"]=scalp_coverage(head,geo)
        result["ear_space_samples"]=points_near_regions(geo)
        report["fit"][name]=result
    report["maps"]={}
    for p in (A/"texturas").glob("*.png"):
        data=p.read_bytes()
        w,h,depth,channels=struct.unpack_from(">IIBB",data,16)
        assert w==h==(1024 if "BaseColor" in p.name else 256) and depth==8
        assert channels==(0 if "Roughness" in p.name else 2)
        report["maps"][p.name]={"dimensions":[w,h],"format":"grayscale" if channels==0 else "RGB","sha256":sha(p)}
    output=json.dumps(report,ensure_ascii=False,indent=2)
    (A/"validacion/resultados.json").write_text(output+"\n",encoding="utf-8")
    print(output)
    for name,result in report["fit"].items():
        for k in ("crown","halo","body_excluding_head"):
            assert result[k]["crossing_triangle_pairs"]==0,(name,k,result[k])
        assert all(s["hair_occlusions"]==0 for s in result["visibility_sampling"].values()),(name,result["visibility_sampling"])
        cover=result["scalp_coverage"]
        assert cover["tested"] == len(cover["sampled_z"]) * cover["angles_per_height"]
        assert cover["uncovered"] == 0, (name, cover)
    print("CELESTIAL_HAIR_QA_PASS",flush=True)


if __name__=="__main__":
    main()
