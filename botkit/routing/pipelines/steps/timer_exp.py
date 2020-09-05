from timeit import timeit


class Chat:
    def __init__(self):
        self.id = 12345678


class Update:
    def __init__(self) -> None:
        self.chat = Chat()

    @property
    def chat_id_walrus(self):
        return chat.id if (chat := self.chat) else None

    @property
    def chat_id_walrus_equivalent(self):
        chat = self.chat
        return chat.id if chat else None

    @property
    def chat_id_normal(self):
        return self.chat.id if self.chat else None


def run_with_walrus():
    u = Update()
    x = u.chat_id_walrus


def run_with_walrus_equivalent():
    u = Update()
    x = u.chat_id_walrus_equivalent


def run_normal():
    u = Update()
    x = u.chat_id_normal


if __name__ == "__main__":
    N = 80000000
    print(f"Comparing durations for {N} repetitions...")
    # print("Normal execution took:", timeit(run_normal, number=N))
    print(
        "Walrus-equivalent thingy took:", timeit(run_with_walrus_equivalent, number=N)
    )
    print("Walrus execution took:", timeit(run_with_walrus, number=N))
