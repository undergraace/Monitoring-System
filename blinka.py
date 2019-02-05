import board
import digitalio
import busio
import time
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

_neutralVoltage = 1500.0
_acidVoltage = 2032.44

print('hello World')


spi = busio.SPI(board.SCLK, board.MOSI, board.MISO)
print('SPI OK')

cs = digitalio.DigitalInOut(board.D5)
print('cs OK')

mcp = MCP.MCP3008(spi, cs)
print('mcp')

chan = AnalogIn(mcp, MCP.P0)

def readPh(voltage):
    slope = (7.00 - 4.00)/((_neutralVoltage - 1500.0) / 3.0 - (_acidVoltage - 1500.0) / 3.0)
    intercept = 7.0 - slope*(_neutralVoltage - 1500.0)/3.0
    _phValue = slope*((voltage*1000)-1500.0)/3.0+intercept
    return round(_phValue,2)
    

while True:
    
    print('CLK: ', board.SCLK)
    print('MOSI: ', board.MOSI)
    print('MISO: ', board.MISO)
    print('D5: ', board.D5)
    print('P0: ', MCP.P0)
    print('raw: ', chan.value)
    print('volt: ', str(chan.voltage))
    print('PH: ', readPh(chan.voltage))
    time.sleep(1.0)



    
    
    

