"""
The router facilitates the transition from one view state to another
it releases and button event handlers and clears the screen
@params : any python object can be passed to the page
"""
from drivers.ili9341 import screenColor
from drivers.button import btnA, btnB, btnC
from ui.colors.basic import WHITE 

def transition( pagename, params=None ):

    try:
  
      # release any callback bound to the buttons
      btnA.restart() 
      btnB.restart() 
      btnC.restart()

      # clear the screen
      screenColor(WHITE)

      # import the page
      page = __import__( "ui/pages/"+pagename )  
      
      # initalize the page with transition parameters
      page.init( params )
      
    except Exception as err:
        raise err

    finally:
        import sys
        # flush the page from memory
        del sys.modules["ui/pages/"+pagename]




