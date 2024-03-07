from lucky.board import board
import lucky.libs.touch as touch

# Display resolution
EPD_WIDTH       = 212
EPD_HEIGHT      = 104

RST_PIN         = board.EPD_RST_PIN  # 9
DC_PIN          = board.EPD_DC_PIN    # 8  
CS_PIN          = board.EPD_CS_PIN    # 10
BUSY_PIN        = board.EPD_BUSY_PIN # 11

TRST    = board.TP_RST_PIN      # 21
INT     = board.TP_INT_PIN       # 20

KEY0 = board.KEY1            # 18  
KEY1 = board.KEY2            # 19
KEY2 = board.KEY3            # 17

class config():
    def __init__(self):
        self.reset_pin = board.pin(RST_PIN, board.mode.OUTPUT)
        self.busy_pin = board.pin(BUSY_PIN, board.mode.INPUT)
        self.cs_pin = board.pin(CS_PIN, board.mode.OUTPUT)

        self.trst_pin = board.pin(TRST, board.mode.OUTPUT)
        self.int_pin = board.pin(INT, board.mode.INPUT)

        self.key0 = board.pin(KEY0, board.mode.INPUT_PULLUP)
        self.key1 = board.pin(KEY1, board.mode.INPUT_PULLUP)
        self.key2 = board.pin(KEY2, board.mode.INPUT_PULLUP)
        
        self.spi = board.spi
        self.i2c = board.i2c
        self.dc_pin = board.pin(DC_PIN, board.mode.OUTPUT)

    def digital_write(self, pin, value):
        pin.value(value)

    def digital_read(self, pin):
        return pin.value()

    def delay_ms(self, delaytime):
        board.delay_ms(delaytime)

    def spi_writebyte(self, data):
        self.spi.write(bytearray(data))

    def module_exit(self):
        self.digital_write(self.reset_pin, 0)
        self.digital_write(self.trst_pin, 0)

class EPD_2in9():
    def __init__(self):
        self.config = config()

        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

    def reset(self):
        self.config.digital_write(self.config.reset_pin, 1)
        self.config.delay_ms(50) 
        self.config.digital_write(self.config.reset_pin, 0)
        self.config.delay_ms(2)
        self.config.digital_write(self.config.reset_pin, 1)
        self.config.delay_ms(50)   

    def send_command(self, command):
        self.config.digital_write(self.config.dc_pin, 0)
        self.config.digital_write(self.config.cs_pin, 0)
        self.config.spi_writebyte([command])
        self.config.digital_write(self.config.cs_pin, 1)

    def send_data(self, data):
        self.config.digital_write(self.config.dc_pin, 1)
        self.config.digital_write(self.config.cs_pin, 0)
        self.config.spi_writebyte([data])
        self.config.digital_write(self.config.cs_pin, 1)
        
    def ReadBusy(self):
        while(self.config.digital_read(self.config.busy_pin) == 1):      #  0: idle, 1: busy
            self.config.delay_ms(10) 

    def init(self):
        self.reset()
        self.config.delay_ms(200)
        self.send_command(0x12)
        self.ReadBusy()

        self.send_command(0x74) #set analog block control
        self.send_data(0x54)
        self.send_command(0x7E) #set digital block control
        self.send_data(0x3B)

        self.send_command(0x01) #Driver output control
        self.send_data(0x07)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
         
        self.send_command(0x0C) #Entry mode
        self.send_data(0x01)
        
        self.SetWindow(0, 0, self.width-1, self.height-1)
        self.ReadBusy()
        
    def SetWindow(self, x_start, y_start, x_end, y_end):
        self.send_command(0x44) # SET_RAM_X_ADDRESS_START_END_POSITION
        self.send_data((x_start>>3) & 0xFF)
        self.send_data((x_end>>3) & 0xFF)
        self.send_command(0x45) # SET_RAM_Y_ADDRESS_START_END_POSITION
        self.send_data(y_start & 0xFF)
        self.send_data((y_start >> 8) & 0xFF)
        self.send_data(y_end & 0xFF)
        self.send_data((y_end >> 8) & 0xFF)

    def SetCursor(self, x, y):
        self.send_command(0x4E) # SET_RAM_X_ADDRESS_COUNTER
        self.send_data((x>>3) & 0xFF)
        
        self.send_command(0x4F) # SET_RAM_Y_ADDRESS_COUNTER
        self.send_data(y & 0xFF)
        self.send_data((y >> 8) & 0xFF)
        self.ReadBusy()
        
    def display(self, image):
        if (image == None):
            return            
        self.send_command(0x24) # WRITE_RAM
        for i in range(0, self.height * int(self.width/8)):
            self.send_data(image[i])   
        self.config.delay_ms(100)

    def Clear(self, color):
        self.send_command(0x24) # WRITE_RAM
        for i in range(0, self.height * int(self.width/8)):
            self.send_data(color)
        self.config.delay_ms(100)

    def sleep(self):
        self.send_command(0x10) # DEEP_SLEEP_MODE
        self.send_data(0x01)
        
        self.config.delay_ms(2000)
        self.config.module_exit()

