"""
delete_unused_filenode.py

The main function in this script is delete_unused_file_nodes().
It finds and deletes all file nodes in the current Maya scene
that are not used (connected) by any DAG object.

This function is implemented because I find MLdeleteUnused
can only delete nodes that are not connected by other nodes,
but there are cases in my project that the file node is connected to a material,
whereas the material is not used by any DAG object in the scene,
and we still want to delete these file nodes.

Note that this script was mainly written by chatGPT.
I have tested it in various cases, but there are still chances that it contains some minor mistakes.

Author: Davina Ma Heming
Date: 2026.04.22
Environment: Python 2.7
"""

import maya.cmds as cmds


def get_downstream_shading_engines(start_node):
    """
    Traverse connections from start_node and collect all shadingEngines

    :type start_node: Maya node object
    :rtype: list[Maya shadingEngine]
    """
    result = set()
    visited = set()
    stack = [start_node]
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        outs = cmds.listConnections(node, s=False, d=True) or []
        for o in outs:
            try:
                nt = cmds.nodeType(o)
            except Exception:
                # Node might not exist anymore, skip it
                continue
            if nt == 'shadingEngine':
                result.add(o)
            else:
                stack.append(o)
    return list(result)


def shading_engine_has_members(se):
    """
    Return True if the shadingEngine has a DAG member (is used by any object)

    :type se: Maya shadingEngine
    :rtype: bool
    """
    try:
        members = cmds.sets(se, q=True) # get members of shadingEngine
        return bool(members)
    except Exception:
        # Check if dagSetMembers has connections
        try:
            conns = cmds.listConnections(se + ".dagSetMembers", s=True, d=False) or []
            return bool(conns)
        except Exception:
            return False


def delete_unused_file_nodes():
    """
    Delete file nodes that are not used by any object.
    Note that MLdeleteUnused may not delete these nodes,
    because they might have connections with them.
    But as long as these file nodes are not used by scene objects,
    this function will find and delete them.

    :rtype: list[Mata file node]
    """
    file_nodes = cmds.ls(type='file') or []
    if not file_nodes:
        print("No file node found in scene.")
        return []

    unused = []
    for file_node in file_nodes:
        try:
            is_referenced = cmds.referenceQuery(file_node, isNodeReferenced=True)
        except Exception:
            pass
        else:
            if is_referenced:
                continue

        downstream_nodes = get_downstream_shading_engines(file_node)
        # If any shadingEngine is found, then file is used
        file_used = False
        for downstream_node in downstream_nodes:
            file_used = file_used or (cmds.nodeType(downstream_node) == 'shadingEngine' and shading_engine_has_members(downstream_node))
            file_used = file_used or (cmds.nodeType(downstream_node) in ["particle", "nParticle", "fluidShape"])
            relativeShapes = cmds.listRelatives(downstream_node, shapes=True, fullPath=True) or []
            file_used = file_used or (cmds.nodeType(downstream_node) == "transform" and any([cmds.nodeType(relativeShape) in ["particle", "nParticle", "fluidShape"] for relativeShape in relativeShapes]))
            if file_used:
                break

        # If no shadingEngine is found, or none of them has members, then file is not used
        if not file_used:
            unused.append(file_node)

    if not unused:
        print("No unused file nodes found.")
        return []

    print("Detected %d file node(s) not used by any scene object: %s" % (len(unused), ", ".join(unused)))
    try:
        cmds.delete(unused)
        print("Deleted %d file nodes" % len(unused))
    except Exception as e:
        raise Exception("Error occurred during file node deletion: %s" % e)

    return unused


if __name__ == "__main__":
    delete_unused_file_nodes()