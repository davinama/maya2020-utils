# maya2020-utils

A collection of utility scripts for Autodesk Maya 2020.

## Overview

This repository contains Python scripts designed to automate common scene tasks in Maya 2020, including removing unused nodes, fixing crash issues, and managing scene organization.

## Scripts

### 1. delete_unused_filenode.py

Finds and deletes all unused file nodes (texture nodes) in the current Maya scene that are not connected to any DAG objects.

**Why this is useful:**  
Maya's built-in `MLdeleteUnused` command only removes completely disconnected nodes. However, there are cases where a file node is connected to a material, but that material is not actually used by any object in the scene. This script identifies and removes these "orphaned" file nodes to help reduce scene file size and improve performance.

**Usage:**
```python
import delete_unused_filenode
delete_unused_filenode.delete_unused_file_nodes()
```

---

### 2. reset_uiConfigurationScriptNode.py

Fixes a Maya 2020 crash issue that occurs when closing the application after opening scene files through Python API calls instead of through the UI.

**Why this is useful:**  
When Maya scenes are loaded asynchronously via `cmds.file()` in Viewport 2.0, uninitialized UI variables can cause Maya to crash on exit. This script scans Maya ASCII (.ma) files and clears the problematic `uiConfigurationScriptNode` values to prevent crashes.

**Note:** This modification does not affect scene data and is automatically restored when the scene is reopened.

**Usage:**
```python
import reset_uiConfigurationScriptNode

ma_file_path = "path/to/your/scene.ma"
reset_uiConfigurationScriptNode.reset_uiConfigurationScriptNode(ma_file_path)
```

---

### 3. delete_unused_namespaces.py

Deletes all unused namespaces in the current Maya scene.

**Why this is useful:**  
Over time, Maya scenes can accumulate empty namespaces from deleted references or imports. These unused namespaces clutter the scene and can cause confusion. This script identifies and removes namespaces that contain no nodes and have no child namespaces.

**Features:**
- Automatically sorts namespaces from deepest child to root for safe deletion
- Supports dry-run mode to preview what would be deleted
- Excludes built-in namespaces ('UI', 'shared')

**Usage:**
```python
import delete_unused_namespaces

# Preview what will be deleted
delete_unused_namespaces.delete_unused_namespaces(dry_run=True)

# Actually delete unused namespaces
delete_unused_namespaces.delete_unused_namespaces(dry_run=False)
```

---

### 4. delete_unused_animlayers.py

Deletes all unused animation layers in the current Maya scene.

**Why this is useful:**  
Animation layers that have no animated attributes, no animation curves, and no child layers serve no purpose and can clutter the animation layer editor. This script removes these empty layers while preserving your animation hierarchy.

**Features:**
- Uses post-order traversal to safely delete layers from child to parent
- Preserves the BaseAnimation root layer
- Automatically handles layer hierarchy

**Usage:**
```python
import delete_unused_animlayers

deleted_layers = delete_unused_animlayers.delete_unused_animlayers()
print("Deleted layers:", deleted_layers)
```

## Environment

- **Maya Version:** Maya 2020
- **Python Version:** Python 2.7 (Maya's built-in Python interpreter)
- **OS:** Cross-platform (tested on Windows)

## Installation

1. Clone this repository or download the scripts
2. Place the scripts in a location accessible to Maya's Python path, or import them directly

## Author

Davina Ma Heming

## License

Feel free to use and modify these scripts for your projects.

## Notes

- All scripts were developed and tested in Maya 2020 production environments
- Some scripts (particularly `reset_uiConfigurationScriptNode.py`) use GB2312 encoding for file operations, which may need adjustment for different locales
- Always backup your scene files before running cleanup operations

## Contributing

Issues and pull requests are welcome!
