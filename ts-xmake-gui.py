#!/usr/bin/env python

import Tkinter as tk
import tkFileDialog
import os
import terminal
from shutil import rmtree
import conf_parse as cp
import json
from tkMessageBox import showinfo

class MainWin(tk.Frame):
    def __init__(self,master=None):
        tk.Frame.__init__(self,master)
        self.pack()
        self.createWidgets()

    def createWidgets(self):
        self.label_project=tk.Label(self,text="Project")
        self.label_project.grid(sticky=tk.W+tk.E+tk.N+tk.S,row=0,column=0,columnspan=6)

        self.projectdir_input_content=tk.StringVar()
        self.projectdir_input_content.set(os.getenv("HOME"))
        self.projectdir_input=tk.Entry(self,textvariable=self.projectdir_input_content)
        self.projectdir_input.grid(sticky=tk.W+tk.E+tk.N+tk.S,row=1,column=0,columnspan=4)

        self.browse_projectdir=tk.Button(self,text="Browse Project Dir",command=self.action_browse_projectdir)
        self.browse_projectdir.grid(sticky=tk.W+tk.E+tk.N+tk.S,row=1,column=4,columnspan=2)

        self.label_action=tk.Label(self,text="Action")
        self.label_action.grid(sticky=tk.W+tk.E+tk.N+tk.S,row=2,column=0,columnspan=6)

        self.config=tk.Button(self,text="Config",command=self.action_config,width=10)
        self.config.grid(sticky=tk.W+tk.E+tk.N+tk.S,row=3,column=0)

        self.build=tk.Button(self,text="Build",command=self.action_build,width=20)
        self.build.grid(sticky=tk.W+tk.E+tk.N+tk.S,row=3,column=1,columnspan=2)

        self.rebuild=tk.Button(self,text="Rebuild",command=self.action_rebuild,width=10)
        self.rebuild.grid(sticky=tk.W+tk.E+tk.N+tk.S,row=3,column=3)

        self.clean=tk.Button(self,text="Clean",command=self.action_clean,width=10)
        self.clean.grid(sticky=tk.W+tk.E+tk.N+tk.S,row=3,column=4)

        self.distclean=tk.Button(self,text="Distclean",command=self.action_distclean,width=10)
        self.distclean.grid(sticky=tk.W+tk.E+tk.N+tk.S,row=3,column=5)

        self.label_target=tk.Label(self,text="Target")
        self.label_target.grid(sticky=tk.W+tk.E+tk.N+tk.S,row=4,column=0,columnspan=2)

        self.target_list=tk.Listbox(self,width=0)
        self.target_list.grid(sticky=tk.W+tk.E+tk.N+tk.S,row=5,column=0,columnspan=2,rowspan=2)

        self.label_config=tk.Label(self,text="Config")
        self.label_config.grid(sticky=tk.W+tk.E+tk.N+tk.S,row=4,column=2,columnspan=4)

        self.reload_conf=tk.Button(self,text="Load",command=self.action_reload_conf)
        self.reload_conf.grid(sticky=tk.W+tk.E+tk.N+tk.S,row=5,column=2,columnspan=2)

        self.reconfig=tk.Button(self,text="Config",command=self.action_config)
        self.reconfig.grid(sticky=tk.W+tk.E+tk.N+tk.S,row=5,column=4,columnspan=2)

        self.configarea=tk.Text(self,width=0)
        self.configarea.grid(sticky=tk.W+tk.E+tk.N+tk.S,row=6,column=2,columnspan=4)

        self.reflesh_target_list()
        self.reflesh_configarea()

    def action_browse_projectdir(self):
        self.projectdir_input_content.set(tkFileDialog.askdirectory(parent=self,initialdir=self.projectdir_input_content.get(),title="Browse Project Dir"))
        self.reflesh_target_list()
        self.reflesh_configarea()

    def action_common(self,action,after_script=""):
        os.chdir(self.projectdir_input_content.get())
        if after_script:
            after_script=";"+after_script
        target=self.target_list.curselection()
        if not target:
            target=""
        else:
            target=self.targets[target[0]]
        terminal.run_keep_window("xmake "+action+" "+target+after_script)
        self.reflesh_target_list()
        self.reflesh_configarea()

    def action_build(self):
        self.action_common("build")

    def action_rebuild(self):
        self.action_common("build -r")

    def action_clean(self):
        self.action_common("clean")

    def action_distclean(self):
        self.action_common("clean")
        rmtree(".xmake")
        self.reflesh_target_list()
        self.reflesh_configarea()

    def action_config(self):
        st=self.configarea.get(1.0,tk.END)
        tarconf=None
        try:
            tarconf=json.loads(st)
            if not self.origin_config:
                raise()
        except:
            self.action_common("config")
            return
        cfs=[]
        for key,value in tarconf.items():
            if not key in self.origin_config or value!=self.origin_config[key]:
                cfs.append(" '--%s=%s'"%(key.replace("'","\\'"),value.replace("'","\\'")))
        self.action_common("config "+''.join(cfs))

    def action_reload_conf(self):
        self.reflesh_configarea()

    def read_conf(self):
        try:
            os.chdir(self.projectdir_input_content.get())
            f=open(".xmake/xmake.conf","r")
            configs=cp.loads(f.read())
            f.close()
            return configs
        except:
            return

    def reflesh_target_list(self):
        configs=self.read_conf() or {}
        targets={}
        if "_TARGETS" in configs:
            targets=configs["_TARGETS"]
        self.target_list.delete(0,tk.END)
        for key in targets:
            self.target_list.insert(tk.END,key)
        self.targets=[key for key in targets]

    def reflesh_configarea(self):
        self.configarea.delete(1.0,tk.END)
        target=self.target_list.curselection()
        if target:
            target=self.targets[target[0]]
            configs=self.read_conf()
            if configs and "_TARGETS" in configs and target in configs["_TARGETS"]:
                tarconf=configs["_TARGETS"][target]
                st=json.dumps(tarconf,indent=4,separators=(',',': '))
                self.configarea.insert(tk.END,st)
                self.origin_config=tarconf

win=MainWin()
win.master.title("xmake")
menubar=tk.Menu(win.master)
def show_about():
    showinfo("About","ts-xmake-gui\nAn ugly xmake gui\n\nMaintained by TitanSnow\nLicensed under The Unlicense")
menubar.add_command(label="About",command=show_about)
win.master.config(menu=menubar)
win.mainloop()
