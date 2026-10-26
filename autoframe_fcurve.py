bl_info = {
    "name": "Autoframe F-Curve",
    "author": "Cenek Strichel",
    "version": (1, 0, 1),
    "blender": (3, 0, 0),
    "location": "Hotkeys only",
    "description": "Auto frame curve in Graph Editor",
    "category": "Cenda Tools",
    "wiki_url": "https://github.com/CenekStrichel/CendaTools/wiki",
    "tracker_url": "https://github.com/CenekStrichel/CendaTools/issues"
    }


import bpy
from bpy.props import BoolProperty


def iter_fcurves(action, slot):
    # Blender 5 removed Action.fcurves, fcurves live in slot channelbags
    layers = getattr(action, "layers", None)
    if layers is None:
        yield from action.fcurves
        return

    for layer in layers:
        for strip in layer.strips:
            for channelbag in strip.channelbags:
                if slot is None or channelbag.slot_handle == slot.handle:
                    yield from channelbag.fcurves



############
# CHANNELS #
############		
class ClickAndFrame(bpy.types.Operator):
    
    bl_idname = "graph.channels_click_and_frame"
    bl_label = "Mouse Click on Channels and Frame"
    
    extend : BoolProperty(name="Extend", default=False)

    '''
    @classmethod
    def poll(cls, context):
        return context.area.type == 'GRAPH_EDITOR'
    '''

    def execute(self, context):
        
        ##############################
        # region
        # Save selected
        ##############################
        selected = []

        objects = list(context.selected_objects) # graph editor shows all selected objects
        if( context.object and context.object not in objects ):
            objects.append(context.object)

        for obj in objects :

            animation_data = obj.animation_data

            if( animation_data and animation_data.action ):
                for fcurve in iter_fcurves(animation_data.action, animation_data.action_slot) :
                    for p in fcurve.keyframe_points :

                        selected.append((p, p.select_control_point, # state of selected
                            p.select_left_handle,
                            p.select_right_handle))
        #endregion
        

        ##############################
        # region 
        # Graph Editor
        ##############################
        if( context.area.type == 'GRAPH_EDITOR' ):
            
            bpy.ops.anim.channels_click('INVOKE_DEFAULT', extend = self.extend) # click to channel
            bpy.ops.anim.channel_select_keys('INVOKE_DEFAULT', extend = self.extend) # select keys

            bpy.ops.graph.view_selected('EXEC_REGION_WIN') # frame selected
            # TODO how to view all selected channels?
        #endregion


        ##############################
        # region 
        # Dope & NLA
        ##############################
        else:

            bpy.ops.anim.channels_click('INVOKE_DEFAULT', extend = self.extend)
        #endregion


        ##############################
        # region 
        # Load selected
        ##############################
        if( selected ):
            for p, select_control_point, select_left_handle, select_right_handle in selected :

                p.select_control_point = select_control_point
                p.select_left_handle = select_left_handle
                p.select_right_handle = select_right_handle
        #endregion
        

        return {'FINISHED'}




################################################################
# register #
classes = (
    ClickAndFrame,
)


addon_keymaps = []

def register():
    
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)
    
    #region KEYMAP

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    
    if(kc):
        
        km = kc.keymaps.new(name='Animation Channels', space_type='EMPTY')
        
        #
        kmi = km.keymap_items.new( ClickAndFrame.bl_idname, 'LEFTMOUSE' , 'PRESS' )
        kmi.properties.extend = False
        addon_keymaps.append((km, kmi))
        
        #
        kmi = km.keymap_items.new( ClickAndFrame.bl_idname, 'LEFTMOUSE', 'PRESS', shift=True )
        kmi.properties.extend = True
        addon_keymaps.append((km, kmi))

    #endregion


def unregister():
    
    #region KEYMAP

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
        
    addon_keymaps.clear()
    
    #endregion

    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
    
    
if __name__ == "__main__":
    register()