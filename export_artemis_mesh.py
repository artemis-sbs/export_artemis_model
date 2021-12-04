import bpy
import bmesh



# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ExportArtemisDxs(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "export_artemis.model_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export Artemis model"

    # ExportHelper mixin class uses this
    filename_ext = ".dxs"

    filter_glob: StringProperty(
        default="*.dxs",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    # use_setting: BoolProperty(
    #     name="Example Boolean",
    #     description="Example Tooltip",
    #     default=True,
    # )

    # type: EnumProperty(
    #     name="Example Enum",
    #     description="Choose between two items",
    #     items=(
    #         ('OPT_A', "First Option", "Description one"),
    #         ('OPT_B', "Second Option", "Description two"),
    #     ),
    #     default='OPT_A',
    # )

    def execute(self, context):
        return self.write_file(context, self.filepath, None)

    def write_file(self, context, filepath, options):
        f = open(filepath, 'w', encoding='utf-8')
        self.write_scene(context, f, options)
        f.close()
        return {'FINISHED'}

    def write_scene(self, context, file, options):
        file.write('<scene version="1.6">')
        # not required
        # self.write_world(context, file, options)
        self.write_materials(context, file, options)
        self.write_primitives(context, file, options)
        # not required
        # self.write_skeletons(context, file, options)
        # self.write_lights(context, file, options)
        file.write('</scene>')

    def write_world(self, context, file, options):
        self.write(file, 1, 
"""
    <settings name="new scene" author="" comments="" shadowOpacity="75">
        <ambient r="255" g="255" b="255" />
    </settings>
""")

    def write_materials(self, context, file, options):

        file.write(
""" <materials highestID="16">
<category name="System">
    <material id="0" name="mine1" used="true" lightmap="true" castShadows="true" receiveShadows="true">
    <raytracing ambientReflection="0.1" diffuseReflection="0.9">
        <specularColor r="255" g="255" b="255" />
        <reflectiveColor r="255" g="255" b="255" />
    </raytracing>
    <layer type="texture" blend="replace">
        <texture file="Artemis\mine1.png" />
    </layer>
    </material>
</category>
</materials>
""")

    def write_primitives(self, context, file, options):
        self.write(file, 1, '<primitives highestID="2">')
        # for each object
        object = bpy.context.object
        self.write_primitive(object, file, options)
        self.write(file, 1, '</primitives>')

    def write_primitive(self, object, file, options):
        id = 1
        name = "mesh"
        self.write(file, 2, f'<primitive id="{id}" name="{name}" type="cylinder" visible="true" snap="none" autoUV="false" groupID="-1" skeletonID="-1">')
        self.write_vertices(object, file, options)
        self.write_polys(object, file, options)
        self.write(file, 2, '</primitive>')
    
    def write_vertices(self, object, file, options):
        self.write(file, 3, '<vertices>')
         #An object (selected one)

        #Write 3D coordinates
        for v in object.data.vertices:
            index = v.index
            x = v.co[0]
            y = v.co[1]
            z = v.co[2]
            self.write(file, 4, f'<vertex id="{index}" x="{x}" y="{y}" z="{z}" jointID="-1" />')
        self.write(file, 3, '</vertices>')


    def write_polys_old(self, object, file, options):
        """ Write the UV Mappings """
        self.write(file, 3, '<polygons>')
        # for each
        materialId=0
        # for each 
        for p in object.data.polygons: 
            self.write(file, 4, f'<poly mid="{materialId}">')
            #Write a line per polygon indicating the vertices it uses
            for i in p.vertices:
                #Write i in your file  
                vertexId = i
                u = "UV.U"
                v = "UV.v"
                self.write(file, 5, f'<vertex vid="{vertexId}" u0="{u}" v0="{v}" />')
            self.write(file, 4, '</poly>')
        self.write(file, 3, '</polygons>')

    def write_polys(self, object, file, options):

        self.write(file, 3, '<polygons>')
        bm = bmesh.new()
        bm.from_mesh(object.data)
        uv_layer = bm.loops.layers.uv.active

        for face in bm.faces:
            materialId= face.material_index
            
            self.write(file, 4, f'<poly mid="{materialId}">')
            for corner in face.loops:
                vertexId = corner.vert.index
                uv = corner[uv_layer].uv
                u = uv.x
                v = uv.y
                self.write(file, 5, f'<vertex vid="{vertexId}" u0="{u}" v0="{v}" />')
            self.write(file, 4, '</poly>')
        self.write(file, 3, '</polygons>')

    

    def write_skeletons(self, context, file, options):
        self.write(file, 1, '<skeletons />')

    def write_lights(self, context, file, options):
        self.write(file, 1, '<lights highestID="2" />')
    
    def write(self, file, indent, lines):
        file.write("    " * indent + lines +' \n')



# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(ExportArtemisDxs.bl_idname, text="Artemis model .dxs")

# Register and add to the "file selector" menu (required to use F3 search "Text Export Operator" for quick access)
def register():
    bpy.utils.register_class(ExportArtemisDxs)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportArtemisDxs)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.export_artemis.model_data('INVOKE_DEFAULT')
