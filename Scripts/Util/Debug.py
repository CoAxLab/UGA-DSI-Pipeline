def Log(message: str, debug: bool = True)->None:
    if debug == False:
        return None
    print(f'Log:\n\t{message}\n')