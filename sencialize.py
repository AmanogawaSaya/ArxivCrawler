def valid(string:str):
    return len(string) > 1 and '%' not in string


with open('all.enw', 'r', encoding='utf8') as fp:
    lines = fp.readlines()

num = 0
length = len(lines)
new_lines = []
while num < length:
    if '%K' in lines[num]:
        origin = num
        num += 1
        while '%' not in lines[num]:
            lines[origin] = lines[origin].strip() + ' ' + lines[num]
            num += 1
        new_lines.append(lines[origin])
    else:
        new_lines.append(lines[num])
    num += 1

with open('new_all.enw', 'w', encoding='utf8') as fp:
    for lines in new_lines:
        fp.write(lines)