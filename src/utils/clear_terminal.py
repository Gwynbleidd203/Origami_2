from os import get_terminal_size

def clear_terminal() -> None:
    """
        clear the current terminal
    """

    return print('\n' * get_terminal_size().lines)