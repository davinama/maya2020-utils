"""
This script deletes all unused namespaces in the current Maya scene.
A namespace is considered unused,
if it has no child namespaces and contains no nodes.

Author: Davina Ma Heming
Date: 2026.04.22
Environment: Python 2.7
"""

import maya.cmds as cmds

BUILTIN_NAMESPACES = ['UI', 'shared']


def get_all_namespaces():
    """
    Returns a list of all user-defined namespaces in the current Maya scene,
    excluding built-in namespaces like 'UI' and 'shared'.

    :rtype: list[string]        # list of Maya namespaces
    """
    try:
        all_ns = cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True) or []
    except Exception:
        all_ns = []
    return [ns for ns in all_ns if ns not in BUILTIN_NAMESPACES]


def is_namespace_empty(ns):
    """
    Checks if a namespace is empty, meaning it has no child namespaces and contains no nodes.

    :type ns: string     # Maya namespace
    :rtype: bool         # True if the namespace is empty, False otherwise
    """
    # Check for child namespaces
    children = cmds.namespaceInfo(ns, listOnlyNamespaces=True) or []
    if children:
        return False

    # Check for nodes in the namespace
    contents = cmds.namespaceInfo(ns, listNamespace=True) or []
    return len(contents) == 0


def delete_unused_namespaces(dry_run=False):
    """
    Deletes all unused namespaces in the current Maya scene.
    A namespace is considered unused if it has no child namespaces and contains no nodes.

    :type dry_run: bool     # If True, will only print namespaces that would be deleted without actually deleting them
    """
    all_ns = get_all_namespaces()

    if not all_ns:
        print("No user-defined namespaces found in the scene.")
        return

    # Sort namespaces from the deepest child to the root namespace.
    sorted_ns = sorted(all_ns, key=lambda ns: ns.count(':'), reverse=True)
    deleted = []
    for ns in sorted_ns:
        # Check if the namespace still exists (it might have been deleted as a child of another namespace)
        if not cmds.namespace(exists=ns):
            continue

        if is_namespace_empty(ns):
            if dry_run:
                print("Found unused namespaces: %s"%ns)
            else:
                try:
                    cmds.namespace(removeNamespace=ns)
                except Exception as e:
                    print("Failed to delete namespace %s: %s"%(ns, str(e)))
            deleted.append(ns)

    if not deleted:
        print("No unused namespaces found.")
    elif not dry_run:
        print("Unused namespaces deleted: %s"%(deleted))


if __name__ == "__main__":
    delete_unused_namespaces(dry_run=True)