def get_key():
    if(board.pin(KEY0).value() == 0):
        return 1
    elif(board.pin(KEY1).value() == 0):
        return 2
    elif(board.pin(KEY2).value() == 0):
        return 3
    else:
        return 0

epd = EPD_2in9()
flag_t = NumSelect = 1
ReFlag = SelfFlag  = temp = isHide = key_value = 0
buf = ['$', '1', '9', '.', '8', '9']

epd.init()
touch.init()

epd.Clear(0xff)
epd.text("Select", 7, 13, 0x00)
epd.text("Adjust", 74, 13, 0x00)
epd.text("Display", 35, 10, 0x00)
epd.text("Show/Hied", 26, 22, 0x00)
epd.text("On Sale!!!", 10, 50, 0x00)
epd.text("Discount %30", 10, 75, 0x00)
epd.text("Price: ", 10, 100, 0x00)
epd.text(''.join(buf), 66, 100, 0x00)

epd.display(epd.buffer)

while True:
    touch_data = touch.read_data()
    key_value = get_key()
    
    if touch_data or key_value:
        if key_value:
            x, y = epd.width+1, epd.height+1
        else:
            x, y = touch_data
        
        if x > 5 and y > 10 and x < 61 and y < 24 or key_value == 1:
            key_value = 0
            NumSelect += 1
            if NumSelect > 4:
                NumSelect = 1
            epd.fill_rect(66, 10, 50, 15, 0xff)
            epd.text("^", 66 + NumSelect*8, 10, 0x00)
            epd.display(epd.buffer)
            
        if x > 30 and y > 5 and x < 96 and y < 18 or key_value == 2:
            key_value = 0
            epd.fill_rect(66, 100, 50, 15, 0xff)
            epd.text(''.join(buf), 66, 100, 0x00)
            epd.display(epd.buffer)
            
        if x > 72 and y > 10 and x < 123 and y < 24 or key_value == 3:
            key_value = 0
            temp = NumSelect
            if NumSelect>2:
                temp += 1
            if buf[temp] == '9':
                buf[temp] = '0'
            else:
                buf[temp] = chr(ord(buf[temp]) + 1)
            epd.fill_rect(66, 100, 50, 15, 0xff)
            epd.text(''.join(buf), 66, 100, 0x00)
            epd.display(epd.buffer)
            
        if x > 21 and y > 17 and x < 103 and y < 35:
            if isHide % 2:
                epd.text("Select", 7, 13, 0x00)
                epd.text("Adjust", 74, 13, 0x00)
                epd.text("Display", 35, 10, 0x00)
                epd.text("Show/Hied", 26, 22, 0x00)
                epd.text("On Sale!!!", 10, 50, 0x00)
                epd.text("Discount %30", 10, 75, 0x00)
                epd.text("Price: ", 10, 100, 0x00)
                epd.text(''.join(buf), 66, 100, 0x00)
            else:
                epd.fill_rect(0, 0, epd.width, 40, 0xff)
                epd.fill_rect(0, 80, epd.width, 24, 0xff)
            isHide += 1
            epd.display(epd.buffer)