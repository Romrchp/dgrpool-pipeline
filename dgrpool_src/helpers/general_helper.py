import numpy as np

def working_strip(curr_string, separator):
    li = []
    string_left = True
    working_string = curr_string
    while string_left:
        loc = working_string.find(separator)
        string_left = (loc != -1)
        if string_left :
            while (working_string[:loc])[0] == ' ' :
                  working_string = working_string[1:]
                  loc-=1 
            li.append(working_string[:loc])
            working_string = working_string[loc + 1:]
        else:
            while working_string[:loc][0] == ' ' :
                  working_string = working_string[1:]
                  loc-=1
            li.append(working_string)       
    return li


def string_to_str_lists(str_input):
    
    if str_input.find('[') == 0 and str_input.find(']') == len(str_input) - 1:
        process = working_strip(str_input[1:-1], ',')

        for i, value in enumerate(process):
            new_value = ''
            for char in value:
                if char not in ("'", '"'):
                    new_value = new_value + char
            process[i] = new_value
    else:
        #print('something is wrong in', str_input)
        process = str_input   
    return process

def string_to_float_lists(str_input):
    if str_input.find('[') == 0 and str_input.find(']') == len(str_input) - 1:
        process = working_strip(str_input[1:-1], ',')
        for i, value in enumerate(process):
            new_value = ''
            for char in value:
                if char.isdigit() or char == '.':
                    new_value = new_value + char
            if new_value == '' or new_value == '.':
                process[i] = np.nan
            else: 
                #print(new_value,process)
                process[i] = float(new_value)
    else:
        #print('something is wrong in ', str_input)
        process = str_input
    return process

def to_lists(df, column, is_string):
    data = df.copy()
    for j, value in enumerate(data.loc[:,column]):
        if is_string:
            data.loc[j, column] = string_to_str_lists(value)
        else:

            data.loc[j, column] = string_to_float_lists(value)
    return data


def get_index_positions(list_of_elems, element):
    index_pos_list = []
    for i in range(len(list_of_elems)):
        if list_of_elems[i] == element:
            index_pos_list.append(i)
    return index_pos_list

def GetListElements(xllist):
    
    if xllist[0] == '[' and xllist[-1] == ']' and len(xllist):
        phenolist = string_to_str_lists(xllist)
        return phenolist;

    else :
        return('?');