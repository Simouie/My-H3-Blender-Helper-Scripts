bl_info = {
    "name": "Halo Reach Deboner",
    "author": "MercyMoon",
    "version": (0, 2, 1),
    "blender": (3, 0, 0),
    "category": "3D View"
}


import pathlib
import os
import bpy

from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import PointerProperty, StringProperty

from io_scene_halo import file_jma


class ReachDebonerProperties(PropertyGroup):

    input_directory: StringProperty(
        subtype="DIR_PATH", name="Input Directory",
        description="Path to directory for your animation files",
    )

    output_directory: StringProperty(
        subtype="DIR_PATH", name="Output Directory",
        description="Path to directory for your animation files",
    )

class ReachDebonerPanel(Panel):

    bl_idname = "DEBONER_PT_Panel"
    
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    bl_category = "Halo Reach Deboner"
    bl_label = "Halo Reach Deboner"

    def draw(self, context):

        col = self.layout.column_flow(columns=1, align=True)
        properties = context.scene.reachdeboner_addon

        col.prop(properties, "input_directory", text="Input")
        col.prop(properties, "output_directory", text="Output")
        col.operator("reachdeboner.importboner", icon="EXPORT", text="Batch Debone / Export")

        col.separator(factor=1.0)

        col.operator(file_jma.ImportJMA.bl_idname, icon="BONE_DATA", text="Import Animation")
        col.operator("reachdeboner.deboner", icon="GROUP_BONE", text="Remove Reach Bones")


class deboner(Operator):

    bl_idname = "reachdeboner.deboner"

    bl_label = "Remove Reach Bones"
    bl_description = "Remove Reach Bones"

    def execute(self, context):

        objects = context.view_layer.objects

        bad_bones = [
            "pedestal", "aim_pitch", "aim_yaw", 
            "l_humerus", "l_radius", "l_handguard", 
            "r_humerus", "r_radius", "r_handguard"
        ]

        for obj in bpy.data.objects:

            if not obj.type == "ARMATURE": continue

            bpy.ops.object.select_all(action="DESELECT")
            objects.active = None

            obj.select_set(True)
            objects.active = obj

            print("Removing keyframes")

            try:

                bpy.ops.object.mode_set(mode="POSE")
                
                for bone in obj.pose.bones:
                    if bone.name in bad_bones:
                        print(f"{obj.name} : {bone.name}")
                        obj.data.bones[bone.name].select = True
                        
                bpy.ops.anim.keyframe_clear_v3d()

            except:
                print("Removing keyframes failed")
                pass

            print("Removing bones")

            try: 

                bpy.ops.object.mode_set(mode="EDIT")
                
                armature = obj.data
                for bone in armature.edit_bones:
                    if bone.name in bad_bones: 
                        print(f"{obj.name} : {bone.name}")
                        armature.edit_bones.remove(bone)
                
            except:
                print("Removing bones failed")
                pass

            bpy.ops.object.mode_set(mode="OBJECT")

        bpy.ops.object.select_all(action="DESELECT")
        objects.active = None
                    
        return {"FINISHED"}

class importboner(Operator):

    bl_idname = "reachdeboner.importboner"

    bl_label = "Reach Batch Importer"
    bl_description = "Reach Batch Importer"

    def execute(self, context):

        input_path = context.scene.reachdeboner_addon.input_directory
        output_path = context.scene.reachdeboner_addon.output_directory

        jma_type = (".JMA", ".JMM", ".JMO", ".JMR", ".JMT", ".JMW", ".JMZ")

        for file_name in os.listdir(input_path):

            if not file_name.endswith(jma_type): continue

            import_path = os.path.join(input_path, file_name)
            print(import_path)

            if not os.path.isfile(import_path): continue

            print("Importing")

            try:
                bpy.ops.import_scene.jma(filepath=import_path)
            except:
                print("Importing failed")
                pass

            print("Deboning")

            try:
                deboner.execute(self, context)
            except:
                print("Deboning failed")
                pass

            print("Exporting")

            export_path = os.path.join(output_path, file_name)
            extension = pathlib.Path(import_path).suffix
            game_version = "halo3mcc"
            
            try:
                bpy.ops.export_jma.export(
                    filepath=export_path,
                    extension_ce=extension, 
                    extension_h2=extension,
                    extension_h3=extension,
                    game_version=game_version
                )
            except:
                print("Exporting failed")
                pass

            for obj in bpy.data.objects:
                if obj.type == "ARMATURE":
                    bpy.data.objects.remove(obj)
            
        return {"FINISHED"}


classes = [ 
    ReachDebonerProperties, 
    ReachDebonerPanel, 
    deboner, importboner 
]

def register():

    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.Scene.reachdeboner_addon = PointerProperty(type=ReachDebonerProperties)

def unregister():

    del bpy.types.Scene.reachdeboner_addon

    for c in classes:
        bpy.utils.unregister_class(c)

if __name__ == "__main__": register()
