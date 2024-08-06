#################################################################
# Guillaume W. Bres, 2022          <guillaume.bressaix@gmail.com>
#################################################################
# Class and macros to interact with AD9546 chipsets
#################################################################
from smbus import SMBus

import ft4222
from ft4222.SPI import Cpha, Cpol
from ft4222.SPIMaster import Mode, Clock, SlaveSelect
from ft4222.GPIO import Port, Dir

def sign_extend (value, length):
    """ sign extends given integer number to desired length """
    binary = bin(value)[2:]
    if binary[0] == '1':
        l = length - len(binary) 
        for i in range(l):
            binary = '1' + binary
        return int(binary,2)
    return value

class AD9546 :
    """ Class to interact with AD9546 chipset,
    only I2C bus supported @ the moment """
    def __init__ (self, bus, address):
        """ Creates an AD9546 device, 
        bus: [int] I2C bus number, X in /dev/i2c-X filesystem entry point   
        address: [int] i2c slave address
        """
        self.slv_addr = address
        # self.handle = SMBus()
        # self.handle.open(bus)
        ## ft4222 implementation
        self.handle = ft4222.openByDescription('FT4222 A')
        self.handleIO = ft4222.openByDescription('FT4222 B')
        self.handleIO.setSuspendOut(False)
        # self.handleIO.gpio_Init(gpio0 = Dir.OUTPUT) # use for reset of pll
        # self.handleIO.gpio_Write(Port.P0, False)
        # sleep(0.1)
        # self.handleIO.gpio_Write(Port.P0, True)
        self.handle.spiMaster_Init(Mode.SINGLE, Clock.DIV_128, Cpha.CLK_LEADING, Cpol.IDLE_LOW, SlaveSelect.SS0)
    
    def write_data (self, addr, data):
        """ Writes given data (uint8_t) to given address (uint16_t) """
        # msb = (addr & 0xFF00)>>8
        # lsb = addr & 0xFF
        # self.handle.write_i2c_block_data(self.slv_addr, msb, [lsb, data & 0xFF])
        ## ft4222 implementation
        spidata = (addr << 8) | data
        spidata = spidata.to_bytes(2, 'big')
        ft_status = self.handle.spiMaster_SingleWrite(spidata, True)


    def read_data (self, addr):
        """ Reads data at given address (uint16_t) returns uint8_t """
        # msb = (addr & 0xFF00)>>8
        # lsb = addr & 0xFF
        # self.handle.write_i2c_block_data(self.slv_addr, msb, [lsb])
        # data = self.handle.read_byte(self.slv_addr)
        ## ft4222 implementation
        spidata = (addr | 0x8000) << 8  # add extra byte for reading
        spidata = spidata.to_bytes(3, 'big')
        data_raw = self.handle.spiMaster_SingleReadWrite(spidata, True)
        data = int.from_bytes(data_raw[2:], 'big')
        return data

    def io_update (self):
        """ Performs `I/O update` operation. 
        Refer to device datasheet """
        self.write_data(0x000F, 0x01)
