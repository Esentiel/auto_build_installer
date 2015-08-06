def logg(msg):
    with open('main.log', 'a') as thefile:
        thefile.write(str(msg)+'\n')
    thefile.close()
    