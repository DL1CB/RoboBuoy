import ui.components.qrcode as qrcode
from ui.router      import transition
"""
Shows the user the QRcode to the app
"""
def init( params ):
    """render welcome page"""
    qrcode.render() 

