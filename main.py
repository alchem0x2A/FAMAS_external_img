import sys,os,shutil,glob
import Tkinter as tk
import tkFileDialog as tF
import tkMessageBox as tM

#only available in gui-mode

# gui = False
#
# try:
#     import easygui
#     gui = True
# except ImportError:
#     gui = False

template = "~template"
line_has_img = r'"",1000,"-----","","","","","","","","","","","","","","STD","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","-----","","","","","","","","","","","-----","-----","","","-----"'
line_no_img = r'"",1000,"","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","-----","","","","","","","","","","","-----","-----","","","-----"'
line_des_detail = r'"Row","Column","Measure positionx(mm)","Measure positiony(mm)","Analysis technique (0:Sessile drop, 1:Ext./Cont.)","Analysis method (0:A half-angle, 1:Circle fitting, 2:Ellipse fitting, 3:Tangent)","3-State (0:No, 1:Yes)","Fit section setup (0:No, 1:Yes)","Fit section (dots)","Detect pitch(dots)","Algorithm (0:Auto, 1:Under 90 deg., 2:Over 90 deg.)","Image mode (0:Frame, 1:Even Field, 2:Odd Field)","Auto threshold level (0:No, 1:Yes)","Black level(%)","Threshold level","Image process area","Image process area","Image process area","Image process area","Correction of curvature (0:No, 1:Yes)","Radius of curvature(um)","ax(Inclination of base line)","b(Offset of base line)","S.A.(deg)","C.A.(deg)","C.A.R(deg)","V0(uL)","V1(uL)","V2(uL)","V3(uL)","V4(uL)","VR(%)","r(um)","h(um)","residual L(dot)","residual R(dot)","T(deg)","H(%)","View (0:Standard, 1:Wide 1, 2:Wide 2)"'
line_detail = r'-10000,-10000,0,0,0,0,60,30,0,0,1,70,128,30,30,30,30,0,1000000,0,0,0,0,0,0,0,0,1.47461577866652E-05,-1.47461577866652E-05,0,0,0,0,0,0,0,0'
line_no_detail = r'0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'
line_edge = r'"Row","Column","L1 x   ","L1 y ","L2 x","L2 y","L3 x","L3 y","R1 x","R1 y","R2 x","R2 y","R3 x","R3 y","TOP x","TOP y       "'
line_pixel = r'"Row","Column","Horizontal(dot)","Vertical(dot)","Diameter(um)",'

num_break = 3
num_col = 10
num_row = 48


