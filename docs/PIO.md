# Programmable I/O (PIO)
Raspberry PI Pico has hardware support for communication protocols (I2C, SPI and UART).

**Programmable I/O** is used when there is no support for a specific hardware or not enough buses available
for I2C, SPI or UART.

Most microcontrollers use **bit-banging** for turning pins of and off directly, which uses the main processing core.
This can lead to timing problems and uses a lot of processing resources. Raspberry Pi Pico offers two PIO
blocks to free the main core.

One PIO block contains 4 state machines, simpler processing cores, which can handle data coming in or out
of the microcontroller. Each state machine has two FIFO structures (32 bits each), one for data coming in
and one for data going out, used to link the state machine with everything else.

A state machine and the program running on the main core do not need to be in sync.

## Assembly instructions
- `IN`: shifts 1-32 bits into input shift register from outside
- `OUT`: shifts 1-32 bits from output shift register to outside
- `PUSH`: sends data to RX FIFO
- `PULL`: get data from TX FIFO
- `MOV`: moves data from source to destination
- `IRQ`: set or clear the interrupt flag
- `SET`: writes data to destination
- `WAIT`: pauses until specific action happens
- `JMP`: moves to different point in code

## References
- https://magazine.raspberrypi.com/articles/what-is-programmable-i-o-on-raspberry-pi-pico
- 