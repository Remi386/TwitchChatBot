def read_ini_settings(file_name):
    settings = dict()

    with open(file_name, 'r') as fd:
        line = fd.readline().strip()
        while line != "":
            if line.startswith("#"):
                line = fd.readline().strip()
                continue

            parsed = line.split("=")

            if len(parsed) == 2:
                # Taking list of arguments
                if parsed[1][0] == '[' and parsed[1][-1] == ']':
                    parsed[1] = [str.lower(value).strip() for value in parsed[1][1:-1].split(",")]

                settings[parsed[0]] = parsed[1]

            line = fd.readline().strip()

    return settings