class MainApp(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.file_type = None
        self.label = tk.Label(text = "Folder or Single Image ?")
        self.label.pack(side = "top")
        self.bt_dir = tk.Button(text = "Folder", command = self.fun_bt_dir)
        self.bt_file = tk.Button(text = "Image(s)", command = self.fun_bt_file)
        self.bt_dir.pack()
        self.bt_file.pack()



    def fun_bt_file(self):
        self.file_type = "f"
        self.get_file_dir()

    def fun_bt_dir(self):
        self.file_type = "d"
        self.get_file_dir()

    def get_file_dir(self):
        options = {"parent":self.parent}
        if self.file_type == "f":
            options["filetypes"] = [("BitMap Images", ".bmp")]
            options["initialdir"] = "."
            options["title"] = "Choose Image(s)"
            options["multiple"] = 1
            files = tF.askopenfilename(**options)
            stat = []
            info = []
            for f in files:
                [s,i] = RenameFig(f)
                stat.append(s)
                info.append(i)
            fail_count = stat.count("e")
            tM.showinfo("Convert Result", \
            "Suucessfully converted %d/%d files"%(len(stat)-fail_count, len(stat)) ,**{"parent" : self.parent})
            self.parent.destroy()
        if self.file_type == "d":
            options["initialdir"] = "."
            f = tF.askdirectory(**options)
            [s,i] = RenameFig(f)
            if s == "e":
                tM.showinfo("Convert Result", "Error :"+i , **{"parent" : self.parent})
            else:
                tM.showinfo("Convert Result", "Sucess!" , **{"parent" : self.parent})
            self.parent.destroy()


def MimicCSV(num_figs, out):
    if num_figs is not 0:
        shutil.copyfile(template, out)
        f_out = open(out, "ab")
        # Table part
        for i in range(num_figs):
            f_out.write(line_has_img+'\r\n')
        for i in range(num_row - num_figs):
            f_out.write(line_no_img+'\r\n')
        f_out.write('"[WORKSHEET]"\r\n')
        f_out.write('\r\n'*num_break)

        # Detail part
        f_out.write('"[DETAIL]"\r\n')
        f_out.write(line_des_detail+'\r\n')
        for i in range(1,num_row+1):
            for j in range(1,num_col+1):
                if i <= num_figs and j == 1:
                    f_out.write("%d,%d,"%(i,j)+line_detail+'\r\n')
                else:
                    f_out.write("%d,%d,"%(i,j)+line_no_detail+'\r\n')
        f_out.write('"[DETAIL]"\r\n')
        f_out.write('\r\n'*num_break)

        # Edge part
        f_out.write('"[EDGE]"\r\n')
        f_out.write(line_edge+'\r\n')
        for i in range(1,num_row+1):
            for j in range(1,num_col+1):
                if i <= num_figs and j == 1:
                    f_out.write("%d,%d"%(i,j)+',-5'+',0'*13+'\r\n')
                else:
                    f_out.write("%d,%d"%(i,j)+',0'*14+'\r\n')
        f_out.write('"[EDGE]"\r\n')
        f_out.write('\r\n'*num_break)

        # Pixel part
        f_out.write('"[PIXEL]"\r\n')
        f_out.write(line_pixel+'\r\n')
        for i in range(1,num_row+1):
            for j in range(1,num_col+1):
                if i <= num_figs and j == 1:
                    f_out.write("%d,%d"%(i,j)+',604'+',604'+',480'+'\r\n')
                else:
                    f_out.write("%d,%d"%(i,j)+',0'*3+'\r\n')
        f_out.write('"[PIXEL]"\r\n')
        f_out.write('\r\n'*num_break)

        f_out.write('"[EOF]"\r\n')

        f_out.close()

def RenameFig(dir_fig):
    abs_dir = os.path.abspath(dir_fig)
    dir_father = os.path.dirname(abs_dir)
    dir_name = os.path.basename(abs_dir)

    name_root = None
    if os.path.exists(abs_dir) is not True:
        return ["e","The item you choose does not exists, exit!"]

    if os.path.isdir(abs_dir) is not True:
        print dir_name
        if '.bmp' in dir_name:
            name_root = os.path.join(dir_father, os.path.splitext(dir_name)[0]+"_new")

            success_mkdir = False
            while success_mkdir is not True:
                try:
                    os.mkdir(name_root)
                    success_mkdir = True
                except OSError:
                    # return ["e","The directory with the same name has existed, delete!"]
                    os.removedirs(name_root)

            shutil.copyfile(abs_dir, os.path.join(name_root, os.path.basename(name_root)+"_R0001C01.bmp"))
            MimicCSV(1, name_root+".csv")
            return ["s", name_root+".csv"]
        else:
            return ["e", "The file is not a bmp image, exit!\n"]
    else:
        # print dir_father
        img_pattern = os.path.join(dir_father, dir_name, "*.bmp")
        all_imgs = glob.glob(img_pattern)
        if len(all_imgs) == 0:
            return ["e", "No bmp images in the folder, exit!"]

        else:
            name_root = os.path.join(dir_father, dir_name+'_new')
            # print name_root

            success_mkdir = False
            while success_mkdir is not True:
                try:
                    os.mkdir(name_root)
                    success_mkdir = True
                except OSError:
                    # print "The directory with the same name has existed, delete!"
                    os.removedirs(name_root)

            for img in sorted(all_imgs):
                i = sorted(all_imgs).index(img)
                shutil.copyfile(img, os.path.join(name_root, os.path.basename(name_root)+"_R%04dC01.bmp"%(i+1)))
            MimicCSV(len(all_imgs), name_root+".csv")
            return ["s", name_root+".csv"]

def main(*args):
    if len(args) > 2:
        print "Error: Too many input variables!"
    elif len(args) == 2:
        [status, info] = RenameFig(args[1])
        if status == "e":
            print "Error: %s"%info
        else:
            print "Success! Please open file %s"%info
    else: #no input

        window = tk.Tk()
        MainApp(window).pack(side = "top", fill = "both", expand = True)
        window.mainloop()







if __name__ == '__main__':
    # MimicCSV(2, 'test.csv')
    # RenameFig('test_old')
    print sys.argv
    main(sys.argv)
