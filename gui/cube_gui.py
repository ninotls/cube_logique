import wx
import cube_commands
import sys
import time


class CubeFrame(wx.Frame):
    def __init__(self, parent):
        self.cube_serial = None
        self.cube_commands = None
        self.logs = None
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=wx.EmptyString, pos=wx.DefaultPosition,
                          size=wx.Size(680, 486), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        sb_sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"Cube Logique"), wx.VERTICAL)

        self.m_staticText1 = wx.StaticText(sb_sizer.GetStaticBox(), wx.ID_ANY, u"Port Série:", wx.DefaultPosition,
                                           wx.DefaultSize, 0)
        self.m_staticText1.Wrap(-1)

        sb_sizer.Add(self.m_staticText1, 0, wx.ALL, 5)

        m_choice3_choices = cube_commands.CubeSerial.get_all_serial_ports()
        self.m_choice3 = wx.Choice(sb_sizer.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                   m_choice3_choices, 0)
        self.m_choice3.SetSelection(0)
        sb_sizer.Add(self.m_choice3, 0, wx.ALL, 5)

        self.m_button2 = wx.Button(sb_sizer.GetStaticBox(), wx.ID_ANY, u"Refresh", wx.DefaultPosition, wx.DefaultSize,
                                   0)
        sb_sizer.Add(self.m_button2, 0, wx.ALL, 5)

        self.m_button3 = wx.Button(sb_sizer.GetStaticBox(), wx.ID_ANY, u"Connexion", wx.DefaultPosition, wx.DefaultSize,
                                   0)
        sb_sizer.Add(self.m_button3, 0, wx.ALL, 5)

        self.m_staticText2 = wx.StaticText(sb_sizer.GetStaticBox(), wx.ID_ANY, u"Commande:", wx.DefaultPosition,
                                           wx.DefaultSize, 0)
        self.m_staticText2.Wrap(-1)

        sb_sizer.Add(self.m_staticText2, 0, wx.ALL, 5)

        self.m_textCtrl3 = wx.TextCtrl(sb_sizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                       wx.Size(500, -1), wx.TE_PROCESS_ENTER)
        sb_sizer.Add(self.m_textCtrl3, 0, wx.ALL, 5)

        self.m_button4 = wx.Button(sb_sizer.GetStaticBox(), wx.ID_ANY, u"Envoyer", wx.DefaultPosition, wx.DefaultSize,
                                   0)
        sb_sizer.Add(self.m_button4, 0, wx.ALL, 5)

        self.m_staticText3 = wx.StaticText(sb_sizer.GetStaticBox(), wx.ID_ANY, u"Console:", wx.DefaultPosition,
                                           wx.DefaultSize, 0)
        self.m_staticText3.Wrap(-1)

        sb_sizer.Add(self.m_staticText3, 0, wx.ALL, 5)

        self.m_textCtrl2 = wx.TextCtrl(sb_sizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                       wx.Size(500, 500),
                                       wx.HSCROLL | wx.TE_MULTILINE | wx.TE_NO_VSCROLL | wx.TE_READONLY | wx.TE_WORDWRAP)
        sb_sizer.Add(self.m_textCtrl2, 0, wx.ALL, 5)

        self.SetSizer(sb_sizer)
        self.Layout()
        self.m_menubar3 = wx.MenuBar(wx.MB_DOCKABLE)
        self.m_menu1 = wx.Menu()
        self.m_menuItem1 = wx.MenuItem(self.m_menu1, wx.ID_ANY, u"Redémarrer le cube", wx.EmptyString, wx.ITEM_NORMAL)
        self.m_menu1.Append(self.m_menuItem1)

        self.m_menuItem2 = wx.MenuItem(self.m_menu1, wx.ID_ANY, u"Quitter", wx.EmptyString, wx.ITEM_NORMAL)
        self.m_menu1.Append(self.m_menuItem2)

        self.m_menubar3.Append(self.m_menu1, u"Outils")

        self.m_menu2 = wx.Menu()
        self.m_menubar3.Append(self.m_menu2, u"A propos")

        self.SetMenuBar(self.m_menubar3)

        self.Centre(wx.BOTH)

        # Connect Events
        self.m_button2.Bind(wx.EVT_BUTTON, self.refresh_ports)
        self.m_button3.Bind(wx.EVT_BUTTON, self.open_port)
        self.m_button4.Bind(wx.EVT_BUTTON, self.send_command)
        self.Bind(wx.EVT_MENU, self.quit, id=self.m_menuItem2.GetId())
        self.Bind(wx.EVT_MENU, self.reset, id=self.m_menuItem1.GetId())

    # Virtual event handlers, override them in your derived class
    def refresh_ports(self, event):
        event.Skip()
        ports_list = cube_commands.CubeSerial.get_all_serial_ports()
        self.update_serial_port(ports_list)

    def open_port(self, event):
        event.Skip()
        port_name = self.m_choice3.GetString(self.m_choice3.GetCurrentSelection())
        self.cube_serial = cube_commands.CubeSerial(port_name, 115200)
        self.m_textCtrl2.AppendText(f"Port Ouvert {port_name}\n")
        self.cube_commands = cube_commands.HWInterface(self.cube_serial.serial, 0.1, 5)
        self.cube_commands.register_callback(self.display)
        self.m_textCtrl2.AppendText(f"Cube Logique ok\n")

    def display(self, data):
        res_split = data.split("\n")
        for data in res_split:
            self.m_textCtrl2.AppendText(f"Cube: {data}\n")

    def update_serial_port(self, ports_list):
        self.m_choice3.Clear()
        self.m_choice3.Append(ports_list)

    def reset(self, event):
        event.Skip()
        self.send_command(event, cmd="rst")

    def send_command(self, event, cmd=None):
        event.Skip()
        self.m_textCtrl2.Clear()
        if not cmd:
            cmd = self.m_textCtrl3.GetValue()
        else:
            cmd = cmd
        val = self.cube_commands.parse_command(cmd)
        if val:
            self.m_textCtrl2.AppendText(f"Sending command {val.decode('utf-8')}\n")
            sys.stdout.flush()
            self.cube_commands.write_hw(val)
            while "Cube:" not in self.m_textCtrl2.GetValue():
                time.sleep(0.5)

    @staticmethod
    def quit(event):
        event.Skip()
        exit()
