import wx
import wx.xrc
import serial.tools.list_ports


def _get_all_serial_ports():
    ports = serial.tools.list_ports.comports()
    list_all_ports = []

    for port, _, _ in sorted(ports):
        list_all_ports.append(port)

    return list_all_ports


class MyFrame1(wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=wx.EmptyString, pos=wx.DefaultPosition,
                          size=wx.Size(680, 486), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        sb_sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"Cube Logique"), wx.VERTICAL)

        self.m_staticText1 = wx.StaticText(sb_sizer.GetStaticBox(), wx.ID_ANY, u"Port Série:", wx.DefaultPosition,
                                           wx.DefaultSize, 0)
        self.m_staticText1.Wrap(-1)

        sb_sizer.Add(self.m_staticText1, 0, wx.ALL, 5)

        m_choice3_choices = _get_all_serial_ports()
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
        self.m_button2.Bind(wx.EVT_BUTTON, self.refresh)
        self.m_button3.Bind(wx.EVT_BUTTON, self.open_serial_port)
        self.m_button4.Bind(wx.EVT_BUTTON, self.send_command)
        self.Bind(wx.EVT_MENU, self.quit, id=self.m_menuItem2.GetId())

    def __del__(self):
        pass

    # Virtual event handlers, override them in your derived class
    def refresh(self, event):
        event.Skip()
        choices = _get_all_serial_ports()
        self.m_choice3.Clear()
        self.m_choice3.Append(choices)

    def open_serial_port(self, event):
        event.Skip()
        port_name = self.m_choice3.GetString(self.m_choice3.GetCurrentSelection())
        port_baud = "115200"
        ser = serial.Serial(port_name, port_baud, timeout=0, write_timeout=0)
        # timeout=0 means "non-blocking," ser.read() will always return, but
        # may return a null string.
        self.m_textCtrl2.AppendText(f"opened port {port_name} at {str(port_baud)} baud\n")
        return ser

    @staticmethod
    def send_command(event):
        event.Skip()

    @staticmethod
    def quit(event):
        event.Skip()
        exit()


app = wx.App(False)
frame = MyFrame1(None)
frame.Show(True)
# start the applications
app.MainLoop()
