#By OTREE    Bilibili@O-TREE
#from ctypes import Union
#from ensurepip import version
from msilib.schema import Media
from pyexpat import ExpatError
import re
import shlex
import subprocess
import threading
import time
import tkinter as tk
import sys
import ctypes
from tkinter import Menu, filedialog, simpledialog 
from tkinter import messagebox
import tkinter.font as tkFont
import webbrowser
import zipfile
#from turtle import title
import PIL.Image, PIL.ImageTk
import os

version="1.2.8"

root_path = os.path.split(os.path.realpath(__file__))[0] + '\\'
print(root_path)
os.system(f"cd {root_path}\lib\scrcpy")
print(f"found adb path:{root_path}\lib\scrcpy")
if os.path.exists(r"lib\\scrcpy\\adb.exe") is False:
    messagebox.showerror(r"致命错误","致命错误：ADB工具“lib\scrcpy\adb.exe”丢失！！！请重新下载安装！\n联系邮箱:ocr_8@qq.com")

if os.path.exists("lib\data.dll") is False:
    messagebox.showerror("致命错误","致命错误：配置文件“lib\data.dll”丢失！！！请重新下载安装！\n联系邮箱:ocr_8@qq.com")

if os.path.exists("lib\scrcpy") is False:
    messagebox.showerror("错误","功能错误：库文件夹lib\scrcpy丢失！！！请重新下载安装！\n联系邮箱:ocr_8@qq.com")


maximizebutton_status = '□'
duration = 0
window_size=[1000,800]#以列表形式存储窗口大小数据
device_id_list = []
powershell_process = None

