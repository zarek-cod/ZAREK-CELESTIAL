"""Refine the Celestial Hair V4 sculpt and sample its evaluated surface for UGC."""
from pathlib import Path
import argparse
import json
import math
import sys

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform

ASSET = Path(__file__).resolve().parents[1]
HAIR = ASSET.parent
WORK = HAIR / "work/v5"
STEM = "CelestialHair_V5"
sys.path.insert(0, str(HAIR / "v4/scripts"))
import build_v4 as v4

sculpt = v4.sculpt
smooth = sculpt.smooth
v4.ASSET, v4.STEM = ASSET, STEM

# Main silhouettes get 64 samples per lock, mid layers 49, and sheltered locks 30.
HERO = {0, 1, 3, 4, 5, 6, 12, 13, 17, 19, 20, 22, 37, 39}
MID = {8, 9, 10, 14, 18, 21, 23, 38, 41, 43}
HIDDEN = {25, 27, 28, 30, 32, 33, 35, 36}


def refine():
    recipe = []
    for index, (name, zone, knots, pigment, roll) in enumerate(v4.refine_recipe()):
        stations = []
        for i, (x, y, z, width, depth) in enumerate(knots):
            t = i / (len(knots) - 1)
            if index in {2, 7}:
                # Restore the slimmer overlapping fringe layers from C.
                forward = float(smooth(-.25, -.45, z)) * (1 - float(smooth(.82, 1, t)))
                y -= (.025 if index == 2 else .010) * forward
                width *= 1 + .075 * math.sin(math.pi * t)
                if index == 2:
                    fan = math.sin(math.pi * t) ** 2
                    x += .050 * fan
                    width *= 1 + .22 * fan
                    depth *= 1 + .19 * fan
            if zone == "Nuca":
                fall = float(smooth(.23, 1, t))
                z += (.089 + .018 * math.cos(index * 2.37)) * fall
                fullness = math.sin(math.pi * t) ** 2
                width *= 1 + .08 * fullness
                depth *= 1 + .18 * fullness
                y += (.015 + .006 * math.sin(index)) * fullness
            if zone == "Nuca superior":
                z += .023 * float(smooth(.40, 1, t))
                depth *= 1.08
            if zone in {"Coronilla exterior", "Coronilla"}:
                z -= (.046 if index in HIDDEN else .023) * (1 - float(smooth(.10, .50, t)))
                depth *= 1 + .065 * math.sin(math.pi * t)
            stations.append((x, y, z, width, depth))
        recipe.append((name, zone, stations, pigment, roll))
    return recipe


def shape(name, positions, mapping, sides, tile, collection, material, level):
    if name.startswith("Base"):
        # Set the dome below the top locks and retain a continuous side hairline.
        for row in positions:
            center_z = sum(p.z for p in row) / sides
            dome = float(smooth(-.025, .24, center_z))
            nape = float(smooth(-.40, -.87, center_z))
            for p in row:
                p.x *= 1 - .035 * dome
                p.y *= 1 - .032 * dome
                p.z -= .052 * dome
                hairline = float(smooth(.135, -.18, center_z) * (1 - smooth(.42, .78, -center_z)))
                front = float(smooth(.13, .45, -p.y))
                rear = float(smooth(.18, .50, p.y))
                p.y *= 1 - (.024 * front + .039 * rear) * hairline
                p.z += .016 * front * float(smooth(-.27, -.46, center_z))
                p.z += .038 * nape * float(smooth(.04, .48, p.y))
    else:
        extra = .077 if tile in {40, 41} else .043 if tile in {2, 3, 21, 26, 29} else .013
        for row in positions:
            center = sum(row, Vector()) / sides
            radial = Vector((center.x, center.y, 0))
            amount = extra * float(smooth(.33, .52, radial.length))
            amount *= float(smooth(.15, .005, center.z) * (1 - smooth(.20, .50 if tile in {40, 41} else .43, -center.z)))
            if radial.length > .01:
                shift = radial.normalized() * amount
                for p in row:
                    p -= shift
    return v4.inset_control(name, positions, mapping, sides, tile, collection, material, level)


