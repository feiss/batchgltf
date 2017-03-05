# batchgltf
# COLLADA -> glTF Batch Convert Tool
# Diego F. Goberna
# https://github.com/feiss/batchgltf

# MIT licensed
# Copyright 2017 Diego F. Goberna
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import Tkinter as tk
import tkFileDialog, tkMessageBox
import sys, os, subprocess

class ProgressWindow(tk.Toplevel):
  def __init__(self, *args, **kwargs):
    tk.Toplevel.__init__(self, *args, **kwargs)
    self.title('collada2gltf output')
    ww = 1000
    wh = 200
    sw = self.winfo_screenwidth()
    sh = self.winfo_screenheight()
    self.geometry("%dx%d+%d+%d" % (ww, wh, sw / 2 - ww/2, sh / 2 - wh/2))

    self.log = tk.Text(self, height = 1, state = tk.DISABLED)
    self.log.grid(row = 0, column = 0, sticky = tk.W+tk.E+tk.N+tk.S)
    
    scroll = tk.Scrollbar(self, orient = tk.VERTICAL, command = self.log.yview)
    scroll.grid(row = 0, column = 1, sticky=tk.N+tk.S)

    self.log['yscrollcommand'] = scroll.set

    self.grid_rowconfigure(0, weight=1)
    self.grid_columnconfigure(0, weight=1)

  def add(self, str):
    self.log.config(state = tk.NORMAL)
    self.log.insert(tk.END, str)
    self.log.config(state = tk.DISABLED)

