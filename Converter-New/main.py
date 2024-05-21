from source.gui.Gui import MainApp

def main() -> None:
    """
    The main function is the entry point for this application.
    It creates an instance of MainApp and calls its mainloop method, which
    starts the event loop that will run until the user closes it.
    
    :return: None
    """
    app = MainApp()
    app.mainloop()


if __name__ == "__main__":
    main()