def textures(recipe):
    y, x = np.mgrid[:1024, :1024].astype(np.float32)
    xx, yy = (x + .5) * 7 / 1024, (y + .5) * 7 / 1024
    tile = xx.astype(np.int16) + 7 * yy.astype(np.int16)
    u = np.clip((xx % 1 - .042) / .916, 0, 1)
    t = np.clip((yy % 1 - .042) / .916, 0, 1)
    side = (u + .5) % 1 - .5
    phase = tile * .671
    twist = .011 * np.sin(t * 5 + phase) * np.sin(t * np.pi)
    shoulder = np.abs(side + twist)
    flow = u * math.tau + .055 * np.sin(6 * t + phase) + .018 * np.sin(14 * t - phase)
    sweep = np.cos(flow * 8 + phase) * .60 + np.sin(flow * 13 - phase * .83) * .31
    fibres = .57 * np.cos(flow * 23 - 2.7 * t + phase) + .29 * np.cos(flow * 37 + phase)
    fine = .71 * np.sin(flow * 47 + phase + t * 5) + .29 * np.cos(flow * 65 + phase)
    ridge = .54 + .46 * np.cos((side + twist - .053 * np.sin(phase)) * 19)
    silver = np.array([161, 178, 206], dtype=np.float32)
    porcelain = np.array([247, 249, 255], dtype=np.float32)
    steel = smooth(.047, .222, shoulder)
    sheen = np.clip(1.01 - .37 * steel + .205 * sweep + .154 * fibres + .060 * fine + .14 * ridge, 0, 1)
    color = silver + (porcelain - silver) * sheen[:, :, None]

    # Paint the turn of each lock into blue shadow, then place a fine black edge
    # on the visible shoulder. The stripe moves with the longitudinal UV flow.
    root = (1 - smooth(.028, .285, t)) * .91
    trough = smooth(.155, .310, shoulder)
    dark = np.array([15, 23, 48], dtype=np.float32)
    weight = np.clip(root + trough * (.72 + .15 * sweep) + .16 * steel * (1 - ridge), 0, .965)
    color = color + (dark - color) * weight[:, :, None]
    edge_center = .146 + .010 * np.sin(4 * t + phase) + .010 * np.sin(t * np.pi) + .019 * (side < 0)
    edge_width = .010 + .005 * np.sin(t * np.pi)
    ink = np.exp(-((shoulder - edge_center) / edge_width) ** 2)
    ink *= smooth(.20, .46, t) * (1 - .40 * smooth(.97, 1, t)) * (.76 + .17 * ridge) * np.where(side < 0, .86, 1.)
    color += (np.array([3, 5, 11], dtype=np.float32) - color) * ink[:, :, None]

    is_accent = np.isin(tile, [i for i, spec in enumerate(recipe) if spec[3] == 1])
    blue_tip = np.exp(-((shoulder - .109 - twist) / .016) ** 2)
    blue_tip *= is_accent * smooth(.72, .94, t) * (.53 + .15 * fibres)
    color += (np.array([37, 105, 243], dtype=np.float32) - color) * blue_tip[:, :, None]
    is_base = tile == len(recipe)
    small_locks = .5 + .5 * np.cos(flow * 14 + .4 * np.sin(flow * 3))
    under_ridge = np.clip(.55 + .29 * small_locks + .10 * sweep + .12 * fibres + .052 * fine, .31, .98)
    under = np.array([106, 121, 151], dtype=np.float32)
    color[is_base] = (under + (porcelain - under) * under_ridge[:, :, None])[is_base]
    rough = np.clip(.52 + .10 * trough - .075 * ridge + .036 * sweep + .029 * fibres, .37, .73)
    height = np.clip(.5 + .117 * sweep + .190 * fibres + .083 * fine, 0, 1)
    maps = {"Color": color, "Altura_MASTER": 255 * height,
            "Rugosidad": 255 * rough.reshape(512, 2, 512, 2).mean(axis=(1, 3))}
    for name, values in maps.items():
        sculpt.png(ASSET / "texturas" / f"{STEM}_{name}.png", np.rint(values).astype(np.uint8))
    return height


