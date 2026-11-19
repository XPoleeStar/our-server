while (inp := input()) != 'exit':
    fullname, group, login, password = inp.split()
    print(fullname, group, hash(login), hash(password))