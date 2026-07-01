def main():
    data = [
        {
            "word": "new",
            "score": 1001
        },
        {
        "word": "little",
        "score": 1000
    },
    {
        "word": "newborn",
        "score": 999
    },
    {
        "word": "first",
        "score": 998
    },
    {
        "word": "old",
        "score": 997
    },
    {
        "word": "poor",
        "score": 996
    },
    {
        "word": "healthy",
        "score": 995
    },
    {
        "word": "tiny",
        "score": 994
    },
    {
        "word": "young",
        "score": 993
    },
    {
        "word": "unborn",
        "score": 992
    },
    {
        "word": "dead",
        "score": 991
    },
    {
        "word": "beautiful",
        "score": 990
    },
    {
        "word": "premature",
        "score": 989
    },
    {
        "word": "born",
        "score": 988
    },
    {
        "word": "big",
        "score": 987
    },
    {
        "word": "second",
        "score": 986
    },
    {
        "word": "normal",
        "score": 985
    },
    {
        "word": "sick",
        "score": 984
    },
    {
        "word": "sweet",
        "score": 983
    },
    {
        "word": "fed",
        "score": 982
    },
    {
        "word": "dear",
        "score": 981
    },
    {
        "word": "pretty",
        "score": 980
    },
    {
        "word": "fat",
        "score": 979
    },
    {
        "word": "happy",
        "score": 978
    },
    {
        "word": "precious",
        "score": 977
    },
    {
        "word": "average",
        "score": 976
    },
    {
        "word": "term",
        "score": 975
    },
    {
        "word": "live",
        "score": 974
    },
    {
        "word": "perfect",
        "score": 973
    },
    {
        "word": "helpless",
        "score": 972
    },
    {
        "word": "mere",
        "score": 971
    },
    {
        "word": "hungry",
        "score": 970
    },
    {
        "word": "illegitimate",
        "score": 969
    },
    {
        "word": "blue",
        "score": 968
    },
    {
        "word": "naked",
        "score": 967
    },
    {
        "word": "innocent",
        "score": 966
    },
    {
        "word": "well",
        "score": 965
    },
    {
        "word": "lovely",
        "score": 964
    },
    {
        "word": "eyed",
        "score": 963
    },
    {
        "word": "male",
        "score": 962
    },
    {
        "word": "older",
        "score": 961
    },
    {
        "word": "brown",
        "score": 960
    },
    {
        "word": "stillborn",
        "score": 959
    },
    {
        "word": "tar",
        "score": 958
    },
    {
        "word": "youngest",
        "score": 957
    },
    {
        "word": "nice",
        "score": 956
    },
    {
        "word": "colicky",
        "score": 955
    },
    {
        "word": "cute",
        "score": 954
    },
    {
        "word": "month",
        "score": 953
    },
    {
        "word": "wonderful",
        "score": 952
    },
    {
        "word": "fussy",
        "score": 951
    },
    {
        "word": "pound",
        "score": 950
    },
    {
        "word": "blind",
        "score": 949
    },
    {
        "word": "quiet",
        "score": 948
    },
    {
        "word": "haired",
        "score": 947
    },
    {
        "word": "unwanted",
        "score": 946
    },
    {
        "word": "breastfed",
        "score": 945
    },
    {
        "word": "sickly",
        "score": 944
    },
    {
        "word": "chubby",
        "score": 943
    },
    {
        "word": "bye",
        "score": 942
    },
    {
        "word": "ugly",
        "score": 941
    },
    {
        "word": "easy",
        "score": 940
    },
    {
        "word": "expected",
        "score": 939
    },
    {
        "word": "cry",
        "score": 938
    },
    {
        "word": "plump",
        "score": 937
    },
    {
        "word": "okay",
        "score": 936
    },
    {
        "word": "deformed",
        "score": 935
    },
    {
        "word": "your",
        "score": 934
    },
    {
        "word": "headed",
        "score": 933
    }
]
            # TODO: Add JSON data here

    # Extract adjectives
    adjectives = []
    for item in data:
        adjectives.append(item["word"])

    # Format the sentence
    target_word = "baby"
    sentence = f"Adjectives for the word {target_word}: " + ", ".join(adjectives)
    print(sentence)
    # Print the list variable, Example: Adjectives for the word "word" are: [list of adjectives]
    print()

if __name__ == "__main__":
    main()