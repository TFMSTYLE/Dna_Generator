# SPDX-FileCopyrightText: 2025-2026 The French Monkey
# SPDX-License-Identifier: GPL-3.0-or-later

bl_info = {
    "name": "DNA",
    "author": "The French Monkey",
    "version": (1, 0, 3),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Dna",
    "description": "Generate paramatric DNA",
    "category": "Add Mesh",
    "license": "GPL-3.0-or-later",
}

import bpy, bmesh, math
from math import cos, sin, tau
from mathutils import Vector, Matrix

try:
    from . import relay_updater
except ImportError:  # the Addon Collection has its own updates
    relay_updater = None

# ------------------------------------------------------------------------
# Utility
# ------------------------------------------------------------------------

def get_or_make_material(name, color):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs[0].default_value = (*color, 1.0)
    return mat

def assign_basic_materials(obj):
    matA = get_or_make_material("DNA_Strand_A", (0.2, 0.6, 1.0))
    matB = get_or_make_material("DNA_Strand_B", (1.0, 0.4, 0.4))
    matBase = get_or_make_material("DNA_Bridge", (0.9, 0.9, 0.2))
    obj.data.materials.clear()
    for m in (matA, matB, matBase):
        obj.data.materials.append(m)

# ------------------------------------------------------------------------
# Geometry builders
# ------------------------------------------------------------------------

def build_helix_curve(props):
    cu = bpy.data.curves.new("DNA_Helix_Curve", "CURVE")
    cu.dimensions = "3D"
    cu.resolution_u = 12
    cu.fill_mode = "FULL"
    cu.bevel_depth = props.strand_radius
    cu.use_fill_caps = True

    turns = max(1, int(props.turns))
    steps_per_turn = max(4, int(props.steps_per_turn))
    helix_radius = float(props.helix_radius)
    height_per_turn = float(props.height_per_turn)
    twist_factor = float(props.twist_factor)

    total_steps = turns * steps_per_turn
    total_height = height_per_turn * turns
    angle_step = tau / steps_per_turn

    A = []
    B = []
    for i in range(total_steps + 1):
        t = i / total_steps
        ang = i * angle_step * twist_factor
        z = t * total_height
        A.append(Vector((helix_radius * cos(ang), helix_radius * sin(ang), z)))
        B.append(Vector((helix_radius * cos(ang + math.pi), helix_radius * sin(ang + math.pi), z)))

    sA = cu.splines.new("POLY")
    sA.points.add(len(A) - 1)
    for i, p in enumerate(A):
        sA.points[i].co = (*p, 1.0)

    sB = cu.splines.new("POLY")
    sB.points.add(len(B) - 1)
    for i, p in enumerate(B):
        sB.points[i].co = (*p, 1.0)

    obj = bpy.data.objects.new("DNA_Helix_Curve", cu)
    bpy.context.collection.objects.link(obj)
    return obj

def build_bridge_curve(props):
    cu = bpy.data.curves.new("DNA_Bridge_Curve", "CURVE")
    cu.dimensions = "3D"
    cu.resolution_u = 6
    cu.fill_mode = "FULL"
    cu.bevel_depth = props.bridge_radius
    cu.use_fill_caps = True

    turns = max(1, int(props.turns))
    steps_per_turn = max(4, int(props.steps_per_turn))
    helix_radius = float(props.helix_radius)
    height_per_turn = float(props.height_per_turn)
    base_interval = max(1, int(props.base_interval))
    twist_factor = float(props.twist_factor)
    tilt_angle = math.radians(float(props.tilt))

    total_steps = turns * steps_per_turn
    total_height = height_per_turn * turns
    angle_step = tau / steps_per_turn

    A = []
    B = []
    for i in range(total_steps + 1):
        t = i / total_steps
        ang = i * angle_step * twist_factor
        z = t * total_height
        A.append(Vector((helix_radius * cos(ang), helix_radius * sin(ang), z)))
        B.append(Vector((helix_radius * cos(ang + math.pi), helix_radius * sin(ang + math.pi), z)))

    for i in range(0, len(A), base_interval):
        a = A[i]
        b = B[i]
        mid = (a + b) * 0.5
        rot = Matrix.Rotation(tilt_angle * ((-1) ** i), 3, Vector((0, 0, 1)))
        a_off = rot @ (a - mid) + mid
        b_off = rot @ (b - mid) + mid
        s = cu.splines.new("POLY")
        s.points.add(1)
        s.points[0].co = (*a_off, 1.0)
        s.points[1].co = (*b_off, 1.0)

    obj = bpy.data.objects.new("DNA_Bridge_Curve", cu)
    bpy.context.collection.objects.link(obj)
    return obj

# ------------------------------------------------------------------------
# Assembly
# ------------------------------------------------------------------------

