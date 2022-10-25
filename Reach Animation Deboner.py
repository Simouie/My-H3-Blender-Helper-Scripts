bl_info = {
    "name": "Halo Reach Deboner",
    "author": "MercyMoon",
    "version": (0, 1, 1),
    "blender": (3, 0, 0),
    "category": "3D View"
}

import os
import pathlib
import bpy
from bpy_extras.io_utils import ExportHelper
import subprocess
import sys
from os import path
from io_scene_halo import file_jma
from io_scene_halo.global_functions import global_functions
import argparse
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper
        )

from bpy.types import (
        Operator,
        Panel,
        PropertyGroup
        )

from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        IntProperty,
        PointerProperty,
        StringProperty
        )

class ReachDebonerProperties(bpy.types.PropertyGroup):

    working_directory: bpy.props.StringProperty(
        subtype="DIR_PATH", name="Working Directory",
        description="Path to directory for your animation files",
    )

class deboner(bpy.types.Operator):
    bl_idname = "reachdeboner.deboner"
    bl_label = "Remove Reach Bones"
    bl_description = 'Remove Reach Bones'
    def execute(self, context):
        badbones = ["pedestal", "aim_pitch", "aim_yaw", "l_humerus", "l_radius", "l_handguard", "r_humerus", "r_radius", "r_handguard"]
        try:
            print("removing keyframes of bones")
            for arm in bpy.data.objects:
                #if arm.type == 'ARMATURE':
                bpy.ops.object.mode_set(mode='POSE')
                arm.select_set(True)
                bpy.ops.pose.select_all(action='DESELECT')
                for pb in arm.pose.bones:
                    if pb.name in badbones:
                        arm.data.bones[pb.name].select_set(True)
                        print(pb.name)
                        bpy.ops.anim.keyframe_clear_v3d()
        except:
            print("removing keyframes failed")
            pass
        try:
            print("removing bones")
            for obj in bpy.data.objects:
                if obj.type == 'ARMATURE':
                    bpy.ops.object.mode_set(mode='EDIT')
                    armature = obj.data
                    for bone in armature.edit_bones:
                        if bone.name in badbones: 
                            print(bone.name)
                            armature.edit_bones.remove(bone)
        except:
                print("removing bones failed")
                pass
        return {'FINISHED'}

class importboner(bpy.types.Operator):

    bl_idname = "reachdeboner.importboner"
    bl_label = "Reach Batch Importer"
    bl_description = 'Reach Batch Importer'


    def execute(self, context):

        # path_of_the_directory = r'F:\SteamLibrary\steamapps\common\H3EK\data\animations'
        path_of_the_directory = context.scene.reachdeboner_addon.working_directory
        jma_type = (".JMA", ".JMM", ".JMO", ".JMR", ".JMT", ".JMW", ".JMZ")

        for files in os.listdir(path_of_the_directory):
            if files.endswith(jma_type):
                f = os.path.join(path_of_the_directory,files)
                if os.path.isfile(f):
                    print(f)
                    try:
                        importboner.filepath = f
                        importboner.fix_parents = True
                        importboner.game_version = 'halo3mcc'
                        importboner.jms_path_a = ''
                        importboner.jms_path_b = ''
                        importboner.fix_rotations = False
                        file_extension = pathlib.Path(f).suffix
                        importboner.extension = file_extension
                        importboner.extension_ce = file_extension
                        importboner.extension_h2 = file_extension
                        importboner.extension_h3 = file_extension
                        importboner.jma_version = '16392'
                        importboner.jma_version_ce = '16392'
                        importboner.jma_version_h2 = '16395'
                        importboner.jma_version_h3 = '16395'
                        importboner.generate_checksum = True
                        importboner.frame_rate_float= False
                        importboner.biped_controller= False
                        importboner.folder_structure= False
                        importboner.scale_enum= False
                        importboner.scale_float= False
                        importboner.console= False
                        importboner.custom_frame_rate= '30'
                        print("Importing")
                        try:
                            file_jma.ImportJMA.execute(self, context)
                        except:
                            print("Importing failed")
                            pass
                        print("Deboning")
                        try:
                            deboner.execute(self, context)
                        except:
                            print("deboning failed")
                            pass
                        bpy.ops.object.mode_set(mode='OBJECT')
                        bpy.ops.object.select_all(action='DESELECT')
                        bpy.ops.object.delete()
                        print("Exporting")
                        try:
                            file_jma.ExportJMA.execute(self, context)
                        except:
                            print("exporting failed")
                            pass
                    except:
                        pass
            else:
                continue
        return {'FINISHED'}

class ReachDebonerPanel(bpy.types.Panel):
    from io_scene_halo import file_jma
    bl_idname = "WMFILEPANEL_PT_hello"
    bl_label = "Halo Reach Deboner"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Halo Reach Deboner"
    def draw(self, context):
        layout = self.layout
        scn = context.scene
        col = layout.column_flow(columns=1, align=True)
        row = col.row(align=True)
        col.prop(scn.reachdeboner_addon, 'working_directory', text="Folder")
        col.operator("reachdeboner.deboner", icon="GROUP_BONE", text="Remove Reach Bones")
        col.operator(file_jma.ImportJMA.bl_idname, icon="BONE_DATA", text="Import an Animation")
        col.operator("reachdeboner.importboner", icon="EXPORT", text="Batch Debone/Export")

def register():
    from io_scene_halo.file_jma import import_jma
    bpy.utils.register_class(ReachDebonerPanel)
    bpy.utils.register_class(ReachDebonerProperties)
    bpy.utils.register_class(deboner)
    bpy.utils.register_class(importboner)
    bpy.types.Scene.reachdeboner_addon = bpy.props.PointerProperty(type=ReachDebonerProperties)

def unregister():
    from io_scene_halo.file_jma import import_jma
    bpy.utils.unregister_class(ReachDebonerPanel)
    bpy.utils.unregister_class(ReachDebonerProperties)
    bpy.utils.unregister_class(deboner)
    bpy.utils.unregister_class(importboner)

if __name__ == "__main__": register()
