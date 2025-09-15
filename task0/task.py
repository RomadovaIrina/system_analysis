def main(data:str) -> list[list]:
    b:list[int]  = [1,2,3,4]
    c:set[int] = {1,2,3,4}
    d:set[tuple[int, int, float]] = {(1,2,5), (2,3, 6)}
    print("Hello World!")

if __name__ == "__main__":
    main()
    # на вход строка 1,2,5\n 2,3, 6 типа такого вида. Вернуть list из list
    # кр примерно через 2-3 лабы