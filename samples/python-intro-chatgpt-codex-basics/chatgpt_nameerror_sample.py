"""Intentional NameError sample for a ChatGPT explanation demo."""


def main() -> None:
    price = 100
    print("価格:", price)

    # わざとつづりをまちがえて、NameError の題材にします。
    print(prcie)  # noqa: F821


if __name__ == "__main__":
    main()
