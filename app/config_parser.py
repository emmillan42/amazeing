from dataclasses import dataclass


# class MazeError(Exception):
#     """Excepción base para todo el proyecto."""
#     pass


# class ConfigError(MazeError):
#     """Error en el fichero de configuración."""
#     pass

Cell = tuple[int, int]

@dataclass(frozen=True)
class Config():
    width: int
    height: int
    entry: Cell
    exit: Cell
    output_file: str
    perfect: bool
    seed: int | None = None
    algorithm: str = "backtracker"
    pattern: str | None = "42"


def _parse_int(val_str: str) -> int:
    try:
        num = int(val_str)
        return num
    except ValueError:
        raise ConfigError("Ancho/Alto debe ser un número entero")


def _parse_bool(val_str: str) -> bool:
    pos_list = ("true", "1", "yes")
    neg_list = ("false", "0", "no")

    if val_str.lower() in pos_list:
        return True
    elif val_str.lower() in neg_list:
        return False
    else:
        raise ConfigError("Perfect debe ser un booleano")


def _parse_coords(val_str: str) -> Cell:
    try:
        split_val = val_str.split(',')
        if len(split_val) != 2:
            raise ConfigError("Coordenada de Entrada/Salida no válida")
        first = int(split_val[0])
        second = int(split_val[1])
        tupla = (first, second)
        return tupla
    except Exception:
        raise ConfigError("Entrada/Salida debe ser una tupla de enteros")


def parse_config(filepath: str) -> Config:
    raw_data = {}
    with open(filepath) as f:
        for line in f:
            strip_line = line.strip()
            if not strip_line or strip_line[0] == '#':
                continue
            data_split = strip_line.split('=', 1)
            if len(data_split) != 2:
                raise ConfigError("Error de parseo")
            key = data_split[0].strip()
            value = data_split[1].strip()
            raw_data[key] = value
        print(raw_data)

    required_keys = ["WIDTH", "HEIGHT", "ENTRY", "EXIT",
                     "OUTPUT_FILE", "PERFECT"]
    for clave in required_keys:
        if clave in raw_data:
            continue
        else:
            raise ConfigError(
                f"No se encuentran todas las claves. Falta {clave}"
            )

    width = _parse_int(raw_data["WIDTH"])
    height = _parse_int(raw_data["HEIGHT"])
    entry = _parse_coords(raw_data["ENTRY"])
    exit = _parse_coords(raw_data["EXIT"])
    perfect = _parse_bool(raw_data["PERFECT"])

    # COMPROBACIONES FINALES
    if width < 1 or height < 1:
        raise ConfigError("Largo/Ancho igual a 0 o negativo")
    if entry[0] >= width or entry[0] < 0:
        raise ConfigError("Coordenada X de entrada no válida")
    if entry[1] >= height or entry[1] < 0:
        raise ConfigError("Coordenada Y de entrada no válida")
    if exit[0] >= width or exit[0] < 0:
        raise ConfigError("Coordenada X de salida no válida")
    if exit[1] >= height or exit[1] < 0:
        raise ConfigError("Coordenada Y de salida no válida")
    if entry == exit:
        raise ConfigError("Misma coordenada de entrada y salida")

    seed = _parse_int(raw_data["SEED"]) if raw_data.get("SEED") else None
    algorithm = raw_data.get("ALGORITHM", "backtracker")
    pattern = raw_data.get("PATTERN") if "PATTERN" in raw_data else "42"
    
    return Config(
        width=width,
        height=height,
        entry=entry,
        exit=exit,
        output_file=raw_data["OUTPUT_FILE"],
        perfect=perfect,
        seed=seed,
        algorithm=algorithm,
        pattern=pattern,
    )


# data_config = parse_config('test.txt')
# print(data_config)
