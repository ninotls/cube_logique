import cube_gui
import wx


app = wx.App(False)
frame = cube_gui.CubeFrame(None)
frame.Show(True)
# start the applications
app.MainLoop()