def sculpted(recipe):
    v4.control_sections.clear()
    layer = bpy.data.collections.new("Celestial Hair V5 · MASTER")
    bpy.context.scene.collection.children.link(layer)
    zones = {}
    for name in sorted({spec[1] for spec in recipe} | {"Base"}):
        zones[name] = bpy.data.collections.new("V5 · " + name)
        layer.children.link(zones[name])
    mat = v4.material(master=True)
    sculpt.closed_mesh = shape
    try:
        high = {i: sculpt.cage(spec, i, zones[spec[1]], mat) for i, spec in enumerate(recipe)}
        high[len(recipe)] = sculpt.scalp("C", len(recipe), zones["Base"], mat)
    finally:
        sculpt.closed_mesh = v4.original_closed_mesh
    return high


class Surface:
    """Sample positions and continuous normals on a triangulated MASTER UV island."""

    def __init__(self, source, tile):
        self.tile = tile
        mesh = source.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
        mesh.calc_loop_triangles()
        uv = mesh.uv_layers.active.data
        self.uv = [Vector((*uv[loop].uv, 0)) for tri in mesh.loop_triangles for loop in tri.loops]
        self.points = [mesh.vertices[i].co.copy() for tri in mesh.loop_triangles for i in tri.vertices]
        self.normals = [mesh.corner_normals[i].vector.copy() for tri in mesh.loop_triangles for i in tri.loops]
        self.tree = BVHTree.FromPolygons(self.uv, [(i, i + 1, i + 2) for i in range(0, len(self.uv), 3)],
                                        all_triangles=True)

    def at(self, u, t):
        x, y = sculpt.coord(self.tile, min(.99998, max(.00002, u)), t)
        location, _, index, _ = self.tree.ray_cast(Vector((x, y, 1)), Vector((0, 0, -1)), 2)
        if index is None:
            location, _, index, _ = self.tree.find_nearest(Vector((x, y, 0)))
            assert location is not None and (location - Vector((x, y, 0))).length < .001, (self.tile, u, t)
        i = index * 3
        location2d = self.uv[i:i+3]
        point = barycentric_transform(location, *location2d, *self.points[i:i+3])
        normal = barycentric_transform(location, *location2d, *self.normals[i:i+3]).normalized()
        return point, normal


def stations(surface, mapping, count):
    dense = np.linspace(mapping[0], mapping[-1], 55)
    sample_u = (.0002, .18, .48, .82)
    arc = np.zeros(len(dense))
    for u in sample_u:
        points = [surface.at(u, float(t))[0] for t in dense]
        path = [b - a for a, b in zip(points, points[1:])]
        for i, span in enumerate(path, 1):
            turn = span.angle(path[i], 0) if i < len(path) else 0
            arc[i] += span.length + .015 * turn
    ratios = np.linspace(0, 1, count)
    # Keep the final two rings close enough to preserve the curved taper.
    ratios[-2] = .91 if count >= 7 else .83
    return np.interp(ratios * np.cumsum(arc)[-1], np.cumsum(arc), dense)


