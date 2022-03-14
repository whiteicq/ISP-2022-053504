example_string = '''Hello, I'm a man and I'm russian, ok?
Shit, you're not a nigger! Now I'm really afraid you.
New string lmao'''


# разделить кол-во слов в тексте на кол-во предложений
def average_words(example=example_string):
    counter_words = 1
    counter_sentences = 1
    for char in example:
        if char == '.' or char == '!' or char == '?':
            counter_sentences += 1
        elif char == ' ':
            counter_words += 1
    return counter_words / counter_sentences


# медианное количество слов в предложении
def mediana_words(example=example_string):
    buff_by_sent = list()
    words_in_sent = 0
    for char in example:
        if char == ' ':
            words_in_sent += 1
        if char == '.' or char == '?' or char == '!':
            buff_by_sent.append(words_in_sent)
            words_in_sent = 0
    buff_by_sent[0] += 1
    buff_by_sent.sort()
    N = len(buff_by_sent)
    if N % 2 == 0:
        return (buff_by_sent[N / 2] + buff_by_sent[N / 2 - 1]) / 2
    else:
        return buff_by_sent[N // 2]


def count_words(example=example_string):
    dict_input = dict()
    example = remove_signs(example)
    words = example.split()
    for word in words:
        dict_input[word] = words.count(word)
    return dict_input


def ngrams(example=example_string, k=10, n=4):
    words = list()
    grams = list()
    pop_gram = dict()
    result = list()
    example = remove_signs(example)
    words = example.split(" ")
    for word in words:
        if len(word) < n:
            continue
        for i in range(0, len(word) - n + 1):
            grams.append(word[i:n+i])
    for gram in grams:
        pop_gram[gram] = grams.count(gram)
    for x in range(k):
        max = list(pop_gram.items())[0]
        for y in pop_gram.items():
            if y > max:
                max = y
        result.append(max)
        del pop_gram[max[0]]
    return result


def remove_signs(example):
    example = example.replace(".", "")
    example = example.replace("!", "")
    example = example.replace("?", "")
    example = example.replace(",", "")
    example = example.replace("...", "")
    example = example.replace("&", "and")
    return example


def main():
    input_string = input("Введите строку: ")
    checker = True
    while checker:
        print("1. Среднее количество слов в предложении")
        print("2. Медианное количество слов в предложении")
        print("3. Сколько раз повторяется каждое слово")
        print("4. top-k самых часто повторяющихся буквенных N-грам")
        print("5. Ввести новую строку")
        print("6. Выход")
        p = input("Выберите желаемую операцию над строкой:\n ")
        if p == "1":
            try:
                print(f"Среднее количество слов в предложении: {average_words(input_string)}")
            except DivisionByZero:
                print("Количество предложений равно нулю")
                exit()
        elif p == "2":
            print(f"Медианное количество слов в предложении: {mediana_words(input_string)}")
        elif p == "3":
            print(f"Частота каждого слова в тексте: {count_words(input_string)}")
        elif p == "4":
            k = input("Введите количество частых n-грам: ")
            n = input("Введите размерность для n-грам: ")
            print(f"{k} {n}-грамы: {ngrams(input_string, int(k), int(n))}")
        elif p == "5":
            input_string = input("Введите строку: ")
        elif p == "6":
            checker = False
        else:
            checker = False
        

if __name__ == "__main__":
    main()