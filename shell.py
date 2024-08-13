
import waju



while True:
    instruction = input("waju > ")
    # result,error = waju1.run('<stdin>', instruction)
    result,error = waju.run('<stdin>' , instruction)

    if error:
        print(error.toString())
    else:
        print(result)


    if('..' in instruction):
        break