class App(tk.Tk):
  def __init__(self, *args, **kwargs):
    tk.Tk.__init__(self, *args, **kwargs)
    self.MAGIC = 'v1.0'
    self.title('a COLLADA -> glTF batch converter')
    ww = 700
    wh = 500
    sw = self.winfo_screenwidth()
    sh = self.winfo_screenheight()
    self.geometry("%dx%d+%d+%d" % (ww, wh, sw / 2 - ww/2, sh / 2 - wh/2))
    self.minsize(width = 400, height = 200)

    menubar = tk.Menu(self)
    menufile = tk.Menu(menubar, tearoff=0)
    menufile.add_command(label="New settings", command = self.newSettings, underline = 0, accelerator = 'Ctrl+N')
    menufile.add_command(label="Open settings...", command = self.openSettings, underline = 0, accelerator = 'Ctrl+O')
    menufile.add_command(label="Save settings...", command = self.saveSettings, underline = 0, accelerator = 'Ctrl+S')
    menufile.add_separator()
    menufile.add_command(label="Exit", command = self.quit, underline = 1, accelerator = 'Ctrl+Q')
    menubar.add_cascade(label = "File", menu = menufile, underline = 0)
    self.config(menu = menubar)

    self.bind_all("<Control-n>", self.newSettings)
    self.bind_all("<Control-o>", self.openSettings)
    self.bind_all("<Control-s>", self.saveSettings)
    self.bind_all("<Control-q>", self.quit)


    tk.Label(self, text="Input Folders:").grid(row = 0, column = 0, padx = 10, sticky=tk.W+tk.N)
    tk.Label(self, text="Output Folders:").grid(row = 0, column = 1, padx = 10, sticky=tk.W+tk.N)

    self.scrollbar = tk.Scrollbar(self, orient = tk.VERTICAL)
    self.scrollbar.config(command = self.yview)
    self.scrollbar.grid(row = 1, column = 2, padx = 10, sticky=tk.N+tk.S)

    self.fromlist = tk.Listbox(self, yscrollcommand=self.scrollbar.set)
    self.fromlist.grid(row = 1, column = 0, padx = 4, pady = 5, sticky=tk.W+tk.E+tk.N+tk.S)
    self.tolist = tk.Listbox(self, yscrollcommand=self.scrollbar.set)
    self.tolist.grid(row = 1, column = 1, padx = 4, pady = 5, sticky=tk.W+tk.E+tk.N+tk.S )

    self.fromlist.configure(selectmode = tk.SINGLE, activestyle = tk.NONE, exportselection = False)
    self.tolist.configure(selectmode = tk.SINGLE, activestyle = tk.NONE, exportselection = False)

    self.fromlist.bind("<<ListboxSelect>>", self.onFromListSelect)
    self.fromlist.bind("<KeyPress>", self.onFromListKeyDown)
    self.tolist.bind("<<ListboxSelect>>", self.onToListSelect)

    self.grid_columnconfigure(0, weight=1)
    self.grid_columnconfigure(1, weight=1)
    self.grid_rowconfigure(1, weight=1)

    tk.Button(self, text="+ Add Folder...", command = self.onFromButton).grid(row = 2, column = 0, padx = 10, sticky=tk.NW)
    
    optgroup = tk.LabelFrame(self, text='General options')
    optgroup.grid(row = 3, column = 1, padx = 10, pady = 10, sticky = tk.W+tk.E+tk.N+tk.S)

    paramgroup = tk.LabelFrame(self, text='Conversion options')
    paramgroup.grid(row = 3, column = 0, padx = 10, pady = 10, sticky = tk.W+tk.E+tk.N+tk.S)

    self.embed_resources = tk.IntVar()
    self.use_materials_common = tk.IntVar()
    self.invert_transparency = tk.IntVar()
    self.default_lighting = tk.IntVar()

    self.use_materials_common.set(1)

    tk.Checkbutton(paramgroup, text="embed resources", variable = self.embed_resources).grid(sticky=tk.NW)
    tk.Checkbutton(paramgroup, text="use KHR_materials_common", variable = self.use_materials_common).grid(sticky=tk.NW)
    tk.Checkbutton(paramgroup, text="invert transparency", variable = self.invert_transparency).grid(sticky=tk.NW)
    tk.Checkbutton(paramgroup, text="enable default lighting", variable = self.default_lighting).grid(sticky=tk.NW)
    
    self.delete_dae = tk.IntVar()

    tk.Checkbutton(optgroup, text="Delete DAE files after conversion (!!!) [disabled]", variable = self.delete_dae).grid(sticky=tk.NW)

    self.convertbutton = tk.Button(self, state=tk.DISABLED, text="CONVERT", command = self.convert, width = 30, font = 'bold')
    self.convertbutton.grid(row = 4, column = 0, padx = 10, pady = 10, columnspan = 3, ipady = 2)
    
  def yview(self, *args):
    apply(self.fromlist.yview, args)
    apply(self.tolist.yview, args)

  def newSettings(self, event = None):
    self.fromlist.delete(0, tk.END)
    self.tolist.delete(0, tk.END)
    self.embed_resources.set(0)
    self.use_materials_common.set(0)
    self.invert_transparency.set(0)
    self.default_lighting.set(0)
    self.delete_dae.set(0)
    self.convertbutton.config(state = tk.DISABLED)

  def openSettings(self, event = None):
    file = tkFileDialog.askopenfile(parent = self, title = "Select Settings File:")
    if not file: return
    self.newSettings()
    for line in file:
      l = line.strip().split('=')
      if l[0] == 'src':
        path = os.path.normpath(l[1])
        self.fromlist.insert(tk.END, path)
      elif l[0] == 'dst':
        path = os.path.normpath(l[1])
        self.tolist.insert(tk.END, path)
      elif l[0] == 'params':
        params = l[1].split(';')
        for p in params:
          if p == "-e": self.embed_resources.set(1)
          if p == "-k": self.use_materials_common.set(1)
          if p == "-i": self.invert_transparency.set(1)
          if p == "-l": self.default_lighting.set(1)
      elif l[0] == 'options':
        options = l[1].split(';')
        for o in options:
          if o == "deldae": self.delete_dae.set(1)
    file.close()
    self.convertbutton.config(state = tk.NORMAL)

  def saveSettings(self, event = None):
    file = tkFileDialog.asksaveasfile(parent = self, title = "Set Settings File:")
    if not file: return
    file.write('{}\n'.format(self.MAGIC))
    for i in range(0, self.fromlist.size()):
      source = os.path.normpath(self.fromlist.get(i))
      dest = os.path.normpath(self.tolist.get(i))
      file.write('src={}\n'.format(source))
      file.write('dst={}\n'.format(dest))
    file.write('params={}\n'.format(';'.join(self.getParams())))
    file.write('options={}\n'.format(';'.join(self.getOptions())))
    file.close()

  def quit(self, event = None):
    sys.exit(0)

  def onFromButton(self, event = None):
    folder = tkFileDialog.askdirectory(mustexist = True, parent = self, title="Select a source folder with COLLADA files:")
    if not folder: return
    folder = os.path.normpath(folder)
    self.fromlist.insert(tk.END, folder)
    self.tolist.insert(tk.END, folder)
    self.convertbutton.config(state = tk.NORMAL)

  def onFromListSelect(self, event):
    pos =  self.fromlist.curselection()
    if not pos: return
    pos = pos[0]
    self.tolist.select_clear(0, tk.END)
    self.tolist.selection_set(int(pos))

  def onToListSelect(self, event):
    item = self.tolist.curselection()
    if not item: return
    item = item[0]
    folder = tkFileDialog.askdirectory(title="Select a target folder:")
    if not folder: return
    folder = os.path.normpath(folder)
    self.tolist.delete(item)
    self.tolist.insert(item, folder)

  def onFromListKeyDown(self, event):
    key = event.keysym
    item = self.fromlist.curselection()

    if not item: return
    item = int(item[0])

    jumps = {'Home': -99999, 'End' : 99999, 'Down': 1, 'Up'  : -1, 'Prior': -10, 'Next': 10}

    if key == 'Delete' or key == 'BackSpace':
      self.fromlist.delete(item)
      self.tolist.delete(item)
      if self.fromlist.size() == 0:
        self.convertbutton.config(state = tk.DISABLED)
    elif key in jumps:
      for l in [self.fromlist, self.tolist]:
        l.select_clear(0, tk.END)
        l.selection_set( max(0, min(self.fromlist.size()-1, item + jumps[key])))

  def convert(self):
    progress = ProgressWindow()
    parameters = self.getParams()
    sourcelist = []
    destlist = []
    for i in range(0, self.fromlist.size()):
      sourcelist.append(self.fromlist.get(i))
      destlist.append(self.tolist.get(i))
    convertFiles(sourcelist, destlist, parameters, progress)

  def getParams(self):
    params = []
    if self.embed_resources.get(): params.append('-e')
    if self.use_materials_common.get(): params.append('-k')
    if self.invert_transparency.get(): params.append('-i')
    if self.default_lighting.get(): params.append('-l')
    return params

  def getOptions(self):
    opts = []
    if self.delete_dae.get(): opts.append('deldae')
    return opts
    


