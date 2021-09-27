#https://github.com/m5stack/UIFlow-Code/blob/master/LICENSE.md
import machine 
import micropython
import time

_BUTTON_A_PIN = const(39)
_BUTTON_B_PIN = const(38)
_BUTTON_C_PIN = const(37)

PRESS = const(0x01)
RELEASE = const(0x02)
LONGPRESS = const(0x04)
DOUBLEPRESS = const(0x08)
MULTIPRESS = const(0x10)
PRESSWAIT = const(0x20)

state_list = [PRESS, RELEASE, LONGPRESS, DOUBLEPRESS]

class BtnChild:
    def __init__(self, pin, dbtime=20):
        self.pin = machine.Pin(pin, mode=machine.Pin.IN, pull=machine.Pin.PULL_UP)
        self._event = 0
        self._eventLast = 0
        self._valueLast = 1
        self._pressTime = 0
        self._releaseTime = 0
        self._doubleTime = 220
        self._dbtime = dbtime
        self._holdTime = 1000.0
        self._cbState = PRESS | RELEASE
        self._eventTime = {PRESS:0, RELEASE:0, LONGPRESS:0, DOUBLEPRESS:0}
        self.cb = {PRESS: None, RELEASE:None, LONGPRESS:None, DOUBLEPRESS:None}

    def wasDoublePress(self, callback=None):
        self._cbState |= DOUBLEPRESS
        if callback:
            self.cb[DOUBLEPRESS] = callback
        elif self._event & DOUBLEPRESS:
            self._event -= DOUBLEPRESS
            return True
        else:
            return False

    def pressFor(self, holdTime=1.0, callback=None):
        self._holdTime = holdTime * 1000
        self._cbState |= LONGPRESS
        if callback:
            self.cb[LONGPRESS] = callback
        elif self._event & LONGPRESS:
            self._event -= LONGPRESS
            return True
        else:
            return False

    def wasReleased(self, callback=None):
        if callback:
            self.cb[RELEASE] = callback
        elif self._event & RELEASE:
            self._event -= RELEASE
            return True
        else:
            return False        

    def wasPressed(self, callback=None):
        if callback:
            self.cb[PRESS] = callback
        elif self._event & PRESS:
            self._event -= PRESS
            return True
        else:
            return False

    def isPressed(self):
        return not self.pin.value()

    def isReleased(self):
        return self.pin.value()        

    def restart(self):
        self._cbState = PRESS | RELEASE
        self.cb = {PRESS: None, RELEASE:None, LONGPRESS:None, DOUBLEPRESS:None}
        self._eventTime = {PRESS:0, RELEASE:0, LONGPRESS:0, DOUBLEPRESS:0}
        self._event = 0
        self._pressTime = 0
        self._releaseTime = 0
        self._valueLast = 1

    def deinit(self):
        pass
    
    def upDate(self):
        value = self.pin.value()
        state = self._eventLast ^ self._event
        if state:
            for i in state_list:
                if state & i:
                    if self._event & i:
                        self._eventTime[i] = 40
                    else:
                        self._eventTime[i] = 0
            self._eventLast = self._event

        for i in state_list:
            if self._eventTime[i] > 1:
                self._eventTime[i] -= 1
            elif self._eventTime[i] == 1:
                self._eventTime[i] = 0
                self._event &= ~i

        if value ^ self._valueLast:
            nowTime = time.ticks_ms()
            self._valueLast = value
            if not value:
                if nowTime - self._pressTime > self._dbtime:
                    if self._cbState & DOUBLEPRESS and nowTime - self._pressTime < self._doubleTime:
                        self._event |= DOUBLEPRESS
                    self._event |= PRESSWAIT
                self._pressTime = nowTime
            else:
                if nowTime - self._releaseTime> self._dbtime:
                    if self._cbState & LONGPRESS and nowTime - self._pressTime > self._holdTime:
                        self._event |= LONGPRESS
                    else:
                        self._event |= RELEASE
                self._releaseTime = nowTime    

class Btn:
    def __init__(self, multiTime=50):
        self.timer = machine.Timer(1)
        self.timer.init(period=10, mode=self.timer.PERIODIC, callback=self.timerCb)
        self.btn = []
        self.multiList = []
        self._multiTime = multiTime

    def attach(self, pin):
        self.btn.append(BtnChild(pin))
        return self.btn[-1]
    
    def detach(self, btnIn):
        if btnIn in self.btn:
            self.btn.remove(btnIn)

    def restart(self):
        self.multiList = []
        self.btn = self.btn[:3]
        for i in self.btn:
            i.restart() 
    
    def multiBtnCb(self, btn1, btn2, callback=None):
        self.multiList.append([btn1, btn2, callback])
        btn1._cbState |= MULTIPRESS
        btn2._cbState |= MULTIPRESS

    def timerCb(self, arg):
        nowTime = time.ticks_ms()
        for i in self.btn:
            i.upDate()

        for i in self.multiList:
            if i[0]._event & PRESSWAIT and i[1]._event & PRESSWAIT:
                if abs(i[0]._pressTime - i[1]._pressTime) < self._multiTime:
                    i[0]._event &= ~PRESSWAIT
                    i[1]._event &= ~PRESSWAIT
                    i[2]()
        
        for i in self.btn:
            if i._event & DOUBLEPRESS:
                if i.cb[DOUBLEPRESS]:
                    i.cb[DOUBLEPRESS]()
                    i._event &= ~PRESSWAIT
                    i._event &= ~DOUBLEPRESS                    
            
            if i._event & PRESSWAIT:
                if i._cbState & DOUBLEPRESS:
                    if nowTime - i._pressTime > i._doubleTime:
                        i._event &= ~PRESSWAIT
                        if i.cb[PRESS]:
                            i.cb[PRESS]()         
                        else:
                            i._event |= PRESS
                            i._eventTime[0] = 40

                elif i._cbState & MULTIPRESS:
                    if nowTime - i._pressTime > self._multiTime:
                        i._event &= ~PRESSWAIT
                        if i.cb[PRESS]:
                            i.cb[PRESS]()
                        else:
                            i._event |= PRESS

                else:
                    i._event &= ~PRESSWAIT
                    if i.cb[PRESS]:
                        i.cb[PRESS]()
                    else:
                        i._event |= PRESS

            if i._event & LONGPRESS:
                if i.cb[LONGPRESS]:
                    i._event &= ~LONGPRESS
                    i.cb[LONGPRESS]()

            if i._event & RELEASE:
                if i.cb[RELEASE]:
                    i._event &= ~RELEASE
                    i.cb[RELEASE]()

    def deinit(self):
        pass

btn = Btn()
btnA = btn.attach(_BUTTON_A_PIN)
btnB = btn.attach(_BUTTON_B_PIN)
btnC = btn.attach(_BUTTON_C_PIN)    