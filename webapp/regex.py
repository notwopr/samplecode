# Javascript REgex
# for only alphabetic words
singlealpha = "[A-Za-z]"
alpha_multi = f"{singlealpha}+"
begin_singlealpha = "^[A-Za-z]"
single_word = f"{begin_singlealpha}+"
single_space = '\s'
space_plus_word = f'{single_space}{alpha_multi}'
wordorwords_singlespaced = f"{single_word}({space_plus_word})*"