def convert_to_mesh(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    mesh_obj = bpy.context.active_object
    return mesh_obj


def build_final_mesh(props):
    helix_curve = build_helix_curve(props)
    bridge_curve = build_bridge_curve(props)

    mesh_helix = convert_to_mesh(helix_curve)
    mesh_bridge = convert_to_mesh(bridge_curve)

    bpy.ops.object.select_all(action='DESELECT')
    mesh_helix.select_set(True)
    mesh_bridge.select_set(True)
    bpy.context.view_layer.objects.active = mesh_helix
    bpy.ops.object.join()

    if props.smooth_shading:
        for poly in mesh_helix.data.polygons:
            poly.use_smooth = True
    else:
        for poly in mesh_helix.data.polygons:
            poly.use_smooth = False

    assign_basic_materials(mesh_helix)
    mesh_helix.name = "DNAHelix"

    return mesh_helix

# ------------------------------------------------------------------------
# Generate / Rebuild
# ------------------------------------------------------------------------

def rebuild_dna(obj, props):
    new_mesh_obj = build_final_mesh(props)
    new_data = new_mesh_obj.data.copy()

    old_data = obj.data
    obj.data = new_data
    obj.name = obj.data.name = "DNAHelix"

    bpy.data.objects.remove(new_mesh_obj, do_unlink=True)
    if old_data and old_data.users == 0:
        bpy.data.meshes.remove(old_data)

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    return obj

def generate_dna(context):
    p = context.scene.dnagen_props
    obj = context.active_object
    keys = (
        "turns", "steps_per_turn", "helix_radius", "height_per_turn",
        "strand_radius", "bridge_radius", "base_interval",
        "twist_factor", "tilt", "smooth_shading"
    )

    if obj and obj.type == "MESH" and obj.get("dna_generator") and obj.select_get():
        for k in keys:
            if hasattr(p, k):
                obj[k] = getattr(p, k)
        rebuild_dna(obj, p)
        return obj

    new_obj = build_final_mesh(p)
    new_obj["dna_generator"] = True
    for k in keys:
        if hasattr(p, k):
            new_obj[k] = getattr(p, k)

    context.view_layer.objects.active = new_obj
    new_obj.select_set(True)
    return new_obj

def update_dna(self, context):
    if not self.live_update:
        return

    obj = context.active_object

    if (
        not obj
        or obj.type != "MESH"
        or "dna_generator" not in obj
        or not obj.select_get()
    ):
        return

    rebuild_dna(obj, self)

# ------------------------------------------------------------------------
# Properties
# ------------------------------------------------------------------------

class DNAGenProperties(bpy.types.PropertyGroup):
    live_update: bpy.props.BoolProperty(name="Live Update", default=False)

    turns: bpy.props.IntProperty(name="Turns", default=6, min=1, max=20, subtype='FACTOR', update=update_dna)
    steps_per_turn: bpy.props.IntProperty(name="Steps per Turn", default=12, min=4, max=256, subtype='FACTOR', update=update_dna)
    helix_radius: bpy.props.FloatProperty(name="Helix Radius", default=0.3, min=0.01, max=10.0, subtype='FACTOR', update=update_dna)
    height_per_turn: bpy.props.FloatProperty(name="Height per Turn", default=0.5, min=0.01, max=10.0, subtype='FACTOR', update=update_dna)

    strand_radius: bpy.props.FloatProperty(name="Helix Thickness", default=0.02, min=0.001, max=1.0, subtype='FACTOR', update=update_dna)
    bridge_radius: bpy.props.FloatProperty(name="Bridge Thickness", default=0.01, min=0.001, max=1.0, subtype='FACTOR', update=update_dna)

    base_interval: bpy.props.IntProperty(name="Base Pair Interval", default=3, min=1, max=100, subtype='FACTOR', update=update_dna)
    twist_factor: bpy.props.FloatProperty(name="Twist Factor", default=1.0, min=0.1, max=1.0, subtype='FACTOR', update=update_dna)
    tilt: bpy.props.FloatProperty(name="Tilt (°)", default=0.0, min=0.0, max=90.0, subtype='ANGLE', update=update_dna)
    smooth_shading: bpy.props.BoolProperty(name="Smooth Shading", default=True, update=update_dna)

class DNAGEN_OT_generate(bpy.types.Operator):
    bl_idname = "dna.generate"
    bl_label = "Generate DNA"
    bl_options = {"REGISTER", "UNDO"}
    def execute(self, context):
        if context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        generate_dna(context)
        return {"FINISHED"}

# ------------------------------------------------------------------------
# UI
# ------------------------------------------------------------------------

class VIEW3D_PT_dna_generator(bpy.types.Panel):
    bl_label = "Dna"
    bl_idname = "VIEW3D_PT_dna_generator"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Dna"

    def draw(self, context):
        if relay_updater:
            relay_updater.draw(self.layout)
        layout = self.layout
        p = context.scene.dnagen_props
        o = context.object

        row = layout.row(align=True)
        row.operator("dna.generate", text="Generate DNA", icon="RNA")

        layout.prop(p, "live_update", toggle=True)

        layout.separator(factor=0.5)

        layout.prop(p, "turns")
        layout.prop(p, "steps_per_turn")
        layout.prop(p, "helix_radius")
        layout.prop(p, "height_per_turn")

        layout.prop(p, "strand_radius")
        layout.prop(p, "bridge_radius")

        layout.separator(factor=0.5)

        layout.prop(p, "base_interval")
        layout.prop(p, "twist_factor")
        layout.prop(p, "smooth_shading", toggle=True)

        layout.separator(factor=0.5)

        if o and "dna_generator" in o and o.select_get():
            layout.label(text=f"Editing: {o.name}", icon="RNA")
        else:
            layout.label(text="No DNA selected", icon="INFO")

# ------------------------------------------------------------------------
# Registration
# ------------------------------------------------------------------------

classes = (
    DNAGenProperties,
    DNAGEN_OT_generate,
    VIEW3D_PT_dna_generator,
)

def register():
    if relay_updater:
        relay_updater.register("blender-dna")
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.dnagen_props = bpy.props.PointerProperty(type=DNAGenProperties)

def unregister():
    if relay_updater:
        relay_updater.unregister()
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
    del bpy.types.Scene.dnagen_props

if __name__ == "__main__":
    register()