def retopology(high, recipe):
    blank = v4.material(maps=False)
    collection = bpy.data.collections.new("Celestial Hair V5 · UGC")
    bpy.context.scene.collection.children.link(collection)
    bpy.context.view_layer.update()
    objects = {}
    for i, source in high.items():
        if i in HIDDEN:
            continue
        name, _, mapping, _ = v4.control_sections[i]
        surf = Surface(source, i)
        if i == len(recipe):
            count, sides = 10, 22
            ts = np.asarray(mapping)[[0, 2, 3, 4, 5, 6, 7, 8, 10, 12]]
        else:
            count, sides = (8, 8) if i in HERO else (7, 7) if i in MID else (5, 6)
            ts = stations(surf, mapping, count)
        rings, normals = [], []
        for t in ts:
            row = [surf.at(j / sides, float(t)) for j in range(sides)]
            rings.append([point for point, _ in row])
            normals.extend(normal for _, normal in row)
        item = v4.original_closed_mesh(name, rings, ts, sides, i, collection, blank, 0)
        item.modifiers.clear()
        item.data.normals_split_custom_set_from_vertices(normals + [Vector(), Vector()])
        objects[i] = item
    return objects


def bake(high, low, height):
    src, dst = [], []
    for i, lower in low.items():
        offset = Vector((3.8 * (i % 7), 3.8 * (i // 7), 0))
        src.append(v4.duplicate_for_bake(high[i], offset, True))
        dst.append(v4.duplicate_for_bake(lower, offset, False))
    source = v4.joined(src, "MASTER separado para horneado")
    target = v4.joined(dst, "UGC separado para horneado")
    v4.triangles(target)
    material = bpy.data.materials.new("Destino normal V5")
    image = bpy.data.images.new("Normal V5 lineal temporal", 1024, 1024, alpha=True)
    image.colorspace_settings.name = "Non-Color"
    tex = material.node_tree.nodes.new("ShaderNodeTexImage")
    tex.image = image
    material.node_tree.nodes.active = tex
    target.data.materials.append(material)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 4
    v4.select([target, source])
    bpy.ops.object.bake(type="NORMAL", normal_space="TANGENT", use_selected_to_active=True,
                       cage_extrusion=.034, max_ray_distance=.091, margin=7, margin_type="EXTEND",
                       normal_r="POS_X", normal_g="POS_Y", normal_b="POS_Z")
    pixels = np.empty(1024 * 1024 * 4, dtype=np.float32)
    image.pixels.foreach_get(pixels)
    pixels = pixels.reshape(512, 2, 512, 2, 4)
    vectors = pixels[:, :, :, :, :3] * 2 - 1
    valid = ((pixels[:, :, :, :, 3] > .15) & (vectors[:, :, :, :, 2] > .2))[:, :, :, :, None]
    counts = valid.sum(axis=(1, 3))
    normals = (vectors * valid).sum(axis=(1, 3)) / np.maximum(1, counts)
    normals[counts[:, :, 0] == 0] = (0, 0, 1)
    normals[:, :, :2] *= .53
    normals[:, :, 2] = np.maximum(normals[:, :, 2], .77)
    height_512 = height.reshape(512, 2, 512, 2).mean(axis=(1, 3))
    dv, du = np.gradient(height_512)
    normals[:, :, 0] -= np.clip(du * .62, -.22, .22)
    normals[:, :, 1] -= np.clip(dv * .62, -.22, .22)
    normals /= np.maximum(.001, np.linalg.norm(normals, axis=2, keepdims=True))
    encoded = np.rint((normals * .5 + .5) * 255).astype(np.uint8)
    assert np.median(encoded[:, :, 2]) > 220
    sculpt.png(ASSET / "texturas" / f"{STEM}_Normal.png", encoded)
    for obj in (target, source):
        bpy.data.objects.remove(obj, do_unlink=True)
    return {"resolution": 512, "space": "MikkTSpace / OpenGL Y+", "projected_pixels": int(np.count_nonzero(counts)),
            "median_blue": int(np.median(encoded[:, :, 2]))}


VIEWS = (
    ("frente", (0,-6,.05), (0,0,-.41), 2.31),
    ("espalda", (0,6,.72), (0,.08,-.43), 2.33),
    ("perfil", (6,0,.44), (0,0,-.45), 2.33),
    ("perfil_izquierdo", (-6,0,.44), (0,0,-.45), 2.33),
    ("perspectiva", (3.5,-5.5,.96), (0,0,-.41), 2.36),
)


def build(mode):
    bpy.ops.wm.open_mainfile(filepath=str(sculpt.ASSEMBLY))
    bpy.context.preferences.filepaths.save_version = 0
    for name in ("blender", "exportaciones", "texturas", "validacion", "renders"):
        (ASSET / name).mkdir(exist_ok=True, parents=True)
    WORK.mkdir(exist_ok=True, parents=True)
    recipe = refine()
    height = textures(recipe)
    high = sculpted(recipe)
    low = retopology(high, recipe)
    crown = bpy.data.objects[sculpt.ACCESSORIES[0]]
    # Evaluate a tighter crown fit before committing to a vertical placement.
    options = {}
    original = crown.location.z
    for dz in (0, -.009, -.018, -.030):
        crown.location.z = original + dz
        options[str(dz)] = v4.fit(low)
    clear = [float(dz) for dz, info in options.items() if not info["crown_triangle_pairs"]]
    assert clear, options
    trial = min(clear)
    crown.location.z = original + trial
    hi_fit = v4.fit(high)
    while hi_fit["crown_triangle_pairs"] and trial < 0:
        trial = min(0., round(trial + .003, 3))
        crown.location.z = original + trial
        hi_fit = v4.fit(high)
    report = {"MASTER": hi_fit, "UGC": v4.fit(low), "crown_delta_y_studs": trial, "crown_ugc_trials": options}
    print("V5_FIT", json.dumps(report, ensure_ascii=False), flush=True)
    if mode == "measure":
        return
    assert report["UGC"]["evaluated_triangles"] <= 4000, report
    if mode == "final":
        for result in (report["MASTER"], report["UGC"]):
            assert not result["crown_triangle_pairs"] and not result["halo_triangle_pairs"], result
            assert not any(result["blocked_eye_samples_out_of_176_per_eye"]), result
            assert not any(result["scalp_uncovered_by_height_out_of_96"]), result
    normal = bake(high, low, height)
    report["normal"] = normal
    print("V5_NORMAL", normal, flush=True)

    mesh = v4.joined(list(low.values()), STEM + "_UGC")
    v4.triangles(mesh)
    mesh.data.materials.clear()
    mesh.data.materials.append(v4.material())
    assert mesh.data.has_custom_normals
    scene, gpu = sculpt.stage()
    report["gpu"] = gpu
    output = WORK if mode == "preview" else ASSET / "renders"
    accessories = [bpy.data.objects[name] for name in sculpt.ACCESSORIES]
    v4.hide(accessories, True)
    if mode == "final":
        v4.export(mesh)
        v4.hide([mesh], True)
        sculpt.render(scene, "V5_MASTER", (3.5,-5.5,.87), (0,0,-.41), 2.36, output, False)
        v4.save_master(list(high.values()), "MASTER", ASSET / "blender")
    v4.hide(high.values(), True)
    v4.hide([mesh], False)
    for name, direction, center, scale in VIEWS:
        if mode == "preview" and name == "perfil_izquierdo":
            continue
        sculpt.render(scene, "V5_" + name, direction, center, scale, output, mode == "preview")
    if mode == "final":
        v4.save_master([mesh], "UGC", ASSET / "blender")
    v4.hide(accessories, False)
    sculpt.render(scene, "V5_conjunto_neutro", (0,-6.2,.49), (0,0,.057), 3.18, output, mode == "preview")
    scene.world.node_tree.nodes.get("Background").inputs[1].default_value = .19
    bpy.data.lights["Silver edge"].color = (.27,.52,1.0)
    bpy.data.lights["Silver edge"].energy = 590
    sculpt.render(scene, "V5_conjunto_cine", (2.6,-6.1,1.15), (0,0,.05), 3.14, output, mode == "preview")
    (ASSET / "validacion" / "ajuste.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("measure", "preview", "final"))
    build(parser.parse_args(sys.argv[sys.argv.index("--") + 1:]).mode)
