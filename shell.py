import waju

while True:
    instruction = input("waju > ")
    result,error = waju.run('<stdin>' , instruction) # stdin is for a file name which will be replaced later

    if "exit" in instruction:
        print('Exiting from Waju CLI')
        break

    if error:
        print(error.toString())
    else:
        print(result)