def convertFiles(sourcelist, destlist, parameters, progress = None):
  if not checkCommand():
    if progress: 
      progress.destroy()
      tkMessageBox.showerror('batchgltf', 'collada2gltf not found in path')
    else: print 'ERROR: collada2gltf not found in path\n'
    return False

  for i in range(0, len(sourcelist)):
    source = sourcelist[i]
    dest = destlist[i]
    for f in os.listdir(source):
      if f.lower().endswith(".dae"):
        destfile = f[:f.rindex('.')]
        convertFile(os.path.join(source, f), dest, destfile, parameters, progress)
  return True

def convertFile(file, outputfolder, name, parameters, progress = None):
  cmd = ['collada2gltf', '-f', file, '-o', name] + parameters
  cmdstr = ' '.join(cmd) + '\n'

  currdir = os.getcwd()
  os.chdir(outputfolder)

  output = subprocess.check_output(cmd)
  if not progress: 
    print cmdstr
    print output
  else: 
    progress.add(cmdstr)
    progress.add(output)

  os.chdir(currdir)

def checkCommand():
  command = ["collada2gltf", "-v"]
  try:
    with open(os.devnull, "w") as fnull:
      result = subprocess.call(command, stdout = fnull, stderr = fnull)
      return True
  except:
    return False

def runFromCLI(param):
  file = open(param, mode = 'r')
  fromlist = []
  tolist = []
  for line in file:
    l = line.strip().split('=')
    if l[0] == 'src': fromlist.append(l[1])
    elif l[0] == 'dst': tolist.append(l[1])
    elif l[0] == 'params': params = l[1].split(';')
    elif l[0] == 'options': options = l[1].split(';')
  file.close()
  convertFiles(fromlist, tolist, params)


if len(sys.argv) > 1:
  runFromCLI(sys.argv[1])
else:
  app = App()
  app.mainloop()


