import board
import digitalio
import busio
import time

DC_PIN          = board.GP8
CS_PIN          = board.GP9

CLOCK_PIN       = board.GP10
MOSI_PIN        = board.GP11

BUSY_PIN        = board.GP13
RST_PIN         = board.GP12

EPD_WIDTH       = 800
EPD_HEIGHT      = 480

class EPD_7in5:
    def __init__(self):

        self.reset_pin = digitalio.DigitalInOut(RST_PIN)
        self.reset_pin.direction = digitalio.Direction.OUTPUT

        self.busy_pin = digitalio.DigitalInOut(BUSY_PIN)
        self.busy_pin.direction = digitalio.Direction.INPUT
        # self.busy_pin.drive_mode = digitalio.Pull.UP
        
        self.cs_pin = digitalio.DigitalInOut(CS_PIN)
        self.cs_pin.direction = digitalio.Direction.OUTPUT

        self.dc_pin = digitalio.DigitalInOut(DC_PIN)
        self.dc_pin.direction = digitalio.Direction.OUTPUT

        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        
        self.spi = busio.SPI(CLOCK_PIN, MOSI=MOSI_PIN )

        while not self.spi.try_lock():
            pass

        self.spi.configure(baudrate=4000000, phase=0, polarity=0)
        
        self.buffer = bytearray(self.height * self.width // 8)
        self.HW_Init()

    def delay_ms(self, delaytime):
        time.sleep(delaytime / 1000.)

    def digital_write(self, pin, value):
        pin.value = value

    def setBlack(self):
        for i in range(len(self.buffer)):
            self.buffer[i] = 0xFF
            
    def invert(self):
        for i in range(len(self.buffer)):
            self.buffer[i] = 255 - self.buffer[i]

    def setPixel(self, x, y, v):
        # if v == 1 :
        self.buffer[(x + y * EPD_WIDTH) // 8] |= 1 << (7 - (x % 8))
        # else :
            # self.buffer[(x + y * EPD_WIDTH) // 8] &= ~(1 << (7 - (x % 8)))

    # Hardware reset
    def reset(self):
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(50) 
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(2)
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(50)   

    def spi_writebyte(self, data):
        self.spi.write(bytearray(data))

    def send_command(self, command):
        self.digital_write(self.dc_pin, 0)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([command])
        self.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([data])
        self.digital_write(self.cs_pin, 1)

    def digital_read(self, pin):
        return pin.value

    def module_exit(self):
        self.digital_write(self.reset_pin, 0)

    def WaitUntilIdle(self):
        print("e-Paper busy")
        while(self.digital_read(self.busy_pin) == 0):    # Wait until the busy_pin goes LOW
            self.send_command(0x71)
            self.delay_ms(20)
        self.delay_ms(20) 
        print("e-Paper busy release")  

    def TurnOnDisplay(self):
        self.send_command(0x12) # DISPLAY REFRESH
        self.delay_ms(100)      #!!!The delay here is necessary, 200uS at least!!!
        self.WaitUntilIdle()

    def HW_Init(self):
        # EPD hardware init start     
        self.reset()
        
        self.send_command(0x01)  # POWER SETTING
        self.send_data(0x07)
        self.send_data(0x07)     # VGH=20V,VGL=-20V
        self.send_data(0x3f)     # VDH=15V
        self.send_data(0x3f)     # VDL=-15V
        
        self.send_command(0x04)  # POWER ON
        self.delay_ms(100)
        self.WaitUntilIdle()

        self.send_command(0X00)   # PANNEL SETTING
        self.send_data(0x1F)      # KW-3f   KWR-2F	BWROTP 0f	BWOTP 1f

        self.send_command(0x61)     # tres
        self.send_data(0x03)     # source 800
        self.send_data(0x20)
        self.send_data(0x01)     # gate 480
        self.send_data(0xE0)

        self.send_command(0X15)
        self.send_data(0x00)

        self.send_command(0X50)     # VCOM AND DATA INTERVAL SETTING
        self.send_data(0x10)
        self.send_data(0x00)

        self.send_command(0X60)     # TCON SETTING 
        self.send_data(0x22)

        self.send_command(0x65)     # Resolution setting
        self.send_data(0x00)
        self.send_data(0x00)     # 800*480
        self.send_data(0x00)
        self.send_data(0x00)
        
        return 0;

    def TurnOnDisplay(self):
        self.send_command(0x12) # DISPLAY REFRESH
        self.delay_ms(100)      #!!!The delay here is necessary, 200uS at least!!!
        self.WaitUntilIdle()

    def sleep(self):
        self.send_command(0x02) # power off
        self.WaitUntilIdle()
        self.send_command(0x07) # deep sleep
        self.send_data(0xa5)

    def display(self,blackimage):
        high = self.height
        wide = self.width // 8 
        
        # self.send_command(0x10)
        # for j in range(0, high):
        #     for i in range(0, wide):
        #          self.send_data(blackimage[i + j * wide])
                
        self.send_command(0x13) 
        for j in range(0, high):
            for i in range(0, self.width // 8):
                self.send_data(blackimage[i + j * wide])
                
        self.TurnOnDisplay()

    def sleep(self):
        self.send_command(0x02) # power off
        self.WaitUntilIdle()
        self.send_command(0x07) # deep sleep
        self.send_data(0xa5)