def main():
    #声明区
    global selected_device
    global list_var
    global device_listbox
    global message_label
    global output_text
    global update_interval
    global main_window
    global command_input
    global title_text
    global bottom_label
    global command_execute_button
    global icon_photo
    global icon24_photo
    global photo_sw
    global photo_pay
    global ycts_logo_img
    global powershell_process
    #global icon_file

    #global execute_adb_basic_command
    main_window=tk.Tk()#创建窗口(也叫实例化，只有实例化之后才能处理与图片，界面有关的代码)
    #设定界面相关参数
    #main_window.iconbitmap('icon.ico')
    main_window.title(f'ADBgenius v{version}')           
    main_window.columnconfigure(0,minsize=50)
    main_window.configure(bg='#1e1e1e')#背景颜色'PaleTurquoise'
    main_window.geometry('1000x800+300+100')  
    #main_window.resizable(0,0)#锁定窗口大小
    main_window.overrideredirect(True)#取消默认窗口管理器工具栏

    user32 = ctypes.windll.user32
    GWL_STYLE = -16
    GWL_EXSTYLE = -20
    WS_SYSMENU = 0x00080000
    WS_MINIMIZEBOX = 0x00020000
    WS_EX_APPWINDOW = 0x00040000
    WS_EX_TOOLWINDOW = 0x00000080
    SW_MINIMIZE = 6
    SW_RESTORE = 9
    SWP_FRAMECHANGED = 0x0020
    SWP_NOMOVE = 0x0002
    SWP_NOSIZE = 0x0001
    SWP_NOZORDER = 0x0004
    SWP_NOACTIVATE = 0x0010

    def apply_win32_styles():
        if sys.platform != "win32":
            return
        hwnd = main_window.winfo_id()
        style = user32.GetWindowLongW(hwnd, GWL_STYLE)
        style |= WS_SYSMENU | WS_MINIMIZEBOX
        user32.SetWindowLongW(hwnd, GWL_STYLE, style)
        exstyle = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        exstyle |= WS_EX_APPWINDOW
        exstyle &= ~WS_EX_TOOLWINDOW
        user32.SetWindowLongW(hwnd, GWL_EXSTYLE, exstyle)
        user32.SetWindowPos(
            hwnd,
            0,
            0,
            0,
            0,
            0,
            SWP_FRAMECHANGED | SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE,
        )

    def minimize_window():
        if sys.platform != "win32":
            return
        hwnd = main_window.winfo_id()
        user32.ShowWindow(hwnd, SW_MINIMIZE)

    def restore_window(focus_only=False):
        if sys.platform != "win32":
            return
        hwnd = main_window.winfo_id()
        if not focus_only:
            user32.ShowWindow(hwnd, SW_RESTORE)
        user32.SetForegroundWindow(hwnd)
        main_window.lift()
        main_window.focus_force()
        main_window.attributes("-topmost", True)
        main_window.attributes("-topmost", False)

    def on_window_map(_event):
        restore_window(focus_only=True)

    main_window.update_idletasks()
    main_window.after(0, apply_win32_styles)
    main_window.bind("<Map>", on_window_map)



    #图片初始化区
    #password = TECH OTAKUS ILLUMINATE THE WORLD --> RC4 --> base64 = D2rDvGgtw6rCqsKbPl8zQEwdPgfDusODc8KlMcKKwqoeUMOxWAx7w4DDj8OG 取前16位->D2rDvGgtw6rCqsKb
    with zipfile.ZipFile('lib/data.dll', 'r') as zip_ref:
        with zip_ref.open('logo.png',pwd="D2rDvGgtw6rCqsKb".encode()) as file:
            img1 = PIL.Image.open(file)  # 打开图片
            ycts_logo_img = PIL.ImageTk.PhotoImage(image=img1)# 用PIL模块的PhotoImage打开png

        with zip_ref.open('pay.png',pwd="D2rDvGgtw6rCqsKb".encode()) as file:
            img3 = PIL.Image.open(file)  # 打开图片
            photo_pay = PIL.ImageTk.PhotoImage(image=img3)# 用PIL模块的PhotoImage打开png
            
        with zip_ref.open('sw.png',pwd="D2rDvGgtw6rCqsKb".encode()) as file:
            img4 = PIL.Image.open(file)  # 打开图片
            photo_sw = PIL.ImageTk.PhotoImage(image=img4)# 用PIL模块的PhotoImage打开png

        with zip_ref.open('icon32.png',pwd="D2rDvGgtw6rCqsKb".encode()) as file:#不再自动关闭的打开：因为后面还要用------好吧，不用了...
            icon_img = PIL.Image.open(file)  # 打开图片
            icon_photo = PIL.ImageTk.PhotoImage(image=icon_img)# 用PIL模块的PhotoImage打开png
            main_window.iconphoto(True, icon_photo)

        with zip_ref.open('icon24.png',pwd="D2rDvGgtw6rCqsKb".encode()) as file:#不再自动关闭的打开：因为后面还要用------好吧，不用了...
            icon_img = PIL.Image.open(file)  # 打开图片
            icon24_photo = PIL.ImageTk.PhotoImage(image=icon_img)# 用PIL模块的PhotoImage打开png






    #普通变量初始化区
    selected_device = None  # 全局变量，用于保存选中的设备名称
    update_interval = 1  # 全局变量，用于保存自动更新间隔时间，默认为1秒







    #字符变量初始化区
    title_text = tk.StringVar()#定义为字符变量
    title_text.set(f'ADB genuius v{version} - device:None')



    #顶部菜单函数


    def Exit():
        if powershell_process and powershell_process.poll() is None:
            powershell_process.terminate()
        subprocess.run(['adb','kill-server'], shell=True, capture_output=True, text=True)
        main_window.destroy()

    '''#顶部菜单
    menuBar = tk.Menu(main_window)
    # 建立菜单类别对象，并将此菜的类别命名file，tearoff设置为False
    menuFile = tk.Menu(menuBar, tearoff=False)
    # 建立分层菜单，让此子功能列表与父菜单建立链接
    menuBar.add_cascade(label='file', menu=menuFile)
    # 在file菜单内建立菜单列表
    #menuFile.add_command(label='Save', command=Save)
    menuFile.add_separator()#分割线
    menuFile.add_command(label='Exit', command=Exit)
    
    menuHelp = tk.Menu(menuBar, tearoff=False)
    menuBar.add_cascade(label='help', menu=menuHelp)
    #menuHelp.add_command(label='Help', command=Help)
    #menuHelp.add_command(label='Abaot', command=About)
    main_window.config(menu=menuBar)#显示菜单对象'''


    
    
    #===============================================================================================命令行栏

    '''
    # 创建一个Frame来放置Text控件，并设置距离左边(x)400,顶部35，底部300(以周围部件的距离为标准)，并随主窗口大小改变
    text_frame = tk.Frame(main_window)
    text_frame.pack(fill=tk.BOTH, expand=True, padx=(396,0), pady=(60, 300))
    
    # 创建一个Text控件，用于显示命令执行结果
    output_text = tk.Text(text_frame, wrap=tk.WORD, borderwidth=4, bg='#1e1e1e', foreground='#ffffff',highlightbackground='#3c3c3c',highlightcolor='#3c3c3c', font=('微软雅黑','12'), state = tk.NORMAL)
    # 通过place()方法设置Text控件距离Frame左边0像素，从x=0开始向右填充
    output_text.place(x=0, relwidth=1.0, relheight=1.0)
    
    alabel = tk.Label(text_frame,background='#1e1e1e',justify='left',text='').pack(fill='y', expand=True, pady=(0,2), anchor='e')#place(relheight=1, width=5,rely=0,)
    output_text_label = tk.Label(main_window,text=' 输出：', bg='#1e1e1e', foreground='#ffffff', font=('微软雅黑', '13'),anchor='w')
    output_text_label.place(x=400, relwidth=1, height=25, y=35)

    output_text.tag_configure('error_tag',foreground='red',background='#be8a8a') #设置tag即插入文字的大小,颜色等
    '''

    text_frame = tk.Frame(main_window, background='#1e1e1e')
    text_frame.pack(fill=tk.BOTH, expand=True, padx=(396,0), pady=(60, 300))
    text_frame.rowconfigure(0, weight=1)
    text_frame.columnconfigure(1, weight=1)

    output_text = tk.Text(text_frame, wrap=tk.WORD, borderwidth=4, bg='#1e1e1e', foreground='#ffffff', highlightbackground='#3c3c3c', highlightcolor='#3c3c3c', font=('微软雅黑','12'), state=tk.NORMAL)
    output_text.grid(row=0, column=0, columnspan=3, sticky='nsew', padx=2, pady=(2, 0))

    output_text_label = tk.Label(main_window, text=' 输出：', bg='#1e1e1e', foreground='#ffffff', font=('微软雅黑', '13'), anchor='w')
    output_text_label.place(x=400, relwidth=1, height=25, y=35)

    input_label = tk.Label(text_frame, text='PS>', bg='#1e1e1e', foreground='#ffffff', font=('微软雅黑', '12'))
    input_label.grid(row=1, column=0, sticky='w', padx=(8, 4), pady=6)
    command_input = tk.Entry(text_frame, borderwidth=4, bg='#2e2e2e', foreground='#ffffff', highlightbackground='#e1e1e1', highlightcolor='#e1e1e1', font=('微软雅黑', '12'))
    command_input.grid(row=1, column=1, sticky='ew', padx=(0, 6), pady=6)

    command_execute_button = tk.Button(text_frame, text="执行", activebackground='#1177bb', activeforeground='#ffffff', foreground='#ffffff', background='#0e639c', borderwidth=0, command=active_execute_powershell_command)
    command_execute_button.grid(row=1, column=2, sticky='e', padx=(0, 8), pady=6)
    command_execute_button.bind('<Enter>', lambda event: command_execute_button.config(bg='#1177bb'))
    command_execute_button.bind('<Leave>', lambda event: command_execute_button.config(bg='#0e639c'))
    command_execute_button.config(state=tk.NORMAL)
    command_input.bind('<Return>', lambda event: active_execute_powershell_command())

    output_text.tag_configure('error_tag',foreground='red',background='#be8a8a') #设置tag即插入文字的大小,颜色等
    #===============================================================================================命令行栏

    def start_powershell_console():
        global powershell_process
        powershell_process = subprocess.Popen(
            ['powershell', '-NoLogo', '-NoExit', '-Command', '-'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace',
            bufsize=1
        )

        def read_stream(stream, tag=None):
            for line in iter(stream.readline, ''):
                if line:
                    output_text.insert(tk.END, line, tag)
                    output_text.see(tk.END)

        stdout_thread = threading.Thread(target=read_stream, args=(powershell_process.stdout, None))
        stderr_thread = threading.Thread(target=read_stream, args=(powershell_process.stderr, 'error_tag'))
        stdout_thread.daemon = True
        stderr_thread.daemon = True
        stdout_thread.start()
        stderr_thread.start()

    start_powershell_console()


    #===============================================================================================左菜单栏
    
    #------------------布局区
    leftmenubar = tk.Label(main_window,background='#252526',justify='left',text='').place(relheight=1, width=400,relx=0,rely=0)#底
    
    # 创建一个Listbox控件，并使用tk.StringVar来绑定设备列表
    list_var = tk.StringVar()
    device_listbox = tk.Listbox(main_window,background='#333333', foreground='#ffffff',highlightbackground='#3c3c3c',highlightcolor='#3c3c3c', listvariable=list_var)
    device_listbox.place(x=50,y=50,height=150,width=300)

    # 创建一个按钮，用于选择设备
    select_button = tk.Button(main_window, text="切换至该设备", activebackground='#1177bb', activeforeground='#ffffff', foreground='#ffffff',background='#0e639c',borderwidth=0, command=select_device)
    select_button.place(x=50,y=200,height=30,width=200)
    select_button.bind('<Enter>', lambda event: select_button.config(bg='#1177bb'))
    select_button.bind('<Leave>', lambda event: select_button.config(bg='#0e639c'))

    '''.bind('<Enter>', lambda event: .config(bg='#1177bb'))
    .bind('<Leave>', lambda event: .config(bg='#0e639c'))'''
    
    '''# 创建一个按钮，用于执行adb命令
    execute_button = tk.Button(main_window, text="执行ADB命令", command='')#execute_adb_command, state=tk.DISABLED)  # 初始设置按钮为无法按下状态
    execute_button.pack()'''
    # 启动线程更新设备列表
    update_thread = threading.Thread(target=update_device_listbox)
    update_thread.daemon = True  # 将线程设置为守护线程，当主线程结束时，自动结束守护线程
    update_thread.start()

    # 创建一个按钮，用于手动刷新设备列表
    refresh_button = tk.Button(main_window, text="手动刷新", activebackground='#1177bb', activeforeground='#ffffff', foreground='#ffffff',background='#0e639c',borderwidth=0, command='')#refresh_devices)
    refresh_button.place(x=250,y=200,height=30,width=100)
    refresh_button.bind('<Enter>', lambda event: refresh_button.config(bg='#1177bb'))
    refresh_button.bind('<Leave>', lambda event: refresh_button.config(bg='#0e639c'))



    #主快捷键区
    separate1 = tk.Label(main_window,background='#3c3c3c', fg='#b2b2b2')#分隔
    separate1.place(x=25,y=250,height=2,width=350)

    basic_button_font0 = tkFont.Font(size=16)
    basic_button_font1 = tkFont.Font(size=21)
    back_button = tk.Button(main_window, text="⮌", font=basic_button_font0, activebackground='#1177bb', activeforeground='#ffffff', foreground='#ffffff',background='#0e639c',borderwidth=0, command=back_c)
    back_button.place(x=50,y=270,height=30,width=72)
    back_button.bind('<Enter>', lambda event: back_button.config(bg='#1177bb'))
    back_button.bind('<Leave>', lambda event: back_button.config(bg='#0e639c'))

    homebutton = tk.Button(main_window, text="⌂", font=basic_button_font0, activebackground='#1177bb', activeforeground='#ffffff', foreground='#ffffff',background='#0e639c',borderwidth=0, command=home_c)
    homebutton.place(x=125,y=270,height=30,width=72)
    homebutton.bind('<Enter>', lambda event: homebutton.config(bg='#1177bb'))
    homebutton.bind('<Leave>', lambda event: homebutton.config(bg='#0e639c'))

    multitaskbutton = tk.Button(main_window, text="≡", font=basic_button_font1, activebackground='#1177bb', activeforeground='#ffffff', foreground='#ffffff',background='#0e639c',borderwidth=0, command=multitask_c)
    multitaskbutton.place(x=200,y=270,height=30,width=72)
    multitaskbutton.bind('<Enter>', lambda event: multitaskbutton.config(bg='#1177bb'))
    multitaskbutton.bind('<Leave>', lambda event: multitaskbutton.config(bg='#0e639c'))

    separate2 = tk.Label(main_window,background='#3c3c3c', fg='#b2b2b2')#分隔
    separate2.place(x=295,y=268,height=36,width=2)

    powerbutton = tk.Button(main_window, text="○", font=basic_button_font0, activebackground='#1177bb', activeforeground='#ffffff', foreground='#ffffff',background='#0e639c',borderwidth=0, command=power_c)
    powerbutton.place(x=320,y=270,height=30,width=31)
    powerbutton.bind('<Enter>', lambda event: powerbutton.config(bg='#1177bb'))
    powerbutton.bind('<Leave>', lambda event: powerbutton.config(bg='#0e639c'))

    separate3 = tk.Label(main_window,background='#3c3c3c', fg='#b2b2b2')#分隔
    separate3.place(x=25,y=315,height=2,width=350)

    screenbutton = tk.Button(main_window, text="启用ADB投屏", activebackground='#1177bb', activeforeground='#ffffff', foreground='#ffffff',background='#0e639c',borderwidth=0, command=screen_projection)
    screenbutton.place(x=50,y=327,height=30,width=300)
    screenbutton.bind('<Enter>', lambda event: screenbutton.config(bg='#1177bb'))
    screenbutton.bind('<Leave>', lambda event: screenbutton.config(bg='#0e639c'))

    separate4 = tk.Label(main_window,background='#3c3c3c', fg='#b2b2b2')#分隔
    separate4.place(x=25,y=370,height=2,width=350)

    app_installbutton = tk.Button(main_window, text="安装应用", activebackground='#1177bb', activeforeground='#ffffff', foreground='#ffffff',background='#0e639c',borderwidth=0, command=Install_apps)
    app_installbutton.place(x=50,y=390,height=30,width=245)
    app_installbutton.bind('<Enter>', lambda event: app_installbutton.config(bg='#1177bb'))
    app_installbutton.bind('<Leave>', lambda event: app_installbutton.config(bg='#0e639c'))

    app_install_help_button = tk.Button(main_window, text="失败?", activebackground='#1177bb', activeforeground='#ffffff', foreground='#ffffff',background='#0e639c',borderwidth=0, command=show_app_install_help)
    app_install_help_button.place(x=300,y=390,height=30,width=50)
    app_install_help_button.bind('<Enter>', lambda event: app_install_help_button.config(bg='#1177bb'))
    app_install_help_button.bind('<Leave>', lambda event: app_install_help_button.config(bg='#0e639c'))
    

    app_uninstallbutton = tk.Button(main_window, text="卸载应用", activebackground='#1177bb', activeforeground='#ffffff', foreground='#ffffff',background='#0e639c',borderwidth=0, command=Uninstall_apps)
    app_uninstallbutton.place(x=50,y=425,height=30,width=145)
    app_uninstallbutton.bind('<Enter>', lambda event: app_uninstallbutton.config(bg='#1177bb'))
    app_uninstallbutton.bind('<Leave>', lambda event: app_uninstallbutton.config(bg='#0e639c'))

    all_app_infbutton = tk.Button(main_window, text="查看所有应用", activebackground='#1177bb', activeforeground='#ffffff', foreground='#ffffff',background='#0e639c',borderwidth=0, command=all_app_inf)
    all_app_infbutton.place(x=205,y=425,height=30,width=145)
    all_app_infbutton.bind('<Enter>', lambda event: all_app_infbutton.config(bg='#1177bb'))
    all_app_infbutton.bind('<Leave>', lambda event: all_app_infbutton.config(bg='#0e639c'))



    devices_info_infbutton = tk.Button(main_window, text="设备信息 PRO", activebackground='#1177bb', activeforeground='#ffffff', foreground='#ffffff',background='#0e639c',borderwidth=0, command=devices_info)
    devices_info_infbutton.place(x=50,y=465,height=30,width=300)
    devices_info_infbutton.bind('<Enter>', lambda event: devices_info_infbutton.config(bg='#1177bb'))
    devices_info_infbutton.bind('<Leave>', lambda event: devices_info_infbutton.config(bg='#0e639c'))

    #===============================================================================================左菜单栏


    #===============================================================================================自制窗口管理器工具栏
    #工具栏底
    def MouseDown(event): # 不要忘记写参数event
        global mousX  # 全局变量，鼠标在窗体内的x坐标
        global mousY  # 全局变量，鼠标在窗体内的y坐标
    
        mousX=event.x  # 获取鼠标相对于窗体左上角的X坐标
        mousY=event.y  # 获取鼠标相对于窗左上角体的Y坐标
        
    def MouseMove(event):
        w=toolbar.winfo_x() # w为标签的左边距
        h=toolbar.winfo_y() # h为标签的上边距
        main_window.geometry(f'+{event.x_root - mousX-w}+{event.y_root - mousY-h}') # 窗体移动代码
        # event.x_root 为窗体相对于屏幕左上角的X坐标
        # event.y_root 为窗体相对于屏幕左上角的Y坐标
    title_font = tkFont.Font(size=11, family='微软雅黑')#, weight=tkFont.BOLD
    toolbar = tk.Label(main_window,background='#3c3c3c',justify='left', fg='#b2b2b2', font=title_font, textvariable=title_text)#工具栏
    toolbar.place(height=35, relwidth=1,relx=0,rely=0)
    toolbar.bind("<B1-Motion>",MouseMove)
    toolbar.bind("<Button-1>",MouseDown)
    
    #图标
    logo_label = tk.Label(main_window,image=icon24_photo,bg='#3c3c3c',borderwidth=0).place(x=6,y=6)

    #菜单
    menu_button_font = tkFont.Font(size='11',family='微软雅黑')#Menu button样式
    menu_file_button = tk.Button(main_window,activeforeground="#b2b2b2",foreground='#b2b2b2',#前景
                                activebackground="#505050",background='#3c3c3c',#背景
                                command='',text='文件',font=menu_button_font,borderwidth=0)
    menu_file_button.place(height=35, width=55,x=35,y=0)
    menu_file_button.bind('<Enter>', lambda event: menu_file_button.config(bg='#505050'))
    menu_file_button.bind('<Leave>', lambda event: menu_file_button.config(bg='#3c3c3c'))

    # 创建一个菜单按钮，用于下拉菜单
    menu_set_button = tk.Menubutton(main_window, activeforeground="#b2b2b2",foreground='#b2b2b2',#前景
                                    activebackground="#505050",background='#3c3c3c',
                                    text="设置", font=menu_button_font,borderwidth=0, direction='below')
    menu_set_button.place(height=35, width=55,x=90,y=0)
    # 创建主菜单
    set_menu = tk.Menu(menu_set_button, tearoff=False,
                    activeforeground="#b2b2b2",foreground='#b2b2b2',#前景
                    activebackground="#094771",background='#3c3c3c',activeborderwidth=0,
                    font=menu_button_font, borderwidth=0)
    menu_set_button.config(menu=set_menu)

    # 创建二级菜单
    set_sub_speed_menu = tk.Menu(set_menu, tearoff=False,
                    activeforeground="#b2b2b2",foreground='#b2b2b2',#前景
                    activebackground="#094771",background='#3c3c3c',activeborderwidth=0,
                    font=menu_button_font, borderwidth=0)

    # 添加主菜单项
    set_menu.add_cascade(label="自动更新速度", menu=set_sub_speed_menu)
    set_menu.add_command(label="反馈", command=lambda: feedback())
    set_menu.add_command(label="关于", command=lambda: about_ADBG())
    set_menu.add_command(label="赞助", command=lambda: patron())


    # 添加二级菜单项，并设置对应的命令处理函数
    set_sub_speed_menu.add_command(label="5秒", command=lambda: set_update_interval(5))
    set_sub_speed_menu.add_command(label="2秒", command=lambda: set_update_interval(2))
    set_sub_speed_menu.add_command(label="1秒", command=lambda: set_update_interval(1))
    set_sub_speed_menu.add_command(label="0.5秒", command=lambda: set_update_interval(0.5))
    set_sub_speed_menu.add_command(label="最快(高占用)", command=lambda: set_update_interval(0))

    # 创建一个菜单按钮，用于下拉菜单
    root_tools_button = tk.Menubutton(main_window, activeforeground="#b2b2b2",foreground='#b2b2b2',#前景
                                    activebackground="#505050",background='#3c3c3c',
                                    text="已ROOT设备工具", font=menu_button_font,borderwidth=0, direction='below')
    root_tools_button.place(height=35, width=135,x=145,y=0)
    # 创建主菜单
    root_tools_menu = tk.Menu(root_tools_button, tearoff=False,
                    activeforeground="#b2b2b2",foreground='#b2b2b2',#前景
                    activebackground="#094771",background='#3c3c3c',activeborderwidth=0,
                    font=menu_button_font, borderwidth=0)
    root_tools_button.config(menu=root_tools_menu)

    root_tools_menu.add_command(label="温度&使用率监看仪", command=lambda: temp_Monitor_tool())









    #用函数包装的按钮构件
    def Window_manager_Toolbar_Button(maximizebutton_status_):
        global maximizebutton_status
        maximizebutton_status = maximizebutton_status_
        
        print('window_size:',window_size)
        print('Maximize button status:',maximizebutton_status_)



        #退出键
        Exitbuttonfont = tkFont.Font(size=12, weight=tkFont.BOLD)#Exitbutton样式
        Exitbutton=tk.Button(main_window, foreground='#b2b2b2',activebackground="red",#activebackground是按钮按下后的颜色
                            background='#3c3c3c',command=Exit,text='×',font=Exitbuttonfont,borderwidth=0)
        Exitbutton.place(height=35, width=55,x=window_size[0]-55,y=0)#根据window_size中储存的窗口大小确定绝对位置
        Exitbutton.bind('<Enter>', lambda event: Exitbutton.config(bg='#e81123'))#进入时颜色
        Exitbutton.bind('<Leave>', lambda event: Exitbutton.config(bg='#3c3c3c'))#移出时颜色



        #最大化键
        def maximize():
            global window_size
            global maximizebutton_status
            if maximizebutton_status == '❐':#计算时判断
                maximizebutton_status = '□'
                window_size=[1000,800]#以列表形式存储窗口大小数据
                main_window.geometry('1000x800+300+100') 
                minimizebutton.destroy()#删除控件
                maximizebutton.destroy()
                Exitbutton.destroy()
                #toolbar.destroy()
                Window_manager_Toolbar_Button(maximizebutton_status)#启动控件加载
            else:
                maximizebutton_status = '❐'
                window_size=[1920,1080]#以列表形式存储窗口大小数据
                main_window.geometry('1920x1080+0+0')
                minimizebutton.destroy()#删除控件
                maximizebutton.destroy()
                Exitbutton.destroy()
                #toolbar.destroy()
                Window_manager_Toolbar_Button(maximizebutton_status)#启动控件加载
        
        if maximizebutton_status == '❐':#加载时判断
            maximizebutton_text = '❐'
            maximizebuttonfont = tkFont.Font(size=18, weight=tkFont.BOLD)#Exitbutton样式
        else:
            maximizebutton_text = '□'
            maximizebuttonfont = tkFont.Font(size=12, weight=tkFont.BOLD)#Exitbutton样式
        
        maximizebutton=tk.Button(main_window,activebackground="#505050", foreground='#b2b2b2',
                                background='#3c3c3c',command=maximize,text=maximizebutton_text,font=maximizebuttonfont,borderwidth=0)
        maximizebutton.place(height=35, width=55,x=window_size[0]-110,y=0)#根据window_size中储存的窗口大小确定绝对位置
        maximizebutton.bind('<Enter>', lambda event: maximizebutton.config(bg='#505050'))
        maximizebutton.bind('<Leave>', lambda event: maximizebutton.config(bg='#3c3c3c'))
        
            




        #最小化键
        minimizebuttonfont = tkFont.Font(size=12, weight=tkFont.BOLD)#Exitbutton样式
        minimizebutton=tk.Button(main_window,activebackground="#505050", foreground='#b2b2b2',
                                background='#3c3c3c',command=minimize_window,text='-',font=minimizebuttonfont,borderwidth=0)
        minimizebutton.place(height=35, width=55,x=window_size[0]-165,y=0)#根据window_size中储存的窗口大小确定绝对位置
        minimizebutton.bind('<Enter>', lambda event: minimizebutton.config(bg='#505050'))
        minimizebutton.bind('<Leave>', lambda event: minimizebutton.config(bg='#3c3c3c'))
    Window_manager_Toolbar_Button(maximizebutton_status)
    #===============================================================================================自制窗口管理器工具栏





    #底部消息栏
    bottom_label = tk.Label(main_window, background='#68217a',justify='left')
    bottom_label.place(relheight=0.03, relwidth=1,relx=0,rely=0.97)

    message_label = tk.Label(main_window, foreground='#ffffff', background='#68217a', text="  当前设备：None",anchor='w')# 创建一个Label控件，用于显示底部消息栏
    message_label.place(relheight=0.03, relwidth=0.2,relx=0,rely=0.97)




    


    
    main_window.mainloop()
    # 事件绑定，当窗口大小改变时，重新设置command_input的宽度
    
    


#------------------函数区

    
def get_adb_devices():
    result = subprocess.run(['adb','devices'], shell=True, capture_output=True, text=True)#把指令按函数分开防止恶意程序植入病毒
    if result.returncode == 0:
        output_lines = result.stdout.strip().split('\n')
        devices_info = [line.split('\t') for line in output_lines[1:]]
        return devices_info
    else:
        return None

def format_devices_list(list):
    formated_devices_list = []
    for id in list:
        try:
            command = ['adb','-s',str(id),'shell','getprop','ro.product.name']
            result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='UTF-8', errors='replace')
            if result.returncode == 0:
                formated_devices_list.append(id + '    ' + result.stdout.replace('\n',''))
            else:
                if "This adb server's $ADB_VENDOR_KEYS is not set" in result.stderr:
                    formated_devices_list.append(id + '  未授权')
                elif "offline" in result.stderr:
                    formated_devices_list.append(id + ' 已下线,正在重连')
                    command = ['adb','reconnect','offline']
                    result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='UTF-8', errors='replace')
        except Exception as e:
            messagebox.showerror(title=f'ADBgenius v{version}',message=f'列表刷新错误:\n{e}')
    return formated_devices_list

