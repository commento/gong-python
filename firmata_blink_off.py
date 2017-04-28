from pyfirmata import Arduino, util
board = Arduino('/dev/ttyACM0')

# board.digital[13].write(0)
# value = board.digital[13].read()

# if value is None:
#     board.digital[13].write(1)
# else:
#     if value == 0:
#         board.digital[13].write(1)
#     else:
#         board.digital[13].write(0)

board.digital[13].write(0)
print board.digital[13].read()
