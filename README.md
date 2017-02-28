# batchgltf

**Requirements:**
* python
* [COLLADA2glTF](https://github.com/KhronosGroup/COLLADA2GLTF) available to run in current path. You can download a [precompiled binary](https://github.com/KhronosGroup/glTF/releases).

**Usage:**

```
$ python batchgltf.py
```

If no settings file is specified, it will open the GUI:

![image](https://cloud.githubusercontent.com/assets/359872/23403700/90733232-fdb1-11e6-84ef-6aa84e2395f0.png)

Use the **+ Add Folder...** button to add folders that contain .dae files to the Input Folders list. 
The .dae files found in the Input Folders are going to be converted to glTF and saved in the corresponding output folder on the right panel.

* You can change the output folder just by single clicking on each item.
* You can delete an input folder by pressing `DELETE` key.
* If you save the settings to a file, you can then run the conversion directly by specifying the seetings file as a parameter to the script:

```
python batchgltf.py <settings_file>
```

Please remember that a `collada2gltf` executable must be available in the current path.

**Disclaimer:**
This is very draft and untested. Please use with care. The author does not make responsible for the damage it may cause in your files or your life.