adb_Initialization_is_required = True
def update_device_listbox():
    global selected_device
    global device_id_list
    global adb_Initialization_is_required

    if adb_Initialization_is_required:
        text_1 = tk.Label(main_window, foreground='#ffffff', background='#1b1b1b', text='ADB初始化中\n这可能需要几秒...')# 创建一个Label控件，用于显示底部消息栏
        text_1.place(x=50,y=50,height=180,width=300)
        main_window.update()
    while True:
        devices_info = get_adb_devices()
        if adb_Initialization_is_required:
            text_1.destroy()
            adb_Initialization_is_required = False
        if devices_info:
            device_id_list = [device_info[0] for device_info in devices_info]
            list_var.set(format_devices_list(device_id_list))
            # 如果已经选择了设备，并且该设备不在当前在线设备列表中，则取消选择
            if selected_device and selected_device not in device_id_list:
                selected_device = None
                device_listbox.selection_clear(0, tk.END)
                title_text.set(f'ADB genuius v{version} - device:None')
                message_label.config(text="  当前设备：None")
        else:
            list_var.set([])  # 如果没有设备在线，清空Listbox
            title_text.set(f'ADB genuius v{version} - device:None')
            message_label.config(text="  当前设备：None")

        time.sleep(update_interval)  # 根据全局变量update_interval的值设置更新设备列表的速度

def update_device_listbox_once():#独立出来的主动刷新模块，防止多个进程同时使用一个函数导致进程冲突
    global selected_device
    devices_info = get_adb_devices()
    if devices_info:
        device_id_list = [device_info[0] for device_info in devices_info]
        list_var.set(format_devices_list(device_id_list))
        # 如果已经选择了设备，并且该设备不在当前在线设备列表中，则取消选择
        if selected_device and selected_device not in device_id_list:
            selected_device = None
            device_listbox.selection_clear(0, tk.END)
            title_text.set(f'ADB genuius v{version} - device:None')
            message_label.config(text="  当前设备：None")
    else:
        list_var.set([])  # 如果没有设备在线，清空Listbox
        title_text.set(f'ADB genuius v{version} - device:None')
        message_label.config(text="  当前设备：None")

def select_device():
    global selected_device
    global device_name
    selected_index = device_listbox.curselection()
    if selected_index:
        index = int(selected_index[0])
        #selected_device = device_listbox.get(index)
        print(device_id_list)
        print(index)
        selected_device = device_id_list[index]
        try:
            ret = execute_shortcut_commands(command=['shell','getprop','ro.product.name'])
            if ret.returncode != 0:
                selected_device = None
                message_label.config(text="  当前设备：None")
                title_text.set(f'ADB genuius v{version} - device:None')
                command_execute_button.config(state=tk.NORMAL)
                if "This adb server's $ADB_VENDOR_KEYS is not set" in ret.stderr:
                    messagebox.showerror(title=f'ADBgenius v{version}',message='请在设备上确认授权！如没有弹窗请重新拔插设备然后授权！')
                else:
                    messagebox.showerror(title=f'ADBgenius v{version}',message=f'错误:\n{ret.stderr}')
            else:
                device_name = ret.stdout.replace('\n', '')
                message_label.config(text=f"  当前设备：{selected_device}")
                title_text.set(f'ADB genuius v{version} - device: {selected_device}')
                command_execute_button.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror(title=f'ADBgenius v{version}',message=f'错误:\n{e}')
    else:
        selected_device = None
        message_label.config(text="  当前设备：None")
        title_text.set(f'ADB genuius v{version} - device:None')
        command_execute_button.config(state=tk.NORMAL)

def active_execute_adb_command():
    #output_text.insert(tk.END, 'Waiting for device response\n')
    execute_adb_command('N')

def active_execute_powershell_command():
    global output_text
    global command_input
    global powershell_process
    command = command_input.get().strip()
    if not command:
        return
    output_text.insert(tk.END, f"PS> {command}\n")
    output_text.see(tk.END)
    command_input.delete(0, tk.END)
    if powershell_process and powershell_process.poll() is None:
        try:
            powershell_process.stdin.write(command + "\n")
            powershell_process.stdin.flush()
        except Exception as e:
            messagebox.showerror(title=f'ADBgenius v{version}',message=f'PowerShell执行错误:\n{e}')
    else:
        messagebox.showerror(title=f'ADBgenius v{version}',message='PowerShell控制台未启动或已退出。')

