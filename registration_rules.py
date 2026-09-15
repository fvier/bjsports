"""Regras de identificação e cadastro compartilhadas pelo formulário e servidor."""
import re

# Anatel: https://www.gov.br/anatel/pt-br/regulado/numeracao/codigos-nacionais
BRAZIL_DDDS = tuple('11 12 13 14 15 16 17 18 19 21 22 24 27 28 31 32 33 34 35 37 38 41 42 43 44 45 46 47 48 49 51 53 54 55 61 62 63 64 65 66 67 68 69 71 73 74 75 77 79 81 82 83 84 85 86 87 88 89 91 92 93 94 95 96 97 98 99'.split())


def cpf_digits(value):
    return re.sub(r'[^0-9]', '', value or '')


def age_on(birth_date, reference):
    return reference.year - birth_date.year - ((reference.month, reference.day) < (birth_date.month, birth_date.day))

def class_age_error(birth_date, minimum, maximum, reference):
    """Aplica somente os limites informados; público Kids não define idade."""
    if minimum is None and maximum is None:
        return None
    if birth_date is None:
        return 'Informe a data de nascimento para conferir a faixa etária da turma.'
    age = age_on(birth_date, reference)
    if (minimum is not None and age < minimum) or (maximum is not None and age > maximum):
        return 'A idade do aluno está fora da faixa etária configurada para esta turma.'
    return None


def training_weekdays(schedule, flexible=False):
    if flexible or schedule == 'todos':
        return set(range(7))
    return {'ter-qui': {1, 3}, 'seg-qua-sex': {0, 2, 4}}.get(schedule, set())


def parse_age_limits(minimum, maximum):
    """Limites opcionais em anos completos; vazio nunca implica um limite padrão."""
    def parse(value, label):
        raw = str(value).strip() if value is not None else ''
        if not raw:
            return None
        if not re.fullmatch(r'[0-9]{1,3}', raw) or not 0 <= int(raw) <= 150:
            raise ValueError(f'Informe a idade {label} em anos completos, de 0 a 150, ou deixe em branco.')
        return int(raw)

    minimum, maximum = parse(minimum, 'mínima'), parse(maximum, 'máxima')
    if minimum is not None and maximum is not None and minimum > maximum:
        raise ValueError('A idade máxima deve ser igual ou maior que a idade mínima.')
    return minimum, maximum
