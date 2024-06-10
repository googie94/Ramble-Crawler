import ramble_commands as commands
import os


class Option:
    def __init__(self, name, command, prep_call=None):
        self.name = name
        self.command = command
        self.prep_call = prep_call

    def __str__(self):
        return self.name

    def choose(self):
        data = self.prep_call() if self.prep_call else None
        message = self.command.execute(data) if data else self.command.execute()
        print(message)


def print_options(options):
    for shortcut, option in options.items():
        print(f"({shortcut}) {option}")
    print()


def option_choice_is_valid(choice, options):
    return choice in options or choice.upper() in options


def get_option_choice(options):
    choice = input("옵션을 선택하세요: ")
    while not option_choice_is_valid(choice, options):
        print("정확히 입력해주세요")
        choice = input("옵션을 선택하세요: ")
    return options[choice.upper()]


def get_user_input(label, required=True):
    value = input(f"{label}: ") or None
    while required and not value:
        value = input(f"{label}: ") or None
    return value


def get_domain_data():
    return {
        "naver_cafe_id": get_user_input("cafe_id"),
        "naver_menu_id": get_user_input("menu_id"),
        "description": get_user_input("description"),
    }


def get_domain_id_for_ramble():
    return get_user_input("정보를 수집할 아이디를 입력하세요")


def get_domain_info_id_for_deletion():
    return get_user_input("삭제할 아이디를 입력하세요")


def clear_screen():
    clear = "cls" if os.name == "nt" else "clear"
    os.system(clear)


def loop():
    print("Welcome to Ramble!")
    options = {
        "A": Option(
            "네이버 카페 정보 추가하기",
            commands.AddDomainData(),
            prep_call=get_domain_data,
        ),
        "L": Option("네이버 카페 정보 보기 - 일자순", commands.ListDomainData()),
        "D": Option(
            "네이버 카페정보 삭제하기",
            commands.DeleteDomainData(),
            prep_call=get_domain_info_id_for_deletion,
        ),
        "R": Option(
            "번호 수집 시작하기",
            commands.RambleNaverCafeForPhone(),
            prep_call=get_domain_id_for_ramble,
        ),
        "Q": Option("나가기", commands.QuitCommand()),
    }
    clear_screen()
    print_options(options)
    chosen_option = get_option_choice(options)
    clear_screen()
    chosen_option.choose()
    _ = input("\nEnter를 누르면 메뉴로 돌아갑니다")


if __name__ == "__main__":
    while True:
        loop()
