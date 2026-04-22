"""
This script shows current selection in Hypershade window.

Author: Davina Ma Heming
Date: 2026.04.22
Environment: Python 2.7
"""

import maya.cmds as cmds
import maya.mel


def show_selection_in_hypershade(show_conn=False):
    """
    Show current selection in Hypershade window.
    
    :type show_conn: bool     # If True, also show connections of the selected nodes in Hypershade
    """
    selected_nodes = cmds.ls(selection=True) or []
    if not selected_nodes:
        return

    # Open Hypershade window
    maya.mel.eval("HypershadeWindow;")

    # Get Hypershade window name
    hypershade_node_editor = maya.mel.eval('getHypershadeNodeEditor;')      # hyperShadePrimaryNodeEditor
    if not hypershade_node_editor:
        raise Exception("Failed to find Hypershade node editor name.")
    hypershade_panel = cmds.getPanel(withFocus=True)        # hyperShadePanel1
    if not hypershade_panel:
        raise Exception("Failed to find Hypershade panel name.")
    
    # Clear graph
    cmds.evalDeferred(
        lambda: cmds.nodeEditor(hypershade_node_editor, edit=True, rootNode="")
    )

    # Add selection nodes
    cmds.evalDeferred(
        lambda: cmds.nodeEditor(hypershade_node_editor, edit=True, frameAll=True, addNode="")
    )

    # Show connection nodes to current selection
    if show_conn:
        cmds.evalDeferred(
            lambda: maya.mel.eval(
                'hyperShadePanelGraphCommand("{0}", "showUpAndDownstream");'.format(hypershade_panel)
            )
        )


if __name__ == "__main__":
    show_selection_in_hypershade(show_conn=True)