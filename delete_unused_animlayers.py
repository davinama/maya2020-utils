"""
This script deletes all unused animation layers in the current Maya scene.
An animation layer is considered unused,
if it has no animated attributes, no animCurves, and no child layers.

Author: Davina Ma Heming
Date: 2026.04.22
Environment: Python 2.7
"""

import maya.cmds as cmds

def _postorder(layer, result):
    """
    Post-order traversal of the animLayer hierarchy.
    Appends layers to result in "child → parent" order.

    :type layer: string     # Maya animLayer
    :type result: list[string]      # Maya animLayer list, passed by reference, will be modified in-place
    """
    children = cmds.animLayer(layer, q=True, children=True) or []
    for child in children:
        _postorder(child, result)
    result.append(layer)


def get_anim_layers_bottom_up():
    """
    Sort animLayers from the deepest child to the root layer (BaseAnimation).

    :rtype: list[string]        # list of Maya animation layers
    """
    root_layer = cmds.animLayer(q=True, root=True)
    if not root_layer:
        return []

    anim_layers_reversed = []
    _postorder(root_layer, anim_layers_reversed)
    return anim_layers_reversed


def delete_unused_animlayers():
    """
    Deletes all unused animation layers in the current Maya scene.

    :rtype: list[string]        # list of Maya animation layers that were deleted
    """
    root_layer = cmds.animLayer(query=True, root=True)      # BaseAnimation
    # Get all animLayers in "child → parent" order,
    # so we can safely delete unused layers without worrying about the hierarchy.
    all_anim_layers = get_anim_layers_bottom_up()

    if not all_anim_layers or (len(all_anim_layers) == 1 and all_anim_layers[0] == root_layer):
        return []
    
    unused_anim_layers = []
    for anim_layer in all_anim_layers:
        if anim_layer == root_layer:
            continue
        
        layer_attributes = cmds.animLayer(anim_layer, query=True, attribute=True) or []
        layer_curves = cmds.animLayer(anim_layer, query=True, animCurves=True) or []
        child_layers = cmds.animLayer(anim_layer, query=True, children=True) or []

        # An animLayer is considered unused,
        # if it has no animated attributes, no animCurves, and no child layers.
        if not layer_attributes and not layer_curves and not child_layers:
            try:
                cmds.delete(anim_layer)
            except Exception as e:
                print("Failed to delete animLayer %s: %s"%(anim_layer, str(e)))
            else:
                unused_anim_layers.append(anim_layer)

    return unused_anim_layers


if __name__ == "__main__":
    deleted_layers = delete_unused_animlayers()
    if deleted_layers:
        print("Deleted unused animLayers: %s"%(deleted_layers))
    else:
        print("No unused animLayers found.")