def execute_adb_command(cmd):
    global selected_device
    global output_text
    global command_input
    if selected_device:
        #进程树函数
        def execute_thread(cmd_):
            global output_text
            global selected_device
            shell_root_path = os.getcwd()
            if cmd_ == 'N':#执行自定义命令
                command = command_input.get().strip()
                if not command:
                    return
                command = command.split(' ')
                print(command)
                adb_command = ['adb','-s',str(selected_device)]
                for i in range(len(command)):
                    adb_command.append(command[i])
                command_input.delete(0, tk.END)
                #print('execute command:',adb_command)
                output_text.insert(tk.END, shell_root_path + '> ' + ' '.join(adb_command))  # 显示输入的命令
                result = subprocess.run(adb_command, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    #output_text.delete("1.0", tk.END)  # 清空之前的结果
                    #output_text.insert(tk.END, '\nExecution succeeded!!!\n' + result.stdout)  # 显示命令执行结果
                    output_text.insert(tk.END, '\n' + result.stdout)  # 显示命令执行结果
                else:
                    #output_text.delete("1.0", tk.END)  # 清空之前的结果
                    output_text.insert(tk.END, '\n')
                    output_text.insert(tk.END, 'Execution failed!!!\n' + result.stderr, 'error_tag')  # 显示命令执行错误信息
                output_text.see(tk.END)#焦点（光标）移动到最后一个
            else:#执行快捷命令
                #print('execute command:',adb_command)
                output_text.insert(tk.END, shell_root_path + '> ' + ' '.join(adb_command))  # 显示输入的命令
                result = subprocess.run(adb_command, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    #output_text.delete("1.0", tk.END)  # 清空之前的结果
                    #output_text.insert(tk.END, '\nExecution succeeded!!!\n' + result.stdout)  # 显示命令执行结果
                    output_text.insert(tk.END, '\n' + result.stdout)  # 显示命令执行结果
                else:
                    #output_text.delete("1.0", tk.END)  # 清空之前的结果
                    output_text.insert(tk.END, '\n')
                    output_text.insert(tk.END, 'Execution failed!!!\n' + result.stderr, 'error_tag')  # 显示命令执行错误信息
                output_text.see(tk.END)#焦点（光标）移动到最后一个
        

        output_thread = threading.Thread(target=execute_thread(cmd))
        output_thread.setDaemon(True)
        output_thread.start()
        #timer(5)
        bottom_label.configure(bg='#cc6633')
        while return_info != True:#等待计时结束
            pass
        if output_thread.is_alive() is True:
            messagebox.showwarning('警告','命令执行线程阻塞,可能是设备未响应或输入了特殊命令导致返回时间过长或持续返回。\n点击"确定"以取消命令执行并结束进程')

        bottom_label.configure(bg='#68217a')



            #刷新式多行读取（效果不好，停用）
        '''process = subprocess.Popen(adb_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        def read_output():
            while True:
                output = process.stdout.readline()
                if not output:
                    break
                print(output.strip())  # 处理输出，你可以根据需要进行适当的处理
                output_text.insert(tk.END, output.strip() + "\n")  # 在输出框中显示输出
                output_text.see(tk.END)  # 将焦点移动到输出框末尾

            # 处理错误输出
            while True:
                error = process.stderr.readline()
                if not error:
                    break
                print(error.strip())  # 处理错误输出

        output_thread = threading.Thread(target=read_output)
        output_thread.start()'''

            
            
        
    else:
        print('请选择设备')
        messagebox.showwarning('警告','请先选择设备再发送命令！！！')


#=---------------------------------------------------------------------------------快捷命令区

def Install_apps():
    if selected_device is None:
        messagebox.showwarning(title=f'ADBgenius v{version}',message='您还未选中设备！')
    else:
        app_pc_path = filedialog.askopenfilename(title='请选择安装包',filetypes=[('APK文件', '*.apk')])
        if app_pc_path:

            text_1 = tk.Label(main_window, foreground='#ffffff', background='#2b2b2b', text='正在安装中...\n\n请勿断电、断连或执行其他操作!')# 创建一个Label控件，用于显示底部消息栏
            text_1.place(relheight=1, relwidth=1,relx=0,rely=0)
            main_window.update()

            #s.mainloop()
            

            a_command = ['adb','-s',str(selected_device)]
            b_command = ['install', app_pc_path]#, '-r', '-t', '-d'
            for i in range(len(b_command)):
                a_command.append(b_command[i])
            result = subprocess.run(a_command, shell=True, capture_output=True, text=True, encoding='UTF-8', errors='replace')
            time.sleep(0.5)
            if 'Success' in result.stdout and result.returncode == 0:
                text_1.destroy()
                messagebox.showinfo(title=f'ADBgenius v{version}',message='成功安装"' + app_pc_path + '"')
            else:
                text_1.destroy()
                failure_info = match_install_failure_reason(result.stdout + '\n' + result.stderr)
                if failure_info:
                    failure_code, failure_reason = failure_info
                    messagebox.showerror(title=f'ADBgenius v{version}',message='安装失败!\n故障码:' + failure_code + '\n原因:' + failure_reason + '\n输出:' + str(result.stdout) + '\n错误:' + str(result.stderr))
                else:
                    messagebox.showerror(title=f'ADBgenius v{version}',message='安装失败!\n输出:' + str(result.stdout) + '\n错误:' + str(result.stderr))
                    show_app_install_help()



def match_install_failure_reason(install_output):
    failure_map = {
        'INSTALL_FAILED_ALREADY_EXISTS': '尝试安装一个已存在且签名不一致的应用。',
        'INSTALL_FAILED_INVALID_APK': 'APK 文件路径无效、文件损坏或格式不正确。',
        'INSTALL_FAILED_INVALID_URI': '提供的 APK 路径不是一个有效的 URI。',
        'INSTALL_FAILED_INSUFFICIENT_STORAGE': '设备存储空间不足。',
        'INSTALL_FAILED_DUPLICATE_PACKAGE': '系统已存在同包名的应用。',
        'INSTALL_FAILED_NO_MATCHING_ABIS': '应用包含 native 库，但当前设备 CPU 架构不支持。',
        'INSTALL_FAILED_UPDATE_INCOMPATIBLE': '新 APK 的签名与设备上已安装的旧版本不一致。',
        'INSTALL_FAILED_SHARED_USER_INCOMPATIBLE': '请求的共享用户 ID 与已安装的现有应用不兼容。',
        'INSTALL_FAILED_MISSING_SHARED_LIBRARY': '安装依赖一个共享库，但设备上不存在。',
        'INSTALL_FAILED_REPLACE_COULDNT_DELETE': '无法删除旧版本的应用，可能文件被锁定或权限错误。',
        'INSTALL_FAILED_DEXOPT': 'Dex 优化失败，通常是由于空间不足或损坏的 DEX 文件。',
        'INSTALL_FAILED_OLDER_SDK': '应用的 minSdkVersion 高于设备的 Android 版本。',
        'INSTALL_FAILED_CONFLICTING_PROVIDER': '应用声明的 Content Provider 授权与已安装的应用冲突。',
        'INSTALL_FAILED_NEWER_SDK': '应用的 targetSdkVersion 低于设备系统要求。',
        'INSTALL_FAILED_TEST_ONLY': 'APK 被标记为 testOnly，但未使用 -t 参数安装。',
        'INSTALL_PARSE_FAILED_NOT_APK': '选择的文件不是有效的 APK 文件。',
        'INSTALL_PARSE_FAILED_BAD_MANIFEST': 'AndroidManifest.xml 文件无法解析，可能已损坏。',
        'INSTALL_PARSE_FAILED_UNEXPECTED_EXCEPTION': '解析 APK 时发生意外异常。',
        'INSTALL_PARSE_FAILED_NO_CERTIFICATES': 'APK 没有签名。',
        'INSTALL_CANCELED_BY_USER': '用户在设备上取消安装。',
        'INSTALL_FAILED_ABORTED': '安装过程被主动中止。',
        'INSTALL_FAILED_VERIFICATION_FAILURE': '验证安装包时失败。',
        'INSTALL_FAILED_PACKAGE_CHANGED': '应用包名与预期不符。',
        'error: device not found': '无设备连接（adb devices 空列表）。',
        'error: device offline': '设备无响应（offline 状态）。',
        'error: device unauthorized': '设备未授权 USB 调试。',
        'Error: Unable to open file': 'ADB 无法读取指定的 APK 文件，路径错误或权限不足。',
        'Error: Permission denied': 'ADB 进程对 APK 文件没有读取权限。',
        'The APK file does not exist on disk': '文件路径错误或路径变量未正确展开。',
    }
    for failure_code, failure_reason in failure_map.items():
        if failure_code in install_output:
            return failure_code, failure_reason
    return None

def show_app_install_help():
    text = '''                                       安装失败故障码解析


Failure [INSTALL_FAILED_ALREADY_EXISTS: Attempt to re-install ... without first uninstalling.]
原因: 尝试安装一个已存在且签名不一致的应用。

Failure [INSTALL_FAILED_INVALID_APK: ...]
原因: APK 文件路径无效、文件损坏或格式不正确。

Failure [INSTALL_FAILED_INVALID_URI: ...]
原因: 提供的 APK 路径不是一个有效的 URI。

Failure [INSTALL_FAILED_INSUFFICIENT_STORAGE: ...]
原因: 设备存储空间不足。

Failure [INSTALL_FAILED_DUPLICATE_PACKAGE: ...]
原因: 系统已存在同包名的应用。

Failure [INSTALL_FAILED_NO_MATCHING_ABIS: Failed to extract native libraries, res=-113]
原因: 应用包含 native 库（如 arm64-v8a），但当前设备 CPU 架构不支持。

Failure [INSTALL_FAILED_UPDATE_INCOMPATIBLE: Package ... signatures do not match the previously installed version; ignoring!]
原因: 新 APK 的签名与设备上已安装的旧版本不一致。

Failure [INSTALL_FAILED_SHARED_USER_INCOMPATIBLE: ...]
原因: 请求的共享用户 ID 与已安装的现有应用不兼容。

Failure [INSTALL_FAILED_MISSING_SHARED_LIBRARY: ...]
原因: 安装依赖一个共享库，但设备上不存在。

Failure [INSTALL_FAILED_REPLACE_COULDNT_DELETE: ...]
原因: 无法删除旧版本的应用，可能文件被锁定或权限错误。

Failure [INSTALL_FAILED_DEXOPT: ...]
原因: Dex 优化失败，通常是由于空间不足或损坏的 DEX 文件。

Failure [INSTALL_FAILED_OLDER_SDK: ...]
原因: 应用的 minSdkVersion 高于设备的 Android 版本。

Failure [INSTALL_FAILED_CONFLICTING_PROVIDER: ...]
原因: 应用声明的 Content Provider 授权 (authority) 与已安装的应用冲突。

Failure [INSTALL_FAILED_NEWER_SDK: ...]
原因: 应用的 targetSdkVersion 低于设备系统要求（较少见，通常出现在系统升级后）。

Failure [INSTALL_FAILED_TEST_ONLY: ...]
原因: APK 被标记为 android:testOnly="true"，但未使用 -t 参数安装 (adb install -t ...)。

Failure [INSTALL_PARSE_FAILED_NOT_APK: ...]
原因: 选择的文件不是有效的 APK 文件。

Failure [INSTALL_PARSE_FAILED_BAD_MANIFEST: ...]
原因: AndroidManifest.xml 文件无法解析，可能已损坏。

Failure [INSTALL_PARSE_FAILED_UNEXPECTED_EXCEPTION: ...]
原因: 解析 APK 时发生意外异常。

Failure [INSTALL_PARSE_FAILED_NO_CERTIFICATES: ...]
原因: APK 没有签名。

Failure [INSTALL_CANCELED_BY_USER: ...]
原因: 用户在设备上点击了“取消安装”。常见于在非默认安装器（如游戏中心）中安装时弹出窗口被用户拒绝。

Failure [INSTALL_FAILED_ABORTED: ...]
原因: 安装过程被主动中止。

Failure [INSTALL_FAILED_VERIFICATION_FAILURE: ...]
原因: 验证安装包时失败。

Failure [INSTALL_FAILED_PACKAGE_CHANGED: ...]
原因: 应用包名与预期不符。



2. 权限与用户错误
Error: Unable to open file: ...
原因: ADB 无法读取指定的 APK 文件，路径错误或权限不足。

Error: Permission denied ...
原因: ADB 进程对 APK 文件没有读取权限。

error: device not found
原因: 无设备连接（对应 adb devices 的空列表状态）。

error: device offline
原因: 设备无响应（对应 offline 状态）。

error: device unauthorized.
原因: 设备未授权 USB 调试（对应 unauthorized 状态）。



3. 其他错误
Failed to install ...: "Failure [not installed for 0]"
原因: 一个非常泛泛的错误，通常意味着安装进程因未知原因崩溃。可以尝试增加 -d 参数 (adb install -d ...) 来获取更多细节。

The APK file does not exist on disk
原因: 文件路径错误，Shell 环境（如 Windows CMD 的 %CD%）或脚本中的路径变量未正确展开。
    '''
    show_long_info(title='安装失败故障码解析',info_text=text)
def Uninstall_apps():
    if selected_device is None:
        messagebox.showwarning(title=f'ADBgenius v{version}',message='您还未选中设备！')
    else:
        app_name = simpledialog.askstring(title=f'ADBgenius v{version} - 卸载应用',prompt='请填写包名:\n(可通过“查看所有应用”查询)')
        if app_name:

            text_1 = tk.Label(main_window, foreground='#ffffff', background='#2b2b2b', text='正在卸载中...\n\n请勿断电、断连或执行其他操作!')# 创建一个Label控件，用于显示底部消息栏
            text_1.place(relheight=1, relwidth=1,relx=0,rely=0)
            main_window.update()
            
            a_command = ['adb','-s',str(selected_device)]
            b_command = ['uninstall',app_name]
            for i in range(len(b_command)):
                a_command.append(b_command[i])
            result = subprocess.run(a_command, shell=True, capture_output=True, text=True)
            time.sleep(0.5)
            if 'Success' in result.stdout:
                text_1.destroy()
                messagebox.showinfo(title=f'ADBgenius v{version}',message='成功卸载"' + app_name + '"')
            else:
                text_1.destroy()
                messagebox.showerror(title=f'ADBgenius v{version}',message='卸载失败!\n错误:' + result.stderr)


def show_long_info(title,info_text,file_extension = ''):
    sw = tk.Toplevel()#创建窗口
    sw.title(title)
    #s.iconbitmap('icon.ico')

    screenWidth = main_window.winfo_width()
    screenHeight = main_window.winfo_height()
    width = 800  # 设定窗口宽度
    height = 600  # 设定窗口高度
    left = (screenWidth - width) / 2 + main_window.winfo_x()
    top = (screenHeight - height) / 2 + main_window.winfo_y()

    # 宽度x高度+x偏移+y偏移
    # 在设定宽度和高度的基础上指定窗口相对于屏幕左上角的偏移位置
    sw.geometry("%dx%d+%d+%d" % (width, height, left, top))

    #s.resizable(0,0)#锁定窗口大小
    #s.overrideredirect(True)
    #s.attributes("-topmost", True)#置顶

    inf_texts_lab=tk.Text(sw, width=80, heigh=40, bg='#ffffff', spacing3=1)
    scroll = tk.Scrollbar(sw)


    scroll.place(relheight=0.96,relwidth=0.02,relx=0.98,rely=0.04)
    inf_texts_lab.place(relheight=0.96,relwidth=0.98,x=0,rely=0.04)
    
    scroll.config(command=inf_texts_lab.yview)
    inf_texts_lab.config(yscrollcommand=scroll.set)

    def save_text():
        path = filedialog.asksaveasfilename(
            title='请选择位置',
            filetypes=[('TXT文件', '*.txt'),('所有文件','*')],
            initialdir="./",#初始目录
            initialfile=device_name+file_extension,#初始文件名
            defaultextension='.txt'
            )
        print(path)
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as file:
                    file.write(info_text)
            except Exception as e:
                messagebox.showerror(title=f'ADBgenius v{version}',message=f'错误:\n{e}')
            else:
                messagebox.showinfo(title=f'ADBgenius v{version}',message=f'成功保存到{path}')           
    save_button = tk.Button(sw, text="保存", command=save_text)
    save_button.place(x=0,y=0,relheight=0.04,width=64)

    inf_texts_lab.insert(tk.END, info_text)
    sw.mainloop()



def execute_shortcut_commands(command=[]):
    '''执行指定的 ADB 命令（需已选中设备）。
    返回 subprocess.CompletedProcess 对象：
      - args: 实际执行的命令
      - returncode: 返回码（0=成功，非0=失败）
      - stdout: 标准输出
      - stderr: 错误信息
    '''
    if command:
        if selected_device is None:
            messagebox.showwarning(title=f'ADBgenius v{version}',message='您还未选中设备！')
            return False
        else:
            a_command = ['adb','-s',str(selected_device)]
            for i in range(len(command)):
                a_command.append(command[i])
            try:
                result = subprocess.run(a_command, shell=True, capture_output=True, text=True, encoding='UTF-8', errors='replace')
            except Exception as e:
                result = None
                messagebox.showerror(title=f'ADBgenius v{version}',message=f'执行命令时错误:\n{e}')
            '''if result.returncode != 0:
                result = None'''
            return result



# ---------- helper: safe cat (返回 string 或 None) ----------
def _adb_cat(path):
    """返回指定 path 的内容（去掉尾部换行），若不可读则返回 None"""
    try:
        res = execute_shortcut_commands(['shell','cat', path])
        if res and res.returncode == 0:
            out = res.stdout.strip()
            if out == '' or 'No such file or directory' in out or 'Permission denied' in out:
                return None
            return out
    except Exception:
        pass
    return None

# ---------- helper: adb ls 判断文件存在 ----------
def _adb_exists(path):
    """通过 adb shell test -f/-d 判断文件或目录是否存在"""
    # 若存在返回 True，否则 False
    cmd = ['shell', 'sh', '-c', f"if [ -e {shlex.quote(path)} ]; then echo 1; else echo 0; fi"]
    try:
        res = execute_shortcut_commands(cmd)
        if res and res.returncode == 0:
            return res.stdout.strip() == '1'
    except Exception:
        pass
    return False

# ---------- 主函数：获取 SoC 信息 ----------
def SoC_info():
    """
    返回 dict，字段包括：
      SoC Name, SoC Code, SoC Family, Vendor,
      Device Name, Storage Type, Security Patch,
      ABI, Arch, Core Variant,
      SoC ID, Cores, Core Config, Freq Range,
      CPU Freq-Volt Table, GPU Model, GPU Freq Range, GPU Available Frequencies, GPU Freq-Volt Table
    """
    info = {}

    # ---------- 1) 一次性读取 getprop ----------
    props = {}
    try:
        res = execute_shortcut_commands(['shell','getprop'])
        if res and res.stdout:
            for line in res.stdout.splitlines():
                m = re.match(r'\[(.*?)\]: \[(.*?)\]', line)
                if m: props[m.group(1)] = m.group(2)
    except Exception as e:
        print(f'getprop失败:{e}')
    else:
        print('getprop成功')

    # ---------- 2) 从 getprop 提取核心信息 ----------
    info['SoC Name']       = props.get('ro.config.cpu_info_display', 'N/A')
    '''if not info['SoC Name'] or info['SoC Name'] == 'N/A':
        if len(props.get('ro.product.vendor.device', 'N/A')) > 3:
            info['SoC Name'] = props.get('ro.product.vendor.device', 'N/A')
        elif len(props.get('ro.product.vendor.device', 'N/A')) > 3:
            info['SoC Name'] = props.get('ro.product.vendor.device', 'N/A')'''
    info['SoC Code']       = props.get('ro.soc.model', 'N/A')
    info['SoC Family']     = 'N/A'#props.get('ro.soc.model', 'N/A')#props.get('ro.soc.manufacturer', props.get('ro.boot.baseband', 'N/A'))
    if info['SoC Code'] == 'Kirin' or info['SoC Code'] == 'kirin':#适配海思芯片
        print('麒麟芯片适配启用')
        info['SoC Code']   = props.get('ro.hardware', 'N/A')
        if len(info['SoC Code']) >= 5:
            info['SoC Name']   = '海思麒麟' + props.get('ro.hardware', 'N/A')[5:]
        info['SoC Family'] = 'Kirin'
    
    info['Vendor']         = props.get('ro.product.vendor.manufacturer', 'Unknown')
    if len(info['Vendor']) < 6:#纠正部分高通设备的"qcom"或"vivo" "oppo"等情况
        print('厂商纠正')
        info['Vendor']     = props.get('ro.soc.manufacturer', 'Unknown')
    if info['Vendor'] == 'MediaTek' or info['Vendor'] == 'mediatek':
        info['SoC Code']   = props.get('ro.hardware', 'N/A')
    
    info['Device Name']    = props.get('ro.config.marketing_name', props.get('ro.product.model', 'N/A'))
    info['Storage Type']   = props.get('ro.boot.bootdevice', 'N/A')
    info['Security Patch'] = props.get('ro.build.version.security_patch', 'N/A')
    info['ABI']            = props.get('ro.product.cpu.abi', 'N/A')
    info['Arch']           = execute_shortcut_commands(['shell','uname','-m']).stdout.strip() if execute_shortcut_commands(['shell','uname','-m']) else 'N/A'
    info['Core Variant']   = props.get('dalvik.vm.isa.arm64.variant', props.get('dalvik.vm.isa.arm.variant', 'N/A'))
    
    # ---------- 3) soc0 补充 ----------
    if not info['SoC Family'] or info['SoC Family'] == 'N/A':
        print('Prop获取family失败，更换为其他方式')
        info['SoC Family'] = _adb_cat('/sys/devices/soc0/family') or _adb_cat('/sys/devices/system/soc/family') or 'N/A'

    if 'Snapdragon' in info['SoC Family'] or 'snapdragon' in info['SoC Family']:#纠正厂商错误（nova 9）
        info['Vendor'] = 'Qualcomm'
        print('修正厂商错误：Qualcomm')
    if 'Kirin' in info['SoC Family'] or 'kirin' in info['SoC Family']:#纠正厂商错误（nova 8）
        info['Vendor'] = 'Hisilicon'
        print('修正厂商错误：Hisilicon')

    soc_id     = _adb_cat('/sys/devices/soc0/soc_id') or _adb_cat('/sys/devices/system/soc/soc_id')
    '''if soc_family: info['SoC Family'] = soc_family'''
    info['SoC ID'] = soc_id or 'N/A'

    # ---------- 4) /proc/cpuinfo 补充 ----------
    raw_cpuinfo = ''
    try:
        res = execute_shortcut_commands(['shell','cat','/proc/cpuinfo'])
        raw_cpuinfo = res.stdout if res and res.stdout else ''
    except: pass
    if not info['SoC Name'] or info['SoC Name'] == 'N/A':
        for line in (raw_cpuinfo or '').splitlines():
            if "Hardware\t: " in line:
                info['SoC Name'] = line.split(': ')[1]
                break

    # ---------- 5) CPU 核心数量 & 频率 ----------
    cpu_count = None
    try:
        r = execute_shortcut_commands(['shell','nproc'])
        cpu_count = int(r.stdout.strip()) if r and r.stdout.strip().isdigit() else None
    except: pass
    if cpu_count is None:
        cpu_count = len([l for l in (raw_cpuinfo or '').splitlines() if l.startswith('processor')])
    info['Cores'] = cpu_count

    per_core_max, per_core_min, freq_vals = {}, {}, []
    for i in range(cpu_count):
        maxf = _adb_cat(f'/sys/devices/system/cpu/cpu{i}/cpufreq/cpuinfo_max_freq')
        minf = _adb_cat(f'/sys/devices/system/cpu/cpu{i}/cpufreq/cpuinfo_min_freq')
        if maxf and maxf.isdigit():
            ghz = int(maxf) / 1e6
            per_core_max[i] = ghz
            freq_vals.append(ghz)
        if minf and minf.isdigit():
            per_core_min[i] = int(minf) / 1e6

    cluster_summary = {}
    for v in per_core_max.values():
        cluster_summary[v] = cluster_summary.get(v, 0) + 1
    if cluster_summary:
        parts = [f"{count}*{freq:.2f}GHz" for freq, count in sorted(cluster_summary.items(), reverse=True)]
        info['Core Config'] = f"{cpu_count} cores ({'+'.join(parts)})"
    else:
        info['Core Config'] = f"{cpu_count} cores (N/A)"
    info['Freq Range'] = f"{min(freq_vals):.2f}GHz - {max(freq_vals):.2f}GHz" if freq_vals else 'N/A'

    # ---------- 6) CPU Freq-Volt 表 ----------
    # (保留你之前的逻辑)
    cpu_opp_table = []
    for p in [
        '/sys/devices/system/cpu/cpu0/cpufreq/opp_table',
        '/sys/devices/system/cpu/cpu0/cpufreq/opp_tables',
        '/sys/devices/system/cpu/cpu0/cpufreq/operating_points',
        '/sys/devices/system/cpu/opp_table',
    ]:
        dump = _adb_cat(p)
        if dump:
            for line in dump.splitlines():
                m = re.findall(r'(\d+)\D+(\d+)', line)
                for a,b in m:
                    try:
                        fghz = int(a)/1e6
                        v = int(b)/1e6
                        cpu_opp_table.append(f"{fghz:.2f}GHz @ {v:.3f}V")
                    except: pass
            if cpu_opp_table: break
    info['CPU Freq-Volt Table'] = cpu_opp_table if cpu_opp_table else ['N/A']

    # ------------- 6) GPU 探测：model + freq + available_frequencies + gpu opp -------------
    gpu_model = None
    gpu_vendor = None
    openGL_version = None
    gpu_freqs = []
    gpu_freq_range = "N/A"
    gpu_opp_table = []

    gles_info = execute_shortcut_commands(['shell','dumpsys SurfaceFlinger | grep -i "GLES:"']).stdout[6:].replace('\n', '').split(', ')
    #print(execute_shortcut_commands(['shell','dumpsys SurfaceFlinger | grep -i "GLES:"']))
    #GLES: Qualcomm, Adreno (TM) 730, OpenGL ES 3.2 V@0615.60 (GIT@16c1863, I6928db2619, 1674201211) (Date:01/19/23)
    if gles_info and len(gles_info) >= 3:
        gpu_vendor = gles_info[0]
        gpu_model = gles_info[1]
        openGL_version = ', '.join(gles_info[2:])
    
    info['GPU Vendor'] = gpu_vendor or 'N/A'
    info['GPU OpenGL version'] = openGL_version or 'N/A'
    info['GPU Model'] = gpu_model or 'N/A'
    '''# 插入到 info
    info['GPU Model'] = gpu_model or 'N/A'
    # 常见：Qualcomm KGSL 路径（Adreno） - /sys/class/kgsl/kgsl-3d0/gpu_model 等。:contentReference[oaicite:4]{index=4}
    kgsl_model = _adb_cat('/sys/class/kgsl/kgsl-3d0/gpu_model') or _adb_cat('/sys/class/kgsl/kgsl-3d0/gpu')
    if kgsl_model:
        gpu_model = kgsl_model.strip()'''

    # 常见 devfreq 可用频率（适用于 Mali / GPU devfreq 节点 等）：
    # /sys/class/devfreq/<name>/available_frequencies
    # /sys/class/devfreq/<name>/cur_freq  /max_freq /min_freq  （内核 devfreq 文档）:contentReference[oaicite:5]{index=5}
    # 先列出 devfreq 下的项（通过 adb shell ls）
    try:
        res_ls = execute_shortcut_commands(['shell','ls','/sys/class/devfreq']).stdout
    except Exception:
        res_ls = ''
    devfreq_entries = []
    if res_ls:
        devfreq_entries = [x for x in res_ls.split() if x]
    # 尝试匹配包含 gpu / kgsl / mali 的 devfreq entry
    for e in devfreq_entries:
        if any(k in e.lower() for k in ('gpu','kgsl','mali','gmu','adreno')):
            base = f'/sys/class/devfreq/{e}'
            av = _adb_cat(base + '/available_frequencies') or _adb_cat(base + '/available_frequencies_list')
            cur = _adb_cat(base + '/cur_freq')
            mn = _adb_cat(base + '/min_freq') or _adb_cat(base + '/lower_freq')
            mx = _adb_cat(base + '/max_freq') or _adb_cat(base + '/upper_freq')
            if av:
                # available_frequencies 常为空格分隔的 Hz 数字
                freqs = []
                for token in re.split(r'\s+', av.strip()):
                    if token.isdigit():
                        freqs.append(int(token)/1e6)  # -> MHz->GHz
                freqs = sorted(set(freqs))
                gpu_freqs = [f"{f/1000:.2f}GHz" if f>1000 else f"{f:.0f}MHz" for f in freqs] if freqs else gpu_freqs
            else:
                # 也许 cur/max/min 可用
                tries = []
                for val in (mn, mx, cur):
                    if val and val.isdigit():
                        tries.append(int(val)/1e6)
                if tries:
                    gpu_freqs = [f"{min(tries)/1000:.2f}GHz", f"{max(tries)/1000:.2f}GHz"] if max(tries) > 1000 else [f"{min(tries):.0f}MHz", f"{max(tries):.0f}MHz"]
            '''# 若找到 model 但未设置 model 字段，可以尝试读取 name 文件
            if not gpu_model:
                candidate_name = _adb_cat(base + '/name')
                if candidate_name:
                    gpu_model = candidate_name.strip()'''
            # 如果找到了任何 freq info，则以此为准（优先第一个匹配项）
            if gpu_freqs:
                break

    # 另外常见的 GPU 频率路径：Qualcomm 设备有 /sys/class/kgsl/kgsl-3d0/gpuclk 及 cur_freq 等
    if not gpu_freqs:
        kgsl_cur = _adb_cat('/sys/class/kgsl/kgsl-3d0/gpuclk') or _adb_cat('/sys/class/kgsl/kgsl-3d0/gpuclk_freq')
        kgsl_cur2 = _adb_cat('/sys/class/kgsl/kgsl-3d0/cur_freq')
        kgsl_available = _adb_cat('/sys/class/kgsl/kgsl-3d0/available_frequencies')
        if kgsl_available:
            freqs = [int(x)/1e6 for x in re.split(r'\s+', kgsl_available.strip()) if x.isdigit()]
            freqs = sorted(set(freqs))
            gpu_freqs = [f"{f/1000:.2f}GHz" if f>1000 else f"{f:.0f}MHz" for f in freqs]
        elif kgsl_cur or kgsl_cur2:
            # 只读到 cur_freq，仍然能填入范围为 cur
            try:
                curv = int((kgsl_cur or kgsl_cur2).strip())/1e6
                gpu_freqs = [f"{curv/1000:.2f}GHz"]
            except:
                pass

    '''# GPU model 其他尝试（Mali 等）：/sys/devices/platform/*mali*/driver/name 或 /sys/devices/platform/*mali*/devfreq/*/name
    if not gpu_model:
        # 尝试几种常见的 mali 路径
        for pat in ['/sys/devices/platform','/sys/devices']:
            try:
                res_find = execute_shortcut_commands(['shell', 'sh', '-c', f"ls -d {pat}/*mali* 2>/dev/null | head -n 1"])
                if res_find and res_find.stdout.strip():
                    candidate = res_find.stdout.strip()
                    # 尝试读取 device 的 name 或 driver/name 或 /devfreq 下的 name
                    nm = _adb_cat(candidate + '/driver/name') or _adb_cat(candidate + '/name') or _adb_cat(candidate + '/devfreq/*/name')
                    if nm:
                        gpu_model = nm.strip()
                        break
            except Exception:
                pass'''

    
    info['GPU Available Frequencies'] = gpu_freqs or ['N/A']
    # 构造 GPU 频率范围字符串
    try:
        # 从 gpu_freqs 解析数字（单位可能是 GHz 或 MHz 字符串）
        nums = []
        for s in gpu_freqs:
            if isinstance(s, str):
                m = re.search(r'([\d\.]+)\s*GHz', s)
                if m:
                    nums.append(float(m.group(1)))
                else:
                    m2 = re.search(r'(\d+)\s*MHz', s)
                    if m2:
                        nums.append(int(m2.group(1))/1000.0)
        if nums:
            gpu_freq_range = f"{min(nums):.2f}GHz - {max(nums):.2f}GHz"
    except Exception:
        gpu_freq_range = "N/A"
    info['GPU Freq Range'] = gpu_freq_range

    # GPU OPP 尝试（常见位置）
    gpu_opp_paths = [
        '/sys/devices/platform/*gpu*/opp_table',
        '/sys/devices/platform/*mali*/opp_table',
        '/sys/devices/platform/*kgsl*/opp_table',
        '/sys/devices/platform/*gmu*/opp_table',
        '/sys/devices/platform/opp-table/opp_table',
        '/sys/class/devfreq/*/opp_table',
    ]
    for pat in gpu_opp_paths:
        # 对通配符使用 shell glob
        try:
            res_glob = execute_shortcut_commands(['shell','sh','-c', f'for p in {pat}; do if [ -e "$p" ]; then echo "$p"; fi; done | head -n 1'])
            if res_glob and res_glob.stdout.strip():
                path_found = res_glob.stdout.strip()
                dump = _adb_cat(path_found)
                if dump:
                    for line in dump.splitlines():
                        m = re.findall(r'(\d+)\D+(\d+)', line)
                        for a,b in m:
                            try:
                                fghz = int(a) / 1e6
                                vuv = int(b)
                                # convert uV -> V
                                v = vuv / 1e6
                                gpu_opp_table.append(f"{fghz/1000:.2f}GHz @ {v:.3f}V")
                            except:
                                pass
                    if gpu_opp_table:
                        break
        except Exception:
            pass

    info['GPU Freq-Volt Table'] = gpu_opp_table if gpu_opp_table else ['N/A']

    # ------------- 7) 最终返回 -------------
    return info



def RAM_info():
    raw_info = execute_shortcut_commands(command=['shell','cat','/proc/meminfo']).stdout
    info = raw_info.splitlines()
    '''print(info[0],info[2])
    print(info[0].split(' '))'''
    mem_totall = int(info[0].split(' ')[len(info[0].split(' '))-2])/1024#单位为MB
    mem_free = int(info[2].split(' ')[len(info[2].split(' '))-2])/1024
    return [mem_totall,mem_free]

def screen_info():
    screen_pixiv = execute_shortcut_commands(command=['shell','wm','size']).stdout.replace('\n', '\n |')
    screen_density = execute_shortcut_commands(command=['shell','wm','density']).stdout.replace('\n', '\n |')
    return (' |分辨率:' + screen_pixiv + '像素密度DPI:' + screen_density + '\n')

def battery_info():
    Battery_info = execute_shortcut_commands(['shell','dumpsys','battery']).stdout
    if not Battery_info:
        return " | 无电池信息 (dumpsys 没有返回)\n"
    info = {}
    for line in Battery_info.splitlines():
        if ':' in line:
            k,v = line.split(':',1)
            info[k.strip()] = v.strip()
    # 常见字段
    level = info.get('level','N/A')
    scale = info.get('scale','100')
    try:
        percent = f"{int(level)}/{int(scale)}"
    except:
        percent = f"{level}/{scale}"
    voltage = info.get('voltage','N/A')
    temp = info.get('temperature','N/A')
    status = info.get('status','N/A')
    health = info.get('health','N/A')
    ac = info.get('AC powered','false')
    usb = info.get('USB powered','false')
    wireless = info.get('Wireless powered','false')

    # 处理温度显示（Android dumpsys 通常为 1/10 °C 单位）
    temp_display = temp
    try:
        ti = int(temp)
        temp_display = f"{ti/10:.1f}°C ({ti})"
    except:
        pass

    return f""" | 电量: {percent}
 | 电压: {voltage} mV
 | 温度: {temp_display}
 | 状态: {status}
 | 健康: {health}
 | 供电: AC={ac}, USB={usb}, 无线={wireless}
"""

def flash_info():
    """返回闪存（内部存储）容量 + 空闲 + 存储接口类型等信息"""
    info = {}

    # 1) 先从 getprop 拿存储接口或 bootdevice
    props = {}
    try:
        res = execute_shortcut_commands(['shell','getprop'])
        if res and res.stdout:
            for line in res.stdout.splitlines():
                m = re.match(r'\[(.*?)\]: \[(.*?)\]', line)
                if m:
                    props[m.group(1)] = m.group(2)
    except:
        pass

    # 存储接口类型
    storage_interface = props.get('ro.boot.bootdevice', None)
    # "bootdevice" 通常像 “soc/1d84000.ufshc” 或者 “ufshc”
    if storage_interface:
        info['Interface'] = storage_interface.strip()
    else:
        # fallback: 从 sysfs 或卡 /dev/block/XXX 类型判断
        # 可尝试 /sys/block/mmc0/device/type 或类似
        si = _adb_cat('/sys/block/mmc0/device/type')
        if si:
            info['Interface'] = si.strip()
        else:
            info['Interface'] = 'N/A'

    # 2) 总空间 / 空闲空间
    '''try:'''
        # 用 df -h 更好读, 取 /data 或 /storage
    res2 = execute_shortcut_commands(['shell','df','/data'])
    print(res2)
    if res2 and res2.stdout:
        # df 输出如：
        # Filesystem      Size  Used Avail Use% Mounted on
        # /dev/block/xxx  50G   20G   30G  40% /data
        lines = res2.stdout.splitlines()
        # 找挂载 /data 的那行
        for line in lines:
            print(line)
            if 'storage' in line or line.endswith('/data') or '/0' in line:
                print(line)
                parts = re.split(r'\s+', line)
                # parts 1 = Filesystem, 2 = Size, 3 = Used, 4 = Avail
                print(f'匹配字符段:{parts}')
                if len(parts) >= 5:
                    info['Size'] = parts[1]
                    info['Used'] = parts[2]
                    info['Free'] = parts[3]
                print(f'闪存:{info}')
                break
        if 'Size' in info and (info['Size'].endswith('KB') or info['Size'].endswith('kb') or info['Size'].isdigit()):
            if not re.search(r'[a-zA-Z]$', info['Size']):
                info['Size'] = str(round(int(info['Size']) / 1024 / 1024, 2)) + 'GB'
                info['Used'] = str(round(int(info['Used']) / 1024 / 1024, 2)) + 'GB'
                info['Free'] = str(round(int(info['Free']) / 1024 / 1024, 2)) + 'GB'
            elif info['Size'].endswith('KB') or info['Size'].endswith('kb'):
                info['Size'] = str(round(int(info['Size'][:2]) / 1024 / 1024, 2)) + 'GB'
                info['Used'] = str(round(int(info['Used'][:2]) / 1024 / 1024, 2)) + 'GB'
                info['Free'] = str(round(int(info['Free'][:2]) / 1024 / 1024, 2)) + 'GB'
            elif info['Size'].isdigit():
                info['Size'] = str(round(int(info['Size'][:2]) / 1024 / 1024, 2)) + 'GB'
                info['Used'] = str(round(int(info['Used'][:2]) / 1024 / 1024, 2)) + 'GB'
                info['Free'] = str(round(int(info['Free'][:2]) / 1024 / 1024, 2)) + 'GB'
    '''except Exception as e:
        print('flash info:',e)'''

    # 3) 返回格式化文本或 dict
    # 这里返回可供 devices_info 拼接的 dict /字符串
    # 我建议返回一个 dict
    return info


def devices_info():
    if selected_device is None:
        messagebox.showwarning(title=f'ADBgenius v{version}',message='您还未选中设备！')
    else:
        text_1 = tk.Label(main_window, foreground='#ffffff', background='#2b2b2b', text='正在查询中中...\n预计在10秒内完成，请耐心等候！')
        text_1.place(relheight=1, relwidth=1,relx=0,rely=0)
        main_window.update()
        '''try:'''
        model = execute_shortcut_commands(['shell','getprop','ro.product.model']).stdout.strip()
        android_version = execute_shortcut_commands(['shell','getprop','ro.build.version.release']).stdout.strip()
        MAC_path = execute_shortcut_commands(['shell','cat','/sys/class/net/wlan0/address']).stdout.strip()
        Manufactuer = execute_shortcut_commands(['shell','getprop','ro.product.manufacturer']).stdout.strip()
        #Battery_info_raw = execute_shortcut_commands(['shell','dumpsys','battery']).stdout
        sim_operator_info = execute_shortcut_commands(['shell','getprop','gsm.sim.operator.alpha']).stdout.strip()
        network_type = execute_shortcut_commands(['shell','getprop','gsm.network.type']).stdout.strip()

        ram = RAM_info()
        # flash 是 dict
        flash = flash_info()
        flash_text = f" | 存储接口: {flash.get('Interface','N/A')}\n"
        if 'Size' in flash:
            flash_text += f" | 总容量: {flash.get('Size')}，已用: {flash.get('Used')}，可用: {flash.get('Free')}\n"
        else:
            flash_text += " | 无法读取存储容量信息\n"
        screen = screen_info()
        prop_info = SoC_info()  # 我们的新函数，返回 dict
        '''except Exception as e:
            messagebox.showerror(title=f'ADBgenius v{version}',message=f'错误:\n{e}')
            return'''
        '''else:'''
            # 格式化 CPU/SoC/GPU 信息
        cpu_text_lines = []
        cpu_text_lines.append("处理器(SoC):")
        cpu_text_lines.append(f" | 名称: {prop_info.get('SoC Name','N/A')}")
        cpu_text_lines.append(f" | 家族: {prop_info.get('SoC Family','N/A')}")
        cpu_text_lines.append(f" | 厂商: {prop_info.get('Vendor','N/A')}")
        cpu_text_lines.append(f" | 代号: {prop_info.get('SoC Code','N/A')}")
        cpu_text_lines.append(f" | ID: {prop_info.get('SoC ID','N/A')}")
        cpu_text_lines.append(f" | 架构/ABI: {prop_info.get('Arch','N/A')} / {prop_info.get('ABI','N/A')}")
        cpu_text_lines.append(f" | 核心配置: {prop_info.get('Core Config','N/A')}(结果可能有偏差，仅供参考)")
        cpu_text_lines.append(f" | 频率范围: {prop_info.get('Freq Range','N/A')}")
        # CPU Freq-Volt
        cpu_text_lines.append(" | CPU 频率-电压表:")
        for row in prop_info.get('CPU Freq-Volt Table', ['N/A']):
            cpu_text_lines.append(f"   - {row}")

        # GPU 部分
        cpu_text_lines.append(" | GPU 型号: " + prop_info.get('GPU Model','N/A'))
        cpu_text_lines.append(" | GPU 厂商: " + prop_info.get('GPU Vendor','N/A'))
        cpu_text_lines.append(" | OpenGL 版本: " + prop_info.get('GPU OpenGL version','N/A'))
        cpu_text_lines.append(" | GPU 频率范围: " + prop_info.get('GPU Freq Range','N/A'))
        cpu_text_lines.append(" | GPU 可用频率:")
        for row in prop_info.get('GPU Available Frequencies', ['N/A']):
            cpu_text_lines.append(f"   - {row}")
        cpu_text_lines.append(" | GPU 频率-电压表:")
        for row in prop_info.get('GPU Freq-Volt Table', ['N/A']):
            cpu_text_lines.append(f"   - {row}")

        cpu_text = '\n'.join(cpu_text_lines)

        # 格式化电池
        battery_text = battery_info()

        info_text = f'''设备信息摘要(v3)：
型号: {model}
名称: {prop_info.get('Device Name','N/A')}
厂商: {Manufactuer}
安卓版本: {android_version}

内存:
 | 总内存: {ram[0]} MB
 | 空闲内存: {ram[1]} MB

闪存:
{flash_text}

屏幕:
{screen}

网络:
 | 运营商: {sim_operator_info}
 | 网络类型: {network_type}
 | MAC地址: {MAC_path}

电池:
{battery_text}

{cpu_text}
'''
        text_1.destroy()
        show_long_info(title='设备信息',info_text=info_text,file_extension='设备信息v3')

    

def all_app_inf():
    if selected_device is None:
        messagebox.showwarning(title=f'ADBgenius v{version}',message='您还未选中设备！')
    else:
        a_command = ['adb','-s',str(selected_device)]
        b_command = ['shell','pm','list','packages']
        for i in range(len(b_command)):
            a_command.append(b_command[i])
        result = subprocess.run(a_command, shell=True, capture_output=True, text=True)
        show_long_info('查看所有应用',result.stdout,file_extension='所有应用包名')

def screen_projection():#投屏系统
    if selected_device:
        subprocess.run(['start',f'{root_path}\lib\scrcpy\scrcpy.exe','-s',selected_device], shell=True, capture_output=True, text=True)
    else:
        messagebox.showwarning(title=f'ADBgenius v{version}',message='您还未选中设备！')

def home_c():
    execute_adb_basic_command('home')
def back_c():
    execute_adb_basic_command('back')
def multitask_c():
    execute_adb_basic_command('multitask')
def power_c():
    execute_adb_basic_command('power')
    
def execute_adb_basic_command(basic_command):
    a_command = ['adb','-s',str(selected_device)]
    if basic_command == 'back':
        b_command = ['shell','input','keyevent','4']
    if basic_command == 'home':
        b_command = ['shell','input','keyevent','3']
    if basic_command == 'multitask':#多任务
        b_command = ['shell','input','keyevent','187']
    if basic_command == 'power':#电源
        b_command = ['shell','input','keyevent','26']
    for i in range(len(b_command)):
        a_command.append(b_command[i])
    result = subprocess.run(a_command, shell=True, capture_output=True, text=True)
    print(basic_command)
    print(result)

def refresh_devices():
    update_device_listbox_once()

def feedback():#反馈
    if messagebox.askokcancel("反馈",'可以在Bilibili私信我(Bilibili@O-TREE 建议选择此方式)\n或者反馈至邮箱(很少看，不建议):\ocr_8@qq.com\n(确认即复制邮箱至剪贴板)'):
        #main_window.clipboard_clear()
        main_window.clipboard_append("ocr_8@qq.com")
def patron():#赞助
    patron_window = tk.Toplevel()#创建窗口
    patron_window.configure(bg='#1e1e1e')
    #patron_window.iconbitmap(icon_file)
    patron_window.geometry('520x340+550+350')
    patron_window.resizable(0,0)#锁定窗口大小
    patron_window.attributes("-toolwindow", True)#改成工具样式（工具栏只有关闭键）
    patron_window.attributes("-topmost", True)#置顶

    def jump_to_aifadian():
        webbrowser.open("https://ifdian.net/a/OTREE")
        patron_window.destroy()
    
    slabel = tk.Label(patron_window,justify='left' , text='创作不易，十分感谢！\n更多内容欢迎关注\nBilibili@O-TREE',font=('Microsoft YaHei',12),bg='#1e1e1e', foreground='#ffffff').place(relheight=0.2, relwidth=0.35,relx=0.04,rely=0.03)
    slabel = tk.Label(patron_window,justify='left' , text='金额随意，感谢支持！\n\n   支付宝         微信',font=('Microsoft YaHei',12),bg='#1e1e1e', foreground='#ffffff').place(relheight=0.2, relwidth=0.35,relx=0.04,rely=0.29)
    slabel = tk.Label(patron_window,image=photo_sw,bg='lightgray',borderwidth=0).place(relx=0.45,rely=0.04)
    slabel = tk.Label(patron_window,image=photo_pay,bg='lightgray',borderwidth=0).place(relx=0.05,rely=0.5)
    Jump_to_WEB_button=tk.Button(patron_window,command=jump_to_aifadian,text="(oﾟ▽ﾟ)o 跳转至爱发电 (〃'▽'〃)",font=('微软雅黑',12), activebackground='#1177bb', activeforeground='#ffffff', foreground='#ffffff',background='#0e639c',borderwidth=0)
    Jump_to_WEB_button.place(height=30, relwidth=0.54,relx=0.05,y=290)
    Jump_to_WEB_button.bind('<Enter>', lambda event: Jump_to_WEB_button.config(bg='#1177bb'))
    Jump_to_WEB_button.bind('<Leave>', lambda event: Jump_to_WEB_button.config(bg='#0e639c'))

    RET_button=tk.Button(patron_window,command=patron_window.destroy,text='返回',font=('微软雅黑',11), activebackground='#1177bb', activeforeground='#ffffff', foreground='#ffffff',background='#0e639c',borderwidth=0)
    RET_button.place(height=30, relwidth=0.34,relx=0.61,y=290)
    RET_button.bind('<Enter>', lambda event: RET_button.config(bg='#1177bb'))
    RET_button.bind('<Leave>', lambda event: RET_button.config(bg='#0e639c'))


        
    patron_window.mainloop()

def about_ADBG():#关于
    about_window = tk.Toplevel()#创建窗口
    about_window.configure(bg='#1e1e1e')
    #about_window.iconbitmap(icon_file)
    about_window.geometry('450x300+550+350')
    about_window.resizable(0,0)#锁定窗口大小
    about_window.attributes("-toolwindow", True)#改成工具样式（工具栏只有关闭键）
    about_window.attributes("-topmost", True)#置顶

    def jump_to_bilibili(a):
        webbrowser.open("https://space.bilibili.com/668497683/")
    def jump_to_ycts(a):
        webbrowser.open("https://www.ycts.top")
    def jump_to_gen(a):
        webbrowser.open("https://github.com/Genymobile/scrcpy")
    
    title_font = tkFont.Font(family="微软雅黑",size=20,weight=tkFont.BOLD)
    ycts_link_font = tkFont.Font(family="微软雅黑",size=8,underline=1,slant=tkFont.ITALIC)
    link_font = tkFont.Font(family="微软雅黑",size=10,underline=1,slant=tkFont.ITALIC)

    slabel = tk.Label(about_window,justify='left' , text='ADB genius',font=title_font,bg='#1e1e1e', foreground='#cfcfcf').place(relheight=0.15, relwidth=1,relx=0,rely=0.03)
    slabel = tk.Label(about_window,justify='left' , text='By OTREE',font=('微软雅黑',11),bg='#1e1e1e', foreground='#8f8f8f').place(relheight=0.08, relwidth=1,relx=0,rely=0.17)
    separate4 = tk.Label(about_window,background='#3c3c3c', fg='#b2b2b2')#分隔
    separate4.place(x=25,y=80,height=2,width=400)


    slabel = tk.Label(about_window,justify='left', text=f'作者：',font=('微软雅黑',11),bg='#1e1e1e', foreground='#bfbfbf',anchor="w").place(height=18, width=65,x=30,y=85)
    OTREE_link_slabel = tk.Label(about_window,justify='left' , text=f'Bilibili@O-TREE',font=link_font,bg='#1e1e1e', foreground='#bfbfbf',anchor="w")
    OTREE_link_slabel.place(height=18, relwidth=0.3,x=75,y=85)
    OTREE_link_slabel.bind("<Button-1>",jump_to_bilibili)#超链接

    slabel = tk.Label(about_window,justify='left', text=f'版本：{version}',font=('微软雅黑',11),bg='#1e1e1e', foreground='#bfbfbf',anchor="w").place(height=18, width=100,x=30,y=110)


    slabel = tk.Label(about_window,justify='left', text=f'鸣谢：Genymobile',font=('微软雅黑',11),bg='#1e1e1e', foreground='#bfbfbf',anchor="w").place(height=18, width=100,x=225,y=85)
    slabel = tk.Label(about_window,justify='left', text=f'引用项目：',font=('微软雅黑',11),bg='#1e1e1e', foreground='#bfbfbf',anchor="w").place(height=18, width=85,x=225,y=110)
    scp_link_slabel = tk.Label(about_window,justify='left' , text=f'Genymobile/scrcpy',font=link_font,bg='#1e1e1e', foreground='#bfbfbf',anchor="w")
    scp_link_slabel.place(height=18, relwidth=0.3,x=300,y=110)
    scp_link_slabel.bind("<Button-1>",jump_to_gen)#超链接

    super_font1 = tkFont.Font(family="微软雅黑",size=14,slant=tkFont.ITALIC,weight=tkFont.BOLD)
    super_font2 = tkFont.Font(family="微软雅黑",size=11,slant=tkFont.ITALIC,weight=tkFont.BOLD)
    slabel = tk.Label(about_window,justify='left', text=f'技术宅照亮世界',font=super_font1,bg='#353535', foreground='#afafaf').place(height=30, relwidth=1,relx=0,y=145)
    slabel = tk.Label(about_window,justify='left', text=f'TECH OTAKUS ILLUMINATE THE WORLD',font=super_font2,bg='#3e3e3e', foreground='#afafaf').place(height=25, relwidth=1,relx=0,y=175)

    slabel = tk.Label(about_window,justify='left', text=f'未经许可 严禁商用 禁止用于非法用途！',font=('微软雅黑',8),bg='#1e1e1e', foreground='#bfbfbf',anchor="w").place(height=10, width=200,x=245,y=283)
    
    slabel = tk.Label(about_window,image=ycts_logo_img,bg='#1e1e1e',borderwidth=0).place(relx=0.04,rely=0.75)
    ycts_link_slabel = tk.Label(about_window,justify='left' , text='www.ycts.top',font=ycts_link_font,bg='#1e1e1e', foreground='#7580f2')
    ycts_link_slabel.place(height=12, relwidth=0.2,relx=0.14,rely=0.895)
    ycts_link_slabel.bind("<Button-1>",jump_to_ycts)#超链接

    RET_button=tk.Button(about_window,command=about_window.destroy,text='返回',font=('微软雅黑',12), activebackground='#1177bb', activeforeground='#ffffff', foreground='#ffffff',background='#0e639c',borderwidth=0)
    RET_button.place(height=40, relwidth=0.54,relx=0.41,y=235)
    RET_button.bind('<Enter>', lambda event: RET_button.config(bg='#1177bb'))
    RET_button.bind('<Leave>', lambda event: RET_button.config(bg='#0e639c'))

    about_window.mainloop()

def temp_Monitor_tool():
    speed = 2
    size = 11
    window_size = [300,60]#以列表形式存储窗口大小数据
    #UI_number = 1

    # ---- 保留你原来的 CPU/RAM 初始化风格（不过 CPU 部分将复用为 thermal 显示） ----
    #cpulist = psutil.cpu_percent(interval=1, percpu=True)
    #core_num = len(cpulist)#获取核心数量

    def main():
        global cpu_text
        nonlocal num
        if selected_device == None:
            messagebox.showwarning(title=f'ADBgenius v{version}',message='您还未选中设备！')
            return
        #global UI_number
        temp_monitor_window=tk.Tk()
        #设定界面相关参数
        temp_monitor_window.title('ADB Health Monitor')
        temp_monitor_window.columnconfigure(0,minsize=50)
        temp_monitor_window.configure(bg='#1e1e1e')
        temp_monitor_window.geometry(f'{window_size[0]}x60+50+30')
        #temp_monitor_window.resizable(0,0)
        temp_monitor_window.overrideredirect(True)
        temp_monitor_window.attributes("-topmost", True)

        # 字符变量初始化区（保留原名）
        cpu_text = tk.StringVar()
        cpu_text.set('CPU:--.-%')   # 这个文本我们可以不再频繁更新（保留以防兼容）
        ram_usage = tk.StringVar()
        ram_usage.set('RAM: --.-%')

        # ======================== 将“每核显示”替换为“thermal_zone 显示” =========================
        # 设计目标：最小改动 UI，复用 create_widgets / updata_labels 的结构
        def _adb_run(cmd_list, timeout=3):
            """简洁的 adb wrapper，返回 (stdout, stderr) 元组；捕获常见异常。"""
            try:
                p = subprocess.run(cmd_list, capture_output=True, text=True, timeout=timeout)
                return p.stdout or "", p.stderr or ""
            except subprocess.TimeoutExpired:
                return "", "adb timeout"
            except FileNotFoundError:
                return "", "adb not found"
            except Exception as e:
                return "", str(e)

        def fetch_android_cpu_usage():
            """
            通过读取 /proc/stat 两次计算 Android 设备总体 CPU 占用百分比。
            返回 float（0..100）或 None（失败）。
            """
            # 第一次采样
            out1, err1 = _adb_run(['adb', '-s', str(selected_device), 'shell', 'su', '-c', "cat /proc/stat | head -n 1"], timeout=2)
            if err1:
                return None
            #time.sleep(speed)
            out2, err2 = _adb_run(['adb', '-s', str(selected_device), 'shell', 'su', '-c', "cat /proc/stat | head -n 1"], timeout=2)
            if err2:
                return None

            def parse_cpu_line(line):
                parts = line.strip().split()
                if len(parts) < 5:
                    return None
                # parts[0] == 'cpu'
                vals = [int(x) for x in parts[1:]]
                # idle = idle + iowait (tokens index 3 and 4 after 'cpu')
                idle = vals[3] + (vals[4] if len(vals) > 4 else 0)
                total = sum(vals)
                return idle, total

            p1 = parse_cpu_line(out1)
            p2 = parse_cpu_line(out2)
            if not p1 or not p2:
                return None
            idle1, total1 = p1
            idle2, total2 = p2
            diff_idle = idle2 - idle1
            diff_total = total2 - total1
            if diff_total <= 0:
                return None
            usage = (1.0 - (diff_idle / diff_total)) * 100.0
            return round(max(0.0, min(100.0, usage)), 1)

        def fetch_android_ram_usage():
            """
            读取 Android /proc/meminfo，返回使用百分比或 None。
            使用 MemTotal 与 MemAvailable（若无 Available 则退回于计算方式）。
            """
            out, err = _adb_run(['adb', '-s', str(selected_device), 'shell', 'su', '-c', "cat /proc/meminfo"], timeout=3)
            if err or not out:
                return None
            total = None
            avail = None
            for line in out.splitlines():
                if line.startswith('MemTotal:'):
                    try:
                        total = int(line.split()[1])  # kB
                    except:
                        total = None
                elif line.startswith('MemAvailable:'):
                    try:
                        avail = int(line.split()[1])  # kB
                    except:
                        avail = None
                if total and avail:
                    break
            if total is None:
                return None
            if avail is None:
                # 尝试用 MemFree+Buffers+Cached 作为退路
                memfree = buffers = cached = 0
                for line in out.splitlines():
                    if line.startswith('MemFree:'):
                        try: memfree = int(line.split()[1])
                        except: pass
                    elif line.startswith('Buffers:'):
                        try: buffers = int(line.split()[1])
                        except: pass
                    elif line.startswith('Cached:'):
                        try: cached = int(line.split()[1])
                        except: pass
                avail = memfree + buffers + cached
                if not avail:
                    return None
            used = total - avail
            pct = used / total * 100.0
            return round(max(0.0, min(100.0, pct)), 1)

        def temp_to_color(temp_c):
            """
            分段渐变颜色映射:
            <=30 蓝青
            30-45 青蓝->绿
            45-60 绿->黄
            60-80 黄->橙
            >=80 红
            """
            if temp_c is None:
                return '#a4a4a4'  # 无数据 -> 灰色

            if temp_c <= 30:
                return '#00ffff'  # 青蓝
            elif temp_c <= 45:
                # 青蓝 (#00ffff) -> 绿 (#00ff00)
                ratio = (temp_c - 30) / 15.0
                r = 0
                g = int(128 * ratio) + 127
                b = int(255 * (1 - ratio))
                return f'#{r:02x}{g:02x}{b:02x}'
            elif temp_c <= 60:
                # 绿 (#00ff00) -> 黄 (#ffff00)
                ratio = (temp_c - 45) / 15.0
                r = int(255 * ratio)
                g = 255
                b = 0
                return f'#{r:02x}{g:02x}{b:02x}'
            elif temp_c <= 75:
                # 黄 (#ffff00) -> 橙 (#ff8000)
                ratio = (temp_c - 60) / 15.0
                r = 255
                g = int(255 - 127 * ratio)
                b = 0
                return f'#{r:02x}{g:02x}{b:02x}'
            else:
                return '#ff0000'  # 红
            
        errrr = False
        def fetch_thermal_info():
            """
            通过 adb 获取 thermal_zone type 与 temp。
            返回列表 [(type_str, temp_float_or_None, err_str_or_None), ...]
            如果 adb/命令失败，返回 [('ERROR', None, '错误信息'), ...]（单行）
            """
            nonlocal errrr
            #global UI_number
            try:
                # run types
                proc_types = subprocess.run(
                    ['adb', '-s', str(selected_device), 'shell', 'su', '-c', 'cat /sys/class/thermal/thermal_zone*/type'],
                    capture_output=True, text=True, timeout=3
                )
                proc_temps = subprocess.run(
                    ['adb', '-s', str(selected_device), 'shell', 'su', '-c', 'cat /sys/class/thermal/thermal_zone*/temp'],
                    capture_output=True, text=True, timeout=3
                )

                
                # 若命令 stderr 有输出，视为可能的权限/其他错误
                if (proc_types.stderr and proc_types.stderr.strip()) or (proc_temps.stderr and proc_temps.stderr.strip()):
                    # 合并 stderr 信息显示
                    err_msg = (proc_types.stderr or '') + (proc_temps.stderr or '')
                    print(err_msg)
                    if 'su: inaccessible or not found' in err_msg or 'su: not found' in err_msg:
                        messagebox.showerror('ADB Health Monitor','错误:SU异常，请检查root权限，安装并刷入Magisk！')
                        return False
                    elif 'no devices/emulators found' in err_msg:
                        errrr = True
                        text_1 = tk.Label(temp_monitor_window, foreground='#ffffff', background='#1f1f1f', text='正在等待设备连接...')# 创建一个Label控件，用于显示底部消息栏
                        text_1.place(height=80, width=window_size[0]-20-20,x=20,y=35)
                        temp_monitor_window.update()
                    elif 'more than one device/emulator':
                        errrr = True
                        text_1 = tk.Label(temp_monitor_window, foreground='#ffffff', background='#1f1f1f', text='多于一个设备，请选择')# 创建一个Label控件，用于显示底部消息栏
                        text_1.place(height=80, width=window_size[0]-20-20,x=20,y=35)
                        temp_monitor_window.update()
                elif errrr:
                    #UI_number = 0
                    time.sleep(1)
                    temp_monitor_window.after(0, temp_monitor_window.destroy)
                    #text_1.destroy()
                    errrr = False
                    print(errrr)
                #err_msg = err_msg.strip().splitlines()[0] if err_msg.strip() else "Unknown adb error"
                    return [('ERROR', None, err_msg) in err_msg]

                types = [t.strip() for t in proc_types.stdout.strip().splitlines() if t.strip()!='']
                temps_raw = [t.strip() for t in proc_temps.stdout.strip().splitlines() if t.strip()!='']

                # 如果 types 无法读取但 temps 有值，还是要尽量显示索引
                n = max(len(types), len(temps_raw))
                result = []
                for i in range(n):
                    tname = types[i] if i < len(types) else f'zone{i}'
                    temp_val = None
                    if i < len(temps_raw):
                        raw = temps_raw[i]
                        try:
                            val = int(raw)
                            # 若看起来像 milli°C（大于 1000），转为 °C
                            if abs(val) > 1000:
                                temp_val = round(val/1000.0, 1)
                            else:
                                temp_val = round(float(val), 1)
                        except Exception:
                            # 有些设备返回非数值（比如空、N/A），标为 None
                            temp_val = None
                    result.append((tname, temp_val, None))
                return result

            except subprocess.TimeoutExpired:
                return [('ERROR', None, 'adb timeout')]
            except FileNotFoundError:
                return [('ERROR', None, 'adb not found')]
            except Exception as e:
                return [('ERROR', None, str(e))]

        # create_widgets: 根据 thermal 数量创建标签（尽量与原布局一致）
        def create_widgets():
            global window_height
            global thermal_count
            global labels
            labels = []

            # 初始上去尝试获取一次信息以决定 label 数量
            info = fetch_thermal_info()
            # 如果返回的是错误单行，显示一行错误
            if len(info) == 1 and info[0][0] == 'ERROR':
                thermal_count = 1
                display_list = [('ERROR', None, info[0][2])]
            else:
                thermal_count = len(info)
                display_list = info

            widget_width = 120
            widget_height = 15
            left_margin = 20
            right_margin = 20
            top_margin = 65
            bottom_margin = 30
            vertical_spacing = 5

            for i, (name, temp, err) in enumerate(display_list):
                if err:
                    text = f"{name}: {err}"
                else:
                    text = f"{name}: {temp if temp is not None else '--'}°C"
                label = tk.Label(temp_monitor_window, text=text, width=widget_width, height=widget_height,
                                font=('微软雅黑','8'), background='#1e1e1e', fg='#a4a4a4')
                labels.append(label)

            row = 0
            col = 0
            for i in range(len(labels)):
                labels[i].place(x=left_margin + col * (widget_width + 0),
                                y=top_margin + row * (widget_height + vertical_spacing),
                                width=widget_width, height=widget_height)
                col += 1
                if col == 2:
                    col = 0
                    row += 1

            window_height = top_margin + (row+1) * (widget_height + vertical_spacing) + bottom_margin
            # 避免太短
            if window_height < 120:
                window_height = 120
            temp_monitor_window.geometry(f"{window_size[0]}x{window_height}")

        # updata_labels: 更新已有 labels 的文本（每次仅改 text，不销毁标签，避免闪烁）
        def updata_labels():
            info = fetch_thermal_info()
            # 如果之前创建的 labels 数量与现在不匹配，重建（这是少量重写，必要）
            if not labels:
                create_widgets()
            # 错误单行
            if len(info) == 1 and info[0][0] == 'ERROR':
                # 若 labels 数 !=1，重建
                if len(labels) != 1:
                    create_widgets()
                labels[0].config(text=f"ERROR: {info[0][2]}")
            else:
                # 如果数量变化，重建
                if len(info) != len(labels):
                    create_widgets()
                    # 尝试再次获取 to sync
                    info = fetch_thermal_info()

                for i, item in enumerate(info):
                    name, temp, err = item
                    if err:
                        text = f"{name}: {err}"
                    else:
                        text = f"{name}: {temp if temp is not None else '--'}°C"
                    # 防越界
                    if i < len(labels):
                        #labels[i].config(text=text)
                        # 如果是 ERROR 行，用醒目红色；否则按温度映射到颜色
                        if text.startswith("ERROR"):
                            labels[i].config(text=text, fg='#ff5555')
                        else:
                            # 解析出温度（示例： 'soc_thermal: 79.0°C' 或 'soc_thermal: --°C'）
                            # info 里已经有 temp 值，理想情况下直接使用 info；如果要从 text 解析也行：
                            try:
                                # 假设 info 与 labels 同步，优先使用 info
                                _, temp_val, _ = info[i]
                            except Exception:
                                temp_val = None
                            color = temp_to_color(temp_val)
                            labels[i].config(text=text, fg=color)

            # 使用 speed 作为刷新间隔（秒）
            temp_monitor_window.after(int(max(0.2, speed)*1000), updata_labels)

        # ============= 保留你原来的自制窗口管理器与菜单等 =============
        def Exit():
            temp_monitor_window.destroy()

        def set_speed(the_speed):
            global speed
            speed = the_speed

        def set_size(the_size):
            global size
            size = the_size
            try:
                cpu_OU.destroy()
            except Exception:
                pass
            cpu(size)

        def MouseDown(event):
            global mousX, mousY
            mousX=event.x
            mousY=event.y

        set_button = tk.Menubutton(temp_monitor_window, activeforeground="#f9f9f9",foreground='#f9f9f9',
                                        activebackground="#b6b6b6",background='#2d2d2d',
                                        text="⋮", font=('微软雅黑',16),borderwidth=0, direction='below')
        set_button.place(relheight=1, width=20,relx=0,rely=0)
        menu = tk.Menu(set_button, tearoff=False, borderwidth=0)
        set_button.config(menu=menu)
        speed_menu = tk.Menu(menu, tearoff=False)
        size_menu = tk.Menu(menu, tearoff=False)
        menu.add_cascade(label="更新速度", menu=speed_menu)
        menu.add_cascade(label="字号", menu=size_menu)
        speed_menu.add_command(label="1/2s  极高(高占用)", command=lambda: set_speed(0.5))
        speed_menu.add_command(label="1s    高", command=lambda: set_speed(1))
        speed_menu.add_command(label="2s    中（默认）", command=lambda: set_speed(2))
        speed_menu.add_command(label="3s    低", command=lambda: set_speed(3))
        speed_menu.add_command(label="4s    极低", command=lambda: set_speed(4))
        size_menu.add_command(label="8", command=lambda: set_size(8))
        size_menu.add_command(label="9", command=lambda: set_size(9))
        size_menu.add_command(label="10", command=lambda: set_size(10))
        size_menu.add_command(label="11（默认）", command=lambda: set_size(11))
        size_menu.add_command(label="12", command=lambda: set_size(12))
        size_menu.add_command(label="13", command=lambda: set_size(13))
        size_menu.add_command(label="14", command=lambda: set_size(14))

        # 右栏 / 退出键 / 标题保持原样
        rightLabel=tk.Label(temp_monitor_window,background='#2d2d2d')
        rightLabel.place(relheight=1, width=20,x=window_size[0]-20,y=0)
        Exitbuttonfont = tkFont.Font(size=12, weight=tkFont.BOLD)
        Exitbutton=tk.Button(temp_monitor_window, foreground='#f9f9f9',activebackground="red",
                            background='#2d2d2d',command=Exit,text='×',font=Exitbuttonfont,borderwidth=0)
        Exitbutton.place(relheight=1, width=20,x=window_size[0]-20,y=0)
        Exitbutton.bind('<Enter>', lambda event: Exitbutton.config(bg='#e81123'))
        Exitbutton.bind('<Leave>', lambda event: Exitbutton.config(bg='#2d2d2d'))

        def MouseMove_ADB_HM_title(event):
            w=ADB_HM_TITLE.winfo_x()
            h=ADB_HM_TITLE.winfo_y()
            temp_monitor_window.geometry(f'+{event.x_root - mousX-w}+{event.y_root - mousY-h}')

        ADB_HM_TITLE = tk.Label(temp_monitor_window, text='ADB Health Monitor', background='#323232', fg='#a4a4a4', font=('黑体','16'))
        ADB_HM_TITLE.place(x=20, y=0, height=35, width=window_size[0]-20-20)
        ADB_HM_TITLE.bind("<B1-Motion>",MouseMove_ADB_HM_title)
        ADB_HM_TITLE.bind("<Button-1>",MouseDown)

        # ============ RAM 更新（保留你原来的函数，线程方式） ============
        def updata_RAM(UI_number):
            """将 ram_usage 显示为 Android 设备的 RAM 使用率（例如 'RAM: 42.1%'）"""
            try:
                android_ram = fetch_android_ram_usage()
                #print(UI_number,num)
                if android_ram is None and UI_number == num:
                    ram_usage.set('RAM: --.-%')
                elif UI_number == num:
                    ram_usage.set(f'RAM: {android_ram:.1f}%')
            except Exception as e:
                if UI_number == num:
                    ram_usage.set('RAM: --.-%')
                # 可选：
                print(e)

        def updata_cpu_usage(UI_number):
            """将 cpu_text 显示为 Android 设备的总体 CPU 使用率（例如 'CPU: 12.3%'）"""
            try:
                android_cpu = fetch_android_cpu_usage()
                #print(UI_number,num)
                if android_cpu is None and UI_number == num:
                    cpu_text.set('CPU: --.-%')
                elif UI_number == num:
                    cpu_text.set('CPU:' + str(android_cpu).rjust(5) + '%')
            except Exception as e:
                if UI_number == num:
                    cpu_text.set('CPU: --.-%')
                # 可选：打印错误用于调试
                print("fetch android cpu error:", e)

        def updata():
            nonlocal num
            # 线程只负责 RAM 与原 CPU（以免破坏你的原始逻辑）
            print('updata',num)
            UI_number = num
            print
            while UI_number == num:
                updata_cpu_usage(UI_number)
                updata_RAM(UI_number)
                time.sleep(speed)

        updata_thread = threading.Thread(target=updata)
        updata_thread.daemon = True
        updata_thread.start()

        # cpu 显示区（保留）
        def cpu(sz):
            global cpu_OU
            cpu_OU = tk.Label(temp_monitor_window, textvariable=cpu_text, background='#1e1e1e', fg='#a4a4a4', font=('微软雅黑',sz))
            cpu_OU.place(x=20, y=35, height=30, width=window_size[0]-20-20)

        cpu(11)

        # 创建 thermal widgets（替代原 create_widgets）
        create_widgets()

        # 启动周期性更新 thermal labels（使用 after，和你原本的 updata_labels 名称一致）
        temp_monitor_window.after(1000, updata_labels)

        # RAM 显示（保留）
        RAM_label = tk.Label(temp_monitor_window, textvariable=ram_usage, background='#1e1e1e', fg='#a4a4a4', font=('微软雅黑','11'))
        RAM_label.place(x=20, y=window_height - 30, height=30, width=window_size[0]-20-20)

        
        temp_monitor_window.mainloop()
        return True


    status = True
    num = 0
    while status:
        num += 1
        print(num)
        status = main()
        if status:
            print('rebuild UI')

def set_update_interval(interval):
    global update_interval
    update_interval = interval

def adb_devices_info():#ADB设备信息
    execute_adb_command('')

def adb_logcat():#查看日志
    execute_adb_command('logcat')

def timer(len=None):
    global duration
    global return_info
    duration = 0
    return_info = None
    def thread_f(len_):
        global duration
        global return_info
        if type(len_) == int or len_ is None:
            while len_ is None:  # 秒表
                time.sleep(1)
                duration += 1
            if len_ is not None and len_ >= 0:  # 计时
                print('s')
                while duration < len_:
                    time.sleep(1)
                    duration += 1
                return_info = True
        else:
            return_info = 'type "len" must be int'
    thread_f(len)
    '''thread1 = threading.Thread(target=lambda: thread_f(len))
    thread1.setDaemon(True)
    thread1.start()'''
try:
    main()
except Exception as e:
    messagebox.showerror("错误",f"出现错误:\n{e}\n联系邮箱:ocr_8@qq.com进行反馈。")


'''
to do:
增加无线ADB功能
'''
