def parse_ranges(ranges):
    result = []
    for r in ranges.split(','):
        if '-' in r:
            start, end = map(int, r.split('-'))
            result.extend(range(start, end+1))
        else:
            result.append(int(r))
    return result


a = parse_ranges('1,111,5,7-10,55-